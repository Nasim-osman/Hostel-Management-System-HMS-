from django.db import models
from django.conf import settings


class InAppNotification(models.Model):
    class NotificationType(models.TextChoices):
        FEE_DUE = 'FEE_DUE', 'Fee Due Reminder'
        APPLICATION = 'APPLICATION', 'Application Status'
        COMPLAINT = 'COMPLAINT', 'Ticket Update'
        OUTPASS = 'OUTPASS', 'Outpass Update'
        NOTICE = 'NOTICE', 'New Notice'
        CLEARANCE = 'CLEARANCE', 'Clearance Notice'
        SYSTEM = 'SYSTEM', 'System Alert'

    recipient = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='notifications')
    title = models.CharField(max_length=200)
    message = models.TextField()
    notification_type = models.CharField(max_length=20, choices=NotificationType.choices, default=NotificationType.SYSTEM)
    link = models.CharField(max_length=255, blank=True)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Notification for {self.recipient.username}: {self.title}"


def notify_user(recipient, title, message, notification_type=InAppNotification.NotificationType.SYSTEM, link=""):
    """
    Creates an in-app notification for a user.
    """
    return InAppNotification.objects.create(
        recipient=recipient,
        title=title,
        message=message,
        notification_type=notification_type,
        link=link
    )
