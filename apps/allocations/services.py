from django.db import transaction
from django.core.exceptions import ValidationError
from django.utils import timezone
from .models import SeatApplication, SeatAllocation, WaitingListEntry, RoomTransferRequest, CheckoutClearance
from apps.rooms.models import Bed
from apps.residents.models import ResidentProfile


class AllocationService:
    @staticmethod
    @transaction.atomic
    def allocate_bed(resident, bed, actor, application=None, notes=""):
        """
        Atomically allocates a bed to a resident.
        Enforces:
        - Bed must not be occupied.
        - Resident must not already have an active conflicting bed.
        """
        # Lock bed record for update
        locked_bed = Bed.objects.select_for_update().get(id=bed.id)
        if locked_bed.is_occupied:
            raise ValidationError(f"Bed '{locked_bed}' is already occupied.")

        # Check if resident has an existing active bed
        if resident.current_bed:
            raise ValidationError(f"Resident {resident.student_id} is already assigned to {resident.current_bed}.")

        # Mark bed occupied
        locked_bed.is_occupied = True
        locked_bed.save()

        # Update resident profile
        resident.current_bed = locked_bed
        resident.status = ResidentProfile.Status.ACTIVE
        if not resident.admission_date:
            resident.admission_date = timezone.now().date()
        resident.save()

        # Create allocation record
        allocation = SeatAllocation.objects.create(
            application=application,
            resident=resident,
            bed=locked_bed,
            allocated_by=actor,
            is_active=True,
            notes=notes
        )

        # Update application status if provided
        if application:
            application.status = SeatApplication.Status.ALLOCATED
            application.save()

            # Remove from waiting list if present
            WaitingListEntry.objects.filter(application=application).update(
                status=WaitingListEntry.Status.REMOVED
            )

        return allocation

    @staticmethod
    @transaction.atomic
    def execute_room_transfer(transfer_request, new_bed, actor):
        """
        Atomically transfers a resident to a new bed.
        """
        locked_new_bed = Bed.objects.select_for_update().get(id=new_bed.id)
        if locked_new_bed.is_occupied:
            raise ValidationError(f"Target bed '{locked_new_bed}' is already occupied.")

        resident = transfer_request.resident
        old_bed = resident.current_bed

        # Deactivate old allocation
        SeatAllocation.objects.filter(resident=resident, is_active=True).update(
            is_active=False,
            vacated_at=timezone.now()
        )

        # Release old bed
        if old_bed:
            old_bed.is_occupied = False
            old_bed.save()

        # Occupy new bed
        locked_new_bed.is_occupied = True
        locked_new_bed.save()

        # Update resident current bed
        resident.current_bed = locked_new_bed
        resident.save()

        # Create new allocation
        new_allocation = SeatAllocation.objects.create(
            resident=resident,
            bed=locked_new_bed,
            allocated_by=actor,
            is_active=True,
            notes=f"Room Transfer from {old_bed} to {locked_new_bed}"
        )

        transfer_request.status = RoomTransferRequest.Status.COMPLETED
        transfer_request.processed_by = actor
        transfer_request.save()

        return new_allocation

    @staticmethod
    @transaction.atomic
    def finalize_checkout(clearance, actor):
        """
        Completes resident checkout and releases their bed.
        """
        if not clearance.is_fully_cleared:
            raise ValidationError("All clearance checks (Property, Accounts, Warden) must be approved before final checkout.")

        resident = clearance.resident
        current_bed = resident.current_bed

        if current_bed:
            current_bed.is_occupied = False
            current_bed.save()

        SeatAllocation.objects.filter(resident=resident, is_active=True).update(
            is_active=False,
            vacated_at=timezone.now()
        )

        resident.current_bed = None
        resident.status = ResidentProfile.Status.CHECKED_OUT
        resident.save()

        clearance.status = CheckoutClearance.Status.COMPLETED
        clearance.finalized_at = timezone.now()
        clearance.save()

        return True
