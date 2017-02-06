# -*- encoding:utf-8 -*-
from django.contrib import admin

from .models import Webents, Profiles, Commits


class WebentsInline(admin.TabularInline):
    model = Webents
    extra = 0


class WebentsAdmin(admin.ModelAdmin):
    list_display = ('name', 'lastPubStatus', 'lastPubDate')
    fieldsets = [
        (None, {'fields': ['name']}),
        ('发版参数', {'fields': ['lastPubStatus']}),
        ('发版时间', {'fields': ['lastPubDate']}),
    ]


class ProfilesAdmin(admin.ModelAdmin):
    list_display = ('P', 'add_date')
    inlines = [WebentsInline]


class CommitsAdmin(admin.ModelAdmin):
    list_display = ('message', 'author', 'commitsFile', 'nvalue', 'commit_date')


admin.site.register(Commits,CommitsAdmin)

admin.site.register(Profiles, ProfilesAdmin)

admin.site.register(Webents, WebentsAdmin)
