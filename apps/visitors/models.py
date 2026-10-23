from django.db import models
from django.conf import settings
from apps.residents.models import ResidentProfile


class VisitorLog(models.Model):
    class Status(models.TextChoices):
        CHECKED_IN = 'CHECKED_IN', 'Checked In (Active)'
        CHECKED_OUT = 'CHECKED_OUT', 'Checked Out'
        OVERSTAYED = 'OVERSTAYED', 'Overstayed'

    visitor_name = models.CharField(max_length=150)
    visitor_phone = models.CharField(max_length=20)
    resident = models.ForeignKey(ResidentProfile, on_delete=models.CASCADE, related_name='visitors')
    relationship = models.CharField(max_length=50, blank=True, help_text="e.g. Parent, Sibling, Friend")
    destination = models.CharField(
        max_length=150,
        help_text="Building, Floor and Room, e.g. Building A | Floor 2nd | Room 201"
    )
    purpose = models.CharField(max_length=200, help_text="Reason for visit")
    check_in_time = models.DateTimeField(auto_now_add=True)
    check_out_time = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.CHECKED_IN)
    gate_pass_no = models.CharField(max_length=50, blank=True)
    recorded_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name='recorded_visitors')

    class Meta:
        ordering = ['-check_in_time']

    def __str__(self):
        return f"{self.visitor_name} visiting {self.resident.student_id} ({self.destination})"
