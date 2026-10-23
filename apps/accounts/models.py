from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    class Role(models.TextChoices):
        ADMIN = 'ADMIN', 'System Administrator'
        WARDEN = 'WARDEN', 'Hostel Manager / Warden'
        ACCOUNTS = 'ACCOUNTS', 'Accounts Staff'
        MAINTENANCE = 'MAINTENANCE', 'Maintenance Staff'
        RESIDENT = 'RESIDENT', 'Resident'

    role = models.CharField(
        max_length=20,
        choices=Role.choices,
        default=Role.RESIDENT,
        help_text="Designates the user's role and permission scope in HMS."
    )
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    profile_picture = models.ImageField(upload_to='profiles/', blank=True, null=True)

    class Meta:
        verbose_name = 'User'
        verbose_name_plural = 'Users'
        ordering = ['username']

    def __str__(self):
        full = self.get_full_name()
        return f"{full} ({self.get_role_display()})" if full else f"{self.username} ({self.get_role_display()})"

    @property
    def is_admin_user(self):
        return self.role == self.Role.ADMIN or self.is_superuser

    @property
    def is_warden(self):
        return self.role == self.Role.WARDEN

    @property
    def is_accounts_staff(self):
        return self.role == self.Role.ACCOUNTS

    @property
    def is_maintenance_staff(self):
        return self.role == self.Role.MAINTENANCE

    @property
    def is_resident(self):
        return self.role == self.Role.RESIDENT

    @property
    def is_staff_member(self):
        return self.role in [self.Role.ADMIN, self.Role.WARDEN, self.Role.ACCOUNTS, self.Role.MAINTENANCE]
