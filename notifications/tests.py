import time

from django.test import TestCase
from django.test.client import Client

from django.core.cache import cache

from notifications.models import Notification

class NotificationTest(TestCase):
    def test_creating_notifications(self):
        """
        Test creating notifications. Also checks the notifications caching.
        """
        cache.delete("shown_notification")
        cache.delete("shown_notification_available")

        notification_1 = Notification.objects.create(text="Test notification")
        self.assertEqual(Notification.objects.all().count(), 1)

        self.assertEqual(cache.get("shown_notification_available"), False)

        c = Client()

        response = c.get('/')
        self.assertEqual(response.status_code, 200)

        self.assertIsNone(cache.get("shown_notification"))

        notification_1.show_this_message = True
        notification_1.save()

        self.assertEqual(cache.get("shown_notification_available"), True)

        self.assertIsNone(cache.get("shown_notification"))

        response = c.get('/')
        self.assertEqual(response.status_code, 200)

        self.assertEqual(cache.get("shown_notification"), notification_1)

        notification_2 = Notification.objects.create(text="Another test notification")

        response = c.get('/')
        self.assertEqual(response.status_code, 200)

        self.assertEqual(cache.get("shown_notification_available"), True)

        self.assertEqual(cache.get("shown_notification"), notification_1)

        notification_3 = Notification.objects.create(text="Shown notification", show_this_message=True)

        # Update notification_1
        notification_1 = Notification.objects.get(id=notification_1.id)

        self.assertIsNone(notification_1.shown_since_as_timestamp)

        self.assertIsNotNone(notification_3.shown_since_as_timestamp)

        self.assertEqual(cache.get("shown_notification_available"), True)

        self.assertIsNone(cache.get("shown_notification"))

        response = c.get('/')
        self.assertEqual(response.status_code, 200)

        self.assertEqual(cache.get("shown_notification"), notification_3)

        cache.delete("shown_notification")
        cache.delete("shown_notification_available")

        response = c.get('/')
        self.assertEqual(response.status_code, 200)

        self.assertIsNone(cache.get("shown_notification_available"))
        self.assertEqual(cache.get("shown_notification"), notification_3)

        notification_3.show_this_message = False
        notification_3.save()

        self.assertEqual(Notification.objects.filter(show_this_message=True).count(), 0)

        cache.delete("shown_notification")
        cache.delete("shown_notification_available")

        response = c.get('/')
        self.assertEqual(response.status_code, 200)

        self.assertEqual(cache.get("shown_notification_available"), False)
        self.assertIsNone(cache.get("shown_notification"))

    def test_updating_existing_notification(self):
        """
        Tests that shown_since does not change until
        show_this_message is changed to False.
        """
        notification = Notification.objects.create(text="Test notification")
        self.assertIsNone(notification.shown_since_as_timestamp)

        notification.show_this_message = True
        notification.save()

        timestamp_after_first_edit = notification.shown_since_as_timestamp

        self.assertIsNotNone(timestamp_after_first_edit)

        notification = Notification.objects.get(id=notification.id)
        notification.save()

        notification = Notification.objects.get(id=notification.id)
        self.assertEqual(timestamp_after_first_edit, notification.shown_since_as_timestamp)

        notification = Notification.objects.get(id=notification.id)
        notification.show_this_message = False
        notification.save()

        time.sleep(1)

        notification = Notification.objects.get(id=notification.id)
        notification.show_this_message = True
        notification.save()

        notification = Notification.objects.get(id=notification.id)
        self.assertNotEqual(timestamp_after_first_edit, notification.shown_since_as_timestamp)

    def tearDown(self):
        Notification.objects.all().delete()
