from django.db import models
from django.conf import settings
from apps.rooms.models import Bed, Room


class ResidentProfile(models.Model):
    class Status(models.TextChoices):
        APPLICANT = 'APPLICANT', 'Applicant'
        ACTIVE = 'ACTIVE', 'Active Resident'
        CHECKED_OUT = 'CHECKED_OUT', 'Checked Out'
        SUSPENDED = 'SUSPENDED', 'Suspended'

    class Gender(models.TextChoices):
        MALE = 'MALE', 'Male'
        FEMALE = 'FEMALE', 'Female'
        OTHER = 'OTHER', 'Other'

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='resident_profile'
    )
    student_id = models.CharField(max_length=50, unique=True, help_text="University or Institutional Resident ID")
    course = models.CharField(max_length=100, blank=True, help_text="e.g. B.Tech Computer Science")
    batch_year = models.CharField(max_length=20, blank=True, help_text="e.g. 2023-2027")
    gender = models.CharField(max_length=10, choices=Gender.choices, default=Gender.MALE)
    blood_group = models.CharField(max_length=10, blank=True)
    emergency_contact_name = models.CharField(max_length=100, blank=True)
    emergency_contact_phone = models.CharField(max_length=20, blank=True)
    emergency_contact_relation = models.CharField(max_length=50, blank=True)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.APPLICANT)
    admission_date = models.DateField(null=True, blank=True)
    current_bed = models.OneToOneField(
        Bed,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='current_resident',
        help_text="Currently assigned bed"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['student_id']

    def __str__(self):
        return f"{self.user.get_full_name() or self.user.username} ({self.student_id})"

    @property
    def current_room(self):
        return self.current_bed.room if self.current_bed else None
