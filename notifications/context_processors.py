from django.core.cache import cache

from notifications.models import Notification

def notification_processor(request):

    if cache.get('shown_notification_available') != False:

        # Either the shown_notification_available cache key is True
        # or is not set. Anyway, checking if there is a cache
        # item for the shown notification.

        notification = cache.get('shown_notification')

        if not notification:

            # If there is no such cache item, checking if
            # it's in the database.

            try:
                notification = Notification.objects.get(show_this_message=True)
            except (Notification.DoesNotExist, Notification.MultipleObjectsReturned):
                notification = None
                # If there is no shown notification,
                # it is not necessary to check it in the DB next time.
                # In this case it is not fetched until notifications
                # are edited or the cache key expires.
                cache.set('shown_notification_available', False, 86400)
            else:
                # Add the notification to the cache (for 24 hours)
                cache.set('shown_notification', notification, 86400)

        if notification:
            try:
                if request.COOKIES["closed_notification_timestamp"] == str(notification.shown_since_as_timestamp):
                    hide_top_notification = True
                else:
                    hide_top_notification = False
            except KeyError:
                hide_top_notification = False

            return {'top_notification': notification, 'hide_top_notification': hide_top_notification}

    return {'top_notification': None}
