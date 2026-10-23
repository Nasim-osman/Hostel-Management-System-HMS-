from django.db import models
from django.conf import settings
from apps.residents.models import ResidentProfile


class AttendanceRecord(models.Model):
    class Status(models.TextChoices):
        PRESENT = 'PRESENT', 'Present'
        ABSENT = 'ABSENT', 'Absent'
        ON_LEAVE = 'LEAVE', 'On Approved Leave'
        OUTPASS = 'OUTPASS', 'Out on Outpass'

    resident = models.ForeignKey(ResidentProfile, on_delete=models.CASCADE, related_name='attendance_records')
    date = models.DateField()
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PRESENT)
    marked_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name='marked_attendances')
    remarks = models.CharField(max_length=200, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('resident', 'date')
        ordering = ['-date', 'resident']

    def __str__(self):
        return f"{self.resident.student_id} - {self.date}: {self.get_status_display()}"


class OutpassRequest(models.Model):
    class Status(models.TextChoices):
        PENDING = 'PENDING', 'Pending Approval'
        APPROVED = 'APPROVED', 'Approved'
        REJECTED = 'REJECTED', 'Rejected'
        DEPARTED = 'DEPARTED', 'Departed'
        RETURNED = 'RETURNED', 'Returned Safely'
        OVERDUE = 'OVERDUE', 'Overdue Return'

    resident = models.ForeignKey(ResidentProfile, on_delete=models.CASCADE, related_name='outpass_requests')
    purpose = models.CharField(max_length=200, help_text="e.g. Weekend Home Visit, Medical Appointment")
    destination_address = models.TextField(help_text="Where the resident will be staying")
    departure_time = models.DateTimeField()
    expected_return_time = models.DateTimeField()
    actual_return_time = models.DateTimeField(null=True, blank=True)
    parent_contact = models.CharField(max_length=20, help_text="Parent / Guardian phone number")
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
    approved_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='approved_outpasses')
    remarks = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Outpass: {self.resident.student_id} ({self.get_status_display()})"
