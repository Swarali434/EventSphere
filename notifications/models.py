from django.db import models
from django.contrib.auth.models import User
from events.models import Event, Booking


class Notification(models.Model):
    NOTIFICATION_TYPES = [
        ('booking_confirmed', 'Booking Confirmed'),
        ('booking_cancelled', 'Booking Cancelled'),
        ('event_reminder', 'Event Reminder'),
        ('event_approved', 'Event Approved'),
        ('event_rejected', 'Event Rejected'),
        ('new_review', 'New Review'),
        ('system', 'System Notification'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    title = models.CharField(max_length=200)
    message = models.TextField()
    notification_type = models.CharField(max_length=20, choices=NOTIFICATION_TYPES)
    event = models.ForeignKey(Event, on_delete=models.CASCADE, null=True, blank=True)
    booking = models.ForeignKey(Booking, on_delete=models.CASCADE, null=True, blank=True)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.title} - {self.user.username}"


class NotificationPreference(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='notification_preferences')
    email_notifications = models.BooleanField(default=True)
    booking_confirmations = models.BooleanField(default=True)
    event_reminders = models.BooleanField(default=True)
    event_updates = models.BooleanField(default=True)
    marketing_emails = models.BooleanField(default=False)

    def __str__(self):
        return f"Notification preferences for {self.user.username}"
