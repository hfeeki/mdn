from datetime import datetime
from time import strftime
from os import unlink, makedirs
from os.path import basename, dirname, isfile, isdir
from shutil import rmtree
import re

import logging

import zipfile
import tarfile

from django.conf import settings

from django.utils.encoding import smart_unicode, smart_str

from devmo.urlresolvers import reverse

from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import Q
from django.db.models.fields.files import FieldFile, ImageFieldFile
from django.utils.translation import ugettext_lazy as _
from django.template.defaultfilters import slugify
from django.template.loader import render_to_string
from django.template.defaultfilters import slugify

from django.contrib.sites.models import Site
from django.contrib.auth.models import User

import tagging
import tagging.fields
import tagging.models

from tagging.utils import parse_tag_input
from tagging.fields import TagField
from tagging.models import Tag

from . import scale_image


try:
    from PIL import Image
except ImportError:
    import Image


THUMBNAIL_MAXW = getattr(settings, 'DEMO_THUMBNAIL_MAX_WIDTH', 133)
THUMBNAIL_MAXH = getattr(settings, 'DEMO_THUMBNAIL_MAX_HEIGHT', 100)

RESIZE_METHOD = getattr(settings, 'RESIZE_METHOD', Image.ANTIALIAS)

# HACK: For easier L10N, define tag descriptions in code instead of as a DB model
TAG_DESCRIPTIONS = getattr(settings, 'TAG_DESCRIPTIONS', dict( (x['tag_name'], x) for x in (
    { "tag_name": "audio", "title": _("Audio"), 
        "description": _("These demos make noise") },
    { "tag_name": "canvas", "title": _("Canvas"),
        "description": _("These demos make pretty pictures") },
    { "tag_name": "css3", "title": _("CSS3"), 
        "description": _("Fancy styling happens in these demos") },
    { "tag_name": "device", "title": _("Device"), 
        "description": _("Demos here use device thingies") },
    { "tag_name": "file", "title": _("File"), 
        "description": _("Files are manipulated here") },
    { "tag_name": "game", "title": _("Game"), 
        "description": _("Games are demos too!") },
    { "tag_name": "geolocation", "title": _("Geolocation"), 
        "description": _("These demos know where you've been") },
    { "tag_name": "html5", "title": _("HTML5"), 
        "description": _("HTML5 is the future!") },
    { "tag_name": "indexeddb", "title": _("IndexedDB"), 
        "description": _("Data gets indexed happily") },
    { "tag_name": "mobile", "title": _("Mobile"), 
        "description": _("Demos on the march!") },
    { "tag_name": "svg", "title": _("SVG"), 
        "description": _("Drawrings in demos vectorly") },
    { "tag_name": "video", "title": _("Video"), 
        "description": _("Internet killed the video star") },
    { "tag_name": "webgl", "title": _("WebGL"), 
        "description": _("The browser is throwing things at your face in 3D") },
    { "tag_name": "websockets", "title": _("WebSockets"), 
        "description": _("Stick these in your socket and network it") },
    { "tag_name": "forms", "title": _("Forms"), 
        "description": _("Filling out fields just got better") },
    { "tag_name": "mathml", "title": _("MathML"), 
        "description": _("Pretty math stuff") },
    { "tag_name": "smil", "title": _("SMIL"), 
        "description": _("SMILe, you're on candid web demos") },
    { "tag_name": "localstorage", "title": _("Local Storage"), 
        "description": _("Storing things locally") },
    { "tag_name": "offlinesupport", "title": _("Offline Support"), 
        "description": _("Going offline for awhile") },
    { "tag_name": "webworkers", "title": _("Web Workers"), 
        "description": _("Workers of the web unite!") },
)))

# HACK: For easier L10N, define license in code instead of as a DB model
DEMO_LICENSES = getattr(settings, "DEMO_LICENSES", (
    ("cc-by-sa", _("CC-BY-SA Creative Commons Attribution-ShareAlike 3.0 [DEFAULT]")),
    ("cc-by", _("CC-BY Creative Commons Attribution 3.0")),
    ("cc-by-no", _("CC-BY-NO Creative Commons Attribution-NonCommercial 3.0")),
    ("cc-by-no-sa", _("CC-BY-NO-SA Createive Commons Attribution-NonCommercial-ShareAlike 3.0")),
    ("mpl", _("MPL/GPL/LGPL")),
    ("gpl", _("GPL")),
    ("lgpl", _("LGPL")),
    ("bsd", _("BSD")),
    ("apache", _("Apache")),
    ("agpl", _("AGPL")),
    ("cc-by-nd", _("CC-BY-ND Creative Commons Attribution-NonCommercial-NoDervis")),
    ("cc-by-no-nd", _("CC-BY-NO-ND Creative Commons Attribution-NoDervis")),
    ("publicdomain", _("Public Domain")),
    ("other", _("Other (N/A)")),
))


class ConstrainedTagField(tagging.fields.TagField):
    """Tag field constrained to described tags"""

    def __init__(self, *args, **kwargs):
        if 'max_tags' not in kwargs:
            self.max_tags = 5
        else:
            self.max_tags = kwargs['max_tags']
            del kwargs['max_tags']
        super(ConstrainedTagField, self).__init__(*args, **kwargs)

    def validate(self, value, instance):

        if not isinstance(value, (list, tuple)):
            value = parse_tag_input(value)

        if len(value) > self.max_tags:
            raise ValidationError(_('Maximum of %s tags allowed') % 
                    (self.max_tags))

        for tag_name in value:
            if not tag_name in TAG_DESCRIPTIONS:
                raise ValidationError(
                    _('Tag "%s" is not in the set of described tags') % 
                        (tag_name))

    def formfield(self, **kwargs):
        from .forms import ConstrainedTagFormField
        defaults = {'form_class': ConstrainedTagFormField}
        defaults.update(kwargs)
        return super(ConstrainedTagField, self).formfield(**defaults)


class OverwritingFieldFile(FieldFile):
    """The built-in FieldFile alters the filename when saving, if a file with
    that name already exists. This subclass deletes an existing file first so
    that an upload will replace it."""
    def save(self, name, content, save=True):
        name = self.field.generate_filename(self.instance, name)
        self.storage.delete(name)
        super(OverwritingFieldFile, self).save(name,content,save)
    

class OverwritingFileField(models.FileField):
    """This field causes an uploaded file to replace an existing one on disk."""
    attr_class = OverwritingFieldFile


class OverwritingImageFieldFile(ImageFieldFile):
    """The built-in FieldFile alters the filename when saving, if a file with
    that name already exists. This subclass deletes an existing file first so
    that an upload will replace it."""
    def save(self, name, content, save=True):
        name = self.field.generate_filename(self.instance, name)
        self.storage.delete(name)
        super(OverwritingImageFieldFile, self).save(name,content,save)
    

class OverwritingImageField(models.ImageField):
    """This field causes an uploaded file to replace an existing one on disk."""
    attr_class = OverwritingImageFieldFile


def get_root_for_submission(instance):
    c_name = instance.creator.username
    return 'uploads/demos/%(h1)s/%(h2)s/%(username)s/%(slug)s' % dict(
         h1=c_name[0], h2=c_name[1], username=c_name, slug=instance.slug,)

def mk_upload_to(field_fn):
    def upload_to(instance, filename):
        return '%(base)s/%(field_fn)s' % dict( 
            base=get_root_for_submission(instance), field_fn=field_fn)
    return upload_to


class SubmissionManager(models.Manager):
    """Manager for Submission objects"""

    # See: http://www.julienphalip.com/blog/2008/08/16/adding-search-django-site-snap/
    def _normalize_query(self, query_string,
                        findterms=re.compile(r'"([^"]+)"|(\S+)').findall,
                        normspace=re.compile(r'\s{2,}').sub):
        ''' Splits the query string in invidual keywords, getting rid of unecessary spaces
            and grouping quoted words together.
            Example:
            
            >>> normalize_query('  some random  words "with   quotes  " and   spaces')
            ['some', 'random', 'words', 'with quotes', 'and', 'spaces']
        
        '''
        return [normspace(' ', (t[0] or t[1]).strip()) for t in findterms(query_string)] 

    # See: http://www.julienphalip.com/blog/2008/08/16/adding-search-django-site-snap/
    def _get_query(self, query_string, search_fields):
        ''' Returns a query, that is a combination of Q objects. That combination
            aims to search keywords within a model by testing the given search fields.
        
        '''
        query = None # Query to search for every search term        
        terms = self._normalize_query(query_string)
        for term in terms:
            or_query = None # Query to search for a given term in each field
            for field_name in search_fields:
                q = Q(**{"%s__icontains" % field_name: term})
                if or_query is None:
                    or_query = q
                else:
                    or_query = or_query | q
            if query is None:
                query = or_query
            else:
                query = query & or_query
        return query

    def search(self, query_string):
        """Quick and dirty keyword search on submissions"""
        # TODO: Someday, replace this with something like Sphinx or another real search engine
        query = self._get_query(query_string.strip(), ['title', 'summary', 'description',])
        return self.filter(query).order_by('-modified')
        

class Submission(models.Model):
    """Representation of a demo submission"""
    objects = SubmissionManager()

    title = models.CharField(
            _("what is your demo's name?"), 
            max_length=255, blank=False, unique=True)
    slug = models.SlugField(_("slug"), 
            blank=False, unique=True)
    summary = models.CharField(
            _("describe your demo in one line"),
            max_length=255, blank=False)
    description = models.TextField(
            _("describe your demo in more detail (optional)"), 
            blank=True)

    featured = models.BooleanField()
    hidden = models.BooleanField()

    tags = ConstrainedTagField(
            _('select up to 5 tags that describe your demo'),
            max_tags=5)

    screenshot_1 = OverwritingImageField(
            _('Screenshot #1'),
            upload_to=mk_upload_to('screenshot_1.png'), blank=False)
    screenshot_2 = OverwritingImageField(
            _('Screenshot #2'),
            upload_to=mk_upload_to('screenshot_2.png'), blank=True)
    screenshot_3 = OverwritingImageField(
            _('Screenshot #3'),
            upload_to=mk_upload_to('screenshot_3.png'), blank=True)
    screenshot_4 = OverwritingImageField(
            _('Screenshot #4'),
            upload_to=mk_upload_to('screenshot_4.png'), blank=True)
    screenshot_5 = OverwritingImageField(
            _('Screenshot #5'),
            upload_to=mk_upload_to('screenshot_5.png'), blank=True)

    video_url = models.URLField(
            _("have a video of your demo in action? (optional)"),
            verify_exists=False, blank=True, null=True)

    demo_package = OverwritingFileField(
            _('select a ZIP file containing your demo'),
            upload_to=mk_upload_to('demo_package.zip'),
            blank=False)
    source_code_url = models.URLField(
            _("is your source code hosted online? (optional)"),
            verify_exists=False, blank=True, null=True)
    license_name = models.CharField(
            _("select a license for your source code"),
            max_length=64, blank=False, choices=DEMO_LICENSES)

    creator = models.ForeignKey(User, blank=False, null=True)
    
    created = models.DateTimeField( _('date created'), 
            auto_now_add=True, blank=False)
    modified = models.DateTimeField( _('date last modified'), 
            auto_now=True, blank=False)

    def __unicode__(self):
        return 'Submission "%(title)s"' % dict(
            title=self.title )

    def get_absolute_url(self):
        return reverse('demos.views.detail', kwargs={'slug':self.slug})

    def save(self):
        """Save the submission, updating slug and screenshot thumbnails"""
        self.slug = slugify(self.title)
        super(Submission,self).save()
        self.update_thumbnails()

    def delete(self,using=None):
        root = '%s/%s' % (settings.MEDIA_ROOT, get_root_for_submission(self))
        if isdir(root): rmtree(root)
        super(Submission,self).delete(using)

    def clean(self):
        if self.demo_package:
            Submission.validate_demo_zipfile(self.demo_package)

    @classmethod
    def allows_listing_hidden_by(cls, user):
        if user.is_staff or user.is_superuser:
            return True
        return False

    def allows_hiding_by(self, user):
        if user.is_staff or user.is_superuser:
            return True
        return False

    def allows_viewing_by(self, user):
        if user.is_staff or user.is_superuser:
            return True
        if user == self.creator:
            return True
        if not self.hidden:
            return True
        return False

    def allows_editing_by(self, user):
        if user.is_staff or user.is_superuser:
            return True
        if user == self.creator:
            return True
        return False

    def allows_deletion_by(self, user):
        if user.is_staff or user.is_superuser:
            return True
        if user == self.creator:
            return True
        return False

    def update_thumbnails(self):
        """Update thumbnails to accompany full-size screenshots"""
        for idx in range(1, 6):

            name = 'screenshot_%s' % idx
            field = getattr(self, name)
            if not field: continue

            try:
                # TODO: Only update thumbnail if source image has changed / is newer
                thumb_name = field.name.replace('screenshot','screenshot_thumb')
                scaled_file = scale_image(field.file, (THUMBNAIL_MAXW, THUMBNAIL_MAXH))
                if scaled_file:
                    field.storage.delete(thumb_name)
                    field.storage.save(thumb_name, scaled_file)
            except:
                # TODO: Had some exceptions here related to scaling that
                # nonetheless resulted in an updated thumbnail. Investigate further.
                pass

    @classmethod
    def get_valid_demo_zipfile_entries(cls, zf):
        """Filter a zip file's entries for only accepted entries"""
        # TODO: Should we restrict to a certain set of {css,js,html,wot} extensions?
        return [ x for x in zf.infolist() if 
            not (x.filename.startswith('/') or '/..' in x.filename) and
            not (basename(x.filename).startswith('.')) and
            x.file_size > 0 ]

    @classmethod
    def validate_demo_zipfile(cls, file):
        """Ensure a given file is a valid ZIP file without disallowed file
        entries and with an HTML index."""
        try:
            zf = zipfile.ZipFile(file)
        except:
            raise ValidationError(_('ZIP file contains no acceptable files'))

        if zf.testzip():
            raise ValidationError(_('ZIP file corrupted'))
        
        valid_entries = Submission.get_valid_demo_zipfile_entries(zf) 
        if len(valid_entries) == 0:
            raise ValidationError(_('ZIP file contains no acceptable files'))

        index_found = False
        for zi in valid_entries:
            name = zi.filename
            # HACK: We're accepting {index,demo}.html as the root index and
            # normalizing on unpack
            if 'index.html' == name or 'demo.html' == name:
                index_found = True
        
        if not index_found:
            raise ValidationError(_('HTML index not found in ZIP'))

    def process_demo_package(self):
        """Unpack the demo zipfile into the appropriate directory, filtering
        out any invalid file entries and normalizing demo.html to index.html if
        present."""

        # Derive a directory name from the zip filename, clean up any existing
        # directory before unpacking.
        new_root_dir = self.demo_package.path.replace('.zip','')
        if isdir(new_root_dir):
            rmtree(new_root_dir)

        # Load up the zip file and extract the valid entries
        zf = zipfile.ZipFile(self.demo_package.file)
        valid_entries = Submission.get_valid_demo_zipfile_entries(zf) 

        for zi in valid_entries:

            # HACK: Normalize demo.html to index.html
            if zi.filename == 'demo.html':
                zi.filename = 'index.html'

            # Relocate all files from detected root dir to a directory named
            # for the zip file in storage
            out_fn = '%s/%s' % ( new_root_dir, zi.filename )
            out_dir = dirname(out_fn)

            # Create parent directories where necessary.
            if not isdir(out_dir):
                makedirs(out_dir, 0775)

            # Extract the file from the zip into the desired location.
            open(out_fn, 'w').write(zf.read(zi))

