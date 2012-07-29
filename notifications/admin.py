# -*- coding: utf-8 -*-

from django.contrib import admin

from django.utils.translation import ugettext
from django.utils.translation import ugettext_lazy as _
from django.utils import formats

from notifications.models import Notification

class NotificationAdmin(admin.ModelAdmin):
    search_fields = ['text']
    list_display = ('text', 'show_this_message')
    exclude = ('shown_since',)
    readonly_fields = ('display_shown_since_value',)

    def display_shown_since_value(self, obj):
        if obj.shown_since:
            return formats.date_format(obj.shown_since, "DATETIME_FORMAT")
        else:
            return ugettext(u"This message is not shown")

    display_shown_since_value.short_description = _(u"Shown since")

admin.site.register(Notification, NotificationAdmin)
