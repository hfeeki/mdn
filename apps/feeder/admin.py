from django.contrib import admin

from .models import Feed, Entry


class FeedAdmin(admin.ModelAdmin):
    pass
admin.site.register(Feed, FeedAdmin)


class EntryAdmin(admin.ModelAdmin):
    pass
admin.site.register(Entry, EntryAdmin)
