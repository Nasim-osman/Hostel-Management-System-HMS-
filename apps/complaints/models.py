from django.db import models
from django.conf import settings
from apps.residents.models import ResidentProfile
from apps.rooms.models import Room


class Complaint(models.Model):
    class Category(models.TextChoices):
        PLUMBING = 'PLUMBING', 'Plumbing & Water'
        ELECTRICAL = 'ELECTRICAL', 'Electrical & Lighting'
        WIFI = 'WIFI', 'Internet / Wifi'
        CARPENTRY = 'CARPENTRY', 'Carpentry & Furniture'
        CLEANING = 'CLEANING', 'Housekeeping & Cleanliness'
        LAUNDRY = 'LAUNDRY', 'Laundry Service'
        MESS = 'MESS', 'Mess / Food Issue'
        OTHER = 'OTHER', 'Other Maintenance'

    class Priority(models.TextChoices):
        LOW = 'LOW', 'Low'
        MEDIUM = 'MEDIUM', 'Medium'
        HIGH = 'HIGH', 'High'
        URGENT = 'URGENT', 'Urgent'

    class Status(models.TextChoices):
        SUBMITTED = 'SUBMITTED', 'Submitted'
        ASSIGNED = 'ASSIGNED', 'Assigned'
        IN_PROGRESS = 'IN_PROGRESS', 'In Progress'
        RESOLVED = 'RESOLVED', 'Resolved'
        CLOSED = 'CLOSED', 'Closed'

    ticket_number = models.CharField(max_length=50, unique=True, help_text="e.g. HMS-TICK-2026-0001")
    resident = models.ForeignKey(ResidentProfile, on_delete=models.CASCADE, related_name='complaints')
    room = models.ForeignKey(Room, on_delete=models.SET_NULL, null=True, blank=True, related_name='complaints')
    title = models.CharField(max_length=200, help_text="Brief summary of the issue")
    category = models.CharField(max_length=20, choices=Category.choices, default=Category.PLUMBING)
    priority = models.CharField(max_length=20, choices=Priority.choices, default=Priority.MEDIUM)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.SUBMITTED)
    description = models.TextField(help_text="Detailed description of the complaint")
    assigned_to = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='assigned_complaints',
        help_text="Maintenance staff assigned"
    )
    resolution_notes = models.TextField(blank=True)
    resident_feedback = models.PositiveSmallIntegerField(null=True, blank=True, help_text="Rating from 1 to 5")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    resolved_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.ticket_number}: {self.title} ({self.get_status_display()})"
