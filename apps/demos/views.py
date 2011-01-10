import jingo

from django.conf import settings

from django.http import HttpResponseRedirect, HttpResponse, HttpResponseForbidden

from django.shortcuts import get_object_or_404, render_to_response
from django.core.urlresolvers import reverse
from django.template.defaultfilters import slugify

from django.contrib.auth.views import AuthenticationForm 

from django.utils.translation import ugettext_lazy as _

from django.views.generic.list_detail import object_list

from devmo import (SECTION_USAGE, SECTION_ADDONS, SECTION_APPS, SECTION_MOBILE,
                   SECTION_WEB)
from feeder.models import Bundle, Feed

from django.contrib.auth.models import User
from devmo.models import UserProfile

from tagging.models import Tag, TaggedItem
from tagging.utils import LINEAR, LOGARITHMIC

from demos.models import Submission
from demos.forms import SubmissionNewForm, SubmissionEditForm

from contentflagging.models import ContentFlag
from contentflagging.forms import ContentFlagForm
from actioncounters.models import Action

from utils import JingoTemplateLoader
template_loader = JingoTemplateLoader()


def home(request):
    """Home page."""

    featured_submissions = Submission.objects.order_by('-modified').filter(featured=True)
    if not Submission.allows_listing_hidden_by(request.user):
        featured_submissions = featured_submissions.exclude(hidden=True)

    submissions = Submission.objects.order_by('-modified')
    if not Submission.allows_listing_hidden_by(request.user):
        submissions = submissions.exclude(hidden=True)

    return jingo.render(request, 'demos/home.html', {
        'featured_submission_list': featured_submissions.all()[:15],
        'submission_list': submissions.all()[:15] 
    })

def detail(request, slug):
    """Detail page for a submission"""
    submission = get_object_or_404(Submission, slug=slug)
    if not submission.allows_viewing_by(request.user):
        return HttpResponseForbidden(_('access denied'))
    
    return jingo.render(request, 'demos/detail.html', {
        'submission': submission })

def search(request):
    """Search against submission title, summary, and description"""
    query_string = request.GET.get('q', '')
    return object_list(request, Submission.objects.search(query_string),
        paginate_by=25, allow_empty=True,
        template_loader=template_loader,
        template_object_name='submission',
        template_name='demos/listing.html') 

def profile_detail(request, username):
    user = get_object_or_404(User, username=username)
    profile = UserProfile.objects.get(user=user)

    try:
        # HACK: This seems like a dirty violation of the DekiWiki auth package
        from dekicompat.backends import DekiUserBackend
        backend = DekiUserBackend()
        deki_user = backend.get_deki_user(profile.deki_user_id)
    except:
        deki_user = None

    qs = Submission.objects.filter(creator=user)
    return object_list(request, qs,
        extra_context=dict( 
            profile_user=user, 
            profile_deki_user=deki_user
        ),
        paginate_by=25, allow_empty=True,
        template_loader=template_loader,
        template_object_name='submission',
        template_name='demos/listing.html') 

def like(request, slug):
    submission = get_object_or_404(Submission, slug=slug)
    if request.method == "POST":
        Action.objects['like'].increment(request=request, object=submission)
    return HttpResponseRedirect(reverse(
        'demos.views.detail', args=(submission.slug,)))

def flag(request, slug):
    submission = get_object_or_404(Submission, slug=slug)

    if request.method != "POST":
        form = ContentFlagForm()
    else:
        form = ContentFlagForm(request.POST, request.FILES)
        if form.is_valid():
            flag, created = ContentFlag.objects.flag(request=request, object=submission,
                    flag_type=form.cleaned_data['flag_type'],
                    explanation=form.cleaned_data['explanation'])
            return HttpResponseRedirect(reverse(
                'demos.views.detail', args=(submission.slug,)))

    return jingo.render(request, 'demos/flag.html', {
        'form': form, 'submission': submission })

def download(request, slug):
    """Demo download with action counting"""
    submission = get_object_or_404(Submission, slug=slug)
    Action.objects['download'].increment(request=request, object=submission)
    return HttpResponseRedirect(submission.demo_package.url)

def launch(request, slug):
    """Demo launch view with action counting"""
    submission = get_object_or_404(Submission, slug=slug)
    Action.objects['launch'].increment(request=request, object=submission)
    return jingo.render(request, 'demos/launch.html', {
        'submission': submission })

def submit(request):
    """Accept submission of a demo"""
    if not request.user.is_authenticated():
        return jingo.render(request, 'demos/submit_noauth.html', {})

    if request.method != "POST":
        form = SubmissionNewForm()
    else:
        form = SubmissionNewForm(request.POST, request.FILES)
        if form.is_valid():
            
            new_sub = form.save(commit=False)
            if request.user.is_authenticated():
                new_sub.creator = request.user
            new_sub.save()
            
            # TODO: Process in a cronjob?
            new_sub.process_demo_package()

            return HttpResponseRedirect(reverse(
                    'demos.views.detail', args=(new_sub.slug,)))

    return jingo.render(request, 'demos/submit.html', {'form': form})

def edit(request, slug):
    submission = get_object_or_404(Submission, slug=slug)
    if not submission.allows_editing_by(request.user):
        return HttpResponseForbidden(_('access denied'))

    if request.method != "POST":
        form = SubmissionEditForm(instance=submission)
    else:
        form = SubmissionEditForm(request.POST, request.FILES, instance=submission)
        if form.is_valid():

            sub = form.save(commit=False)
            sub.save()
            
            # TODO: Process in a cronjob?
            sub.process_demo_package()
            
            return HttpResponseRedirect(reverse(
                    'demos.views.detail', args=(sub.slug,)))

    return jingo.render(request, 'demos/submit.html', { 
        'form': form, 'submission': submission, 'edit': True })

def delete(request, slug):
    submission = get_object_or_404(Submission, slug=slug)
    if not submission.allows_deletion_by(request.user):
        return HttpResponseForbidden(_('access denied'))

    if request.method == "POST":
        submission.delete()

    return HttpResponseRedirect(reverse('demos.views.home'))

def hideshow(request, slug, hide=True):
    submission = get_object_or_404(Submission, slug=slug)
    if not submission.allows_hiding_by(request.user):
        return HttpResponseForbidden(_('access denied'))

    if request.method == "POST":
        submission.hidden = hide
        submission.save()

    return HttpResponseRedirect(reverse(
            'demos.views.detail', args=(submission.slug,)))
