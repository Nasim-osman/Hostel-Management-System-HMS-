from django.db import models
from django.conf import settings


class Notice(models.Model):
    class Category(models.TextChoices):
        GENERAL = 'GENERAL', 'General Announcement'
        MESS = 'MESS', 'Mess & Dining'
        MAINTENANCE = 'MAINTENANCE', 'Maintenance & Repairs'
        FEES = 'FEES', 'Fees & Accounts'
        EMERGENCY = 'EMERGENCY', 'Urgent / Emergency'
        EVENTS = 'EVENTS', 'Hostel Events'

    class TargetAudience(models.TextChoices):
        ALL = 'ALL', 'All Hostel Members'
        RESIDENTS_ONLY = 'RESIDENTS', 'Residents Only'
        STAFF_ONLY = 'STAFF', 'Staff Only'

    title = models.CharField(max_length=200)
    category = models.CharField(max_length=20, choices=Category.choices, default=Category.GENERAL)
    target_audience = models.CharField(max_length=20, choices=TargetAudience.choices, default=TargetAudience.ALL)
    content = models.TextField()
    is_published = models.BooleanField(default=True)
    publish_date = models.DateTimeField(auto_now_add=True)
    expiry_date = models.DateField(null=True, blank=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name='published_notices')

    class Meta:
        ordering = ['-publish_date']

    def __str__(self):
        return f"{self.title} ({self.get_category_display()})"
