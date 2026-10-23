from django.db import models
from django.core.exceptions import ValidationError


class HostelBlock(models.Model):
    class GenderPolicy(models.TextChoices):
        MALE = 'MALE', 'Boys Hostel'
        FEMALE = 'FEMALE', 'Girls Hostel'
        COED = 'COED', 'Co-Educational'

    name = models.CharField(max_length=100, unique=True, help_text="e.g. Building A, Block 1")
    code = models.CharField(max_length=20, unique=True, help_text="Short code, e.g. BLK-A")
    gender_policy = models.CharField(max_length=20, choices=GenderPolicy.choices, default=GenderPolicy.COED)
    total_floors = models.PositiveIntegerField(default=3)
    description = models.TextField(blank=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return f"{self.name} ({self.get_gender_policy_display()})"


class Room(models.Model):
    class RoomType(models.TextChoices):
        SINGLE = 'SINGLE', 'Single Occupancy'
        DOUBLE = 'DOUBLE', 'Double Sharing'
        TRIPLE = 'TRIPLE', 'Triple Sharing'
        DORMITORY = 'DORM', 'Dormitory (4+ beds)'

    block = models.ForeignKey(HostelBlock, on_delete=models.CASCADE, related_name='rooms')
    room_number = models.CharField(max_length=20, help_text="e.g. 101, 102, 201")
    floor = models.PositiveIntegerField(default=1)
    room_type = models.CharField(max_length=20, choices=RoomType.choices, default=RoomType.DOUBLE)
    capacity = models.PositiveIntegerField(default=2, help_text="Maximum bed capacity of this room")
    base_fee = models.DecimalField(max_digits=10, decimal_places=2, default=5000.00, help_text="Base monthly fee in ₹")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('block', 'room_number')
        ordering = ['block', 'floor', 'room_number']

    def __str__(self):
        return f"{self.block.name} - Room {self.room_number}"

    def clean(self):
        # Validate that existing beds do not exceed the capacity
        if self.pk:
            current_beds_count = self.beds.count()
            if self.capacity < current_beds_count:
                raise ValidationError(f"Capacity cannot be less than the existing number of beds ({current_beds_count}).")

    @property
    def occupied_beds_count(self):
        return self.beds.filter(is_occupied=True).count()

    @property
    def available_beds_count(self):
        return self.beds.filter(is_occupied=False).count()

    @property
    def is_full(self):
        return self.available_beds_count == 0


class Bed(models.Model):
    room = models.ForeignKey(Room, on_delete=models.CASCADE, related_name='beds')
    bed_number = models.CharField(max_length=20, help_text="e.g. Bed-A, Bed-B or 1, 2")
    is_occupied = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('room', 'bed_number')
        ordering = ['room', 'bed_number']

    def __str__(self):
        return f"{self.room.block.name} | Room {self.room.room_number} - {self.bed_number}"

    def clean(self):
        # Ensure that room capacity is not exceeded when creating a new bed
        if not self.pk:
            current_beds = self.room.beds.count()
            if current_beds >= self.room.capacity:
                raise ValidationError(f"Cannot add bed: Room {self.room.room_number} has reached max capacity of {self.room.capacity}.")


class Amenity(models.Model):
    class Status(models.TextChoices):
        OPERATIONAL = 'OPERATIONAL', 'Operational'
        DEGRADED = 'DEGRADED', 'Minor Issue'
        OUTAGE = 'OUTAGE', 'Outage / Maintenance'

    name = models.CharField(max_length=100, unique=True, help_text="e.g. Light, Water, Wifi, Laundry, Hot Water")
    icon = models.CharField(max_length=50, default='lightbulb', help_text="Icon identifier")
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.OPERATIONAL)
    description = models.CharField(max_length=255, blank=True)
    last_inspected = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = 'Amenities'
        ordering = ['name']

    def __str__(self):
        return f"{self.name} - {self.get_status_display()}"
