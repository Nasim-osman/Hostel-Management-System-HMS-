from django.db import models
from django.conf import settings
from apps.residents.models import ResidentProfile
from apps.rooms.models import Room, Bed, HostelBlock


class SeatApplication(models.Model):
    class Status(models.TextChoices):
        PENDING = 'PENDING', 'Pending Review'
        APPROVED = 'APPROVED', 'Approved (Pending Allocation)'
        REJECTED = 'REJECTED', 'Rejected'
        WAITLISTED = 'WAITLISTED', 'Placed on Waiting List'
        ALLOCATED = 'ALLOCATED', 'Seat Allocated'

    resident = models.ForeignKey(ResidentProfile, on_delete=models.CASCADE, related_name='seat_applications')
    preferred_room_type = models.CharField(max_length=20, choices=Room.RoomType.choices, default=Room.RoomType.DOUBLE)
    preferred_block = models.ForeignKey(HostelBlock, on_delete=models.SET_NULL, null=True, blank=True)
    academic_year = models.CharField(max_length=20, default='2026-2027')
    applied_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
    reviewed_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='reviewed_applications')
    review_date = models.DateTimeField(null=True, blank=True)
    review_notes = models.TextField(blank=True)

    class Meta:
        ordering = ['-applied_at']

    def __str__(self):
        return f"Application #{self.id} - {self.resident.student_id} ({self.get_status_display()})"


class SeatAllocation(models.Model):
    application = models.OneToOneField(SeatApplication, on_delete=models.SET_NULL, null=True, blank=True, related_name='allocation')
    resident = models.ForeignKey(ResidentProfile, on_delete=models.CASCADE, related_name='allocations')
    bed = models.ForeignKey(Bed, on_delete=models.PROTECT, related_name='allocations')
    allocated_at = models.DateTimeField(auto_now_add=True)
    allocated_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name='made_allocations')
    is_active = models.BooleanField(default=True)
    vacated_at = models.DateTimeField(null=True, blank=True)
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ['-allocated_at']

    def __str__(self):
        return f"Allocation: {self.resident.student_id} -> {self.bed}"


class WaitingListEntry(models.Model):
    class Status(models.TextChoices):
        WAITING = 'WAITING', 'Waiting in Queue'
        OFFERED = 'OFFERED', 'Seat Offered'
        ACCEPTED = 'ACCEPTED', 'Offer Accepted'
        DECLINED = 'DECLINED', 'Offer Declined'
        REMOVED = 'REMOVED', 'Removed from List'

    application = models.OneToOneField(SeatApplication, on_delete=models.CASCADE, related_name='waiting_list_entry')
    priority_number = models.PositiveIntegerField(help_text="Queue position (1 is highest priority)")
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.WAITING)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['priority_number', 'created_at']
        verbose_name_plural = 'Waiting List Entries'

    def __str__(self):
        return f"Waitlist #{self.priority_number}: {self.application.resident.student_id}"


class RoomTransferRequest(models.Model):
    class Status(models.TextChoices):
        PENDING = 'PENDING', 'Pending Approval'
        APPROVED = 'APPROVED', 'Approved (Pending Bed Selection)'
        REJECTED = 'REJECTED', 'Rejected'
        COMPLETED = 'COMPLETED', 'Transfer Completed'

    resident = models.ForeignKey(ResidentProfile, on_delete=models.CASCADE, related_name='transfer_requests')
    current_bed = models.ForeignKey(Bed, on_delete=models.PROTECT, related_name='transfers_from')
    target_room = models.ForeignKey(Room, on_delete=models.SET_NULL, null=True, blank=True, related_name='transfers_to')
    reason = models.TextField(help_text="State the valid operational or medical reason for room transfer")
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
    requested_at = models.DateTimeField(auto_now_add=True)
    processed_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    decision_notes = models.TextField(blank=True)

    class Meta:
        ordering = ['-requested_at']

    def __str__(self):
        return f"Transfer #{self.id}: {self.resident.student_id} ({self.get_status_display()})"


class CheckoutClearance(models.Model):
    class Status(models.TextChoices):
        PENDING = 'PENDING', 'Pending Clearance'
        IN_PROGRESS = 'IN_PROGRESS', 'In Progress'
        APPROVED = 'APPROVED', 'Approved'
        REJECTED = 'REJECTED', 'Rejected'
        COMPLETED = 'COMPLETED', 'Checkout Finalized'

    resident = models.ForeignKey(ResidentProfile, on_delete=models.CASCADE, related_name='clearance_requests')
    request_date = models.DateField(auto_now_add=True)
    expected_checkout_date = models.DateField()
    
    # Clearance steps
    property_clearance = models.BooleanField(default=False, help_text="Room inspected, keys & fixtures returned")
    property_cleared_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='cleared_properties')
    
    accounts_clearance = models.BooleanField(default=False, help_text="All fees and fines fully settled")
    accounts_cleared_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='cleared_accounts')
    
    warden_approval = models.BooleanField(default=False, help_text="Final Warden sign-off")
    warden_approved_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='approved_checkouts')
    
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
    clearance_notes = models.TextField(blank=True)
    finalized_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-request_date']

    def __str__(self):
        return f"Clearance #{self.id} for {self.resident.student_id} ({self.get_status_display()})"

    @property
    def is_fully_cleared(self):
        return self.property_clearance and self.accounts_clearance and self.warden_approval
