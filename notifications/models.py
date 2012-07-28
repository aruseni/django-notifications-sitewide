# -*- coding: utf-8 -*-

import datetime
import time

from django.db import models
from django.db.models.signals import post_save, post_delete
from django.core.cache import cache
from django.utils.translation import ugettext
from django.utils.translation import ugettext_lazy as _
from django.utils.timezone import utc

class Notification(models.Model):
    text = models.CharField(_(u"Notification text"), max_length=255)
    show_this_message = models.BooleanField(_(u"Show on the website"), db_index=True)
    shown_since = models.DateTimeField(_(u"Shown since"), blank=True, null=True)

    @property
    def shown_since_as_timestamp(self):
        if self.shown_since:
            return int(time.mktime(self.shown_since.timetuple()))
        return

    def save(self, *args, **kwargs):
        # Only one message is displayed at a time
        if self.show_this_message == True:
            Notification.objects.all().update(show_this_message=False, shown_since=None)
            # No need to update shown_since in case it is already set
            if not self.shown_since:
                self.shown_since = datetime.datetime.utcnow().replace(tzinfo=utc)
        else:
            self.shown_since = None
        super(Notification, self).save(*args, **kwargs) # Call the "real" save() method.

    def __unicode__(self):
        return ugettext(u"Notification #%(notification_id)s") % {'notification_id': self.id}

    class Meta:
        verbose_name = _(u"Notification")
        verbose_name_plural = _(u"Notifications")

        ordering = ['-show_this_message']

def update_shown_notification_available_cache_key(sender, **kwargs):
    """
    This signal checks if there is a shown notification,
    and stores the result of the check (as boolean) in the
    shown_notification_available cache key.
    It also deletes the shown_notification cache key.
    """
    cache.set('shown_notification_available', Notification.objects.filter(show_this_message=True).exists(), 86400)
    cache.delete('shown_notification')

post_save.connect(update_shown_notification_available_cache_key, sender=Notification)
post_delete.connect(update_shown_notification_available_cache_key, sender=Notification)
