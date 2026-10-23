from django.test import TestCase
from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model
from decimal import Decimal

from apps.rooms.models import HostelBlock, Room, Bed
from apps.residents.models import ResidentProfile
from apps.allocations.models import SeatApplication, SeatAllocation, RoomTransferRequest, CheckoutClearance
from apps.allocations.services import AllocationService

User = get_user_model()


class AllocationServiceTests(TestCase):
    def setUp(self):
        self.warden = User.objects.create_user(username='test_warden', password='password123', role=User.Role.WARDEN)
        self.resident_user = User.objects.create_user(username='test_res', password='password123', role=User.Role.RESIDENT)
        self.resident = ResidentProfile.objects.create(user=self.resident_user, student_id='RES-SERV-01')

        self.block = HostelBlock.objects.create(name='Block Service', code='BS-1')
        self.room1 = Room.objects.create(block=self.block, room_number='101', floor=1, capacity=2)
        self.bed1 = Bed.objects.create(room=self.room1, bed_number='Bed-A')
        self.bed2 = Bed.objects.create(room=self.room1, bed_number='Bed-B')

    def test_allocate_bed_success(self):
        """IT-001: Successfully allocate bed updates bed occupancy and resident profile."""
        alloc = AllocationService.allocate_bed(
            resident=self.resident,
            bed=self.bed1,
            actor=self.warden,
            notes="Regular allocation"
        )
        self.bed1.refresh_from_db()
        self.resident.refresh_from_db()

        self.assertTrue(self.bed1.is_occupied)
        self.assertEqual(self.resident.current_bed, self.bed1)
        self.assertEqual(self.resident.status, ResidentProfile.Status.ACTIVE)
        self.assertTrue(alloc.is_active)

    def test_allocate_already_occupied_bed_fails(self):
        """IT-002: Cannot allocate an already occupied bed."""
        self.bed1.is_occupied = True
        self.bed1.save()

        with self.assertRaises(ValidationError):
            AllocationService.allocate_bed(
                resident=self.resident,
                bed=self.bed1,
                actor=self.warden
            )

    def test_room_transfer_workflow(self):
        """IT-003: Room transfer safely releases old bed and takes new bed."""
        AllocationService.allocate_bed(resident=self.resident, bed=self.bed1, actor=self.warden)

        transfer_req = RoomTransferRequest.objects.create(
            resident=self.resident,
            current_bed=self.bed1,
            target_room=self.room1,
            reason="Relocate to Bed B"
        )

        AllocationService.execute_room_transfer(transfer_req, self.bed2, self.warden)

        self.bed1.refresh_from_db()
        self.bed2.refresh_from_db()
        self.resident.refresh_from_db()

        self.assertFalse(self.bed1.is_occupied) # Old bed released
        self.assertTrue(self.bed2.is_occupied) # New bed occupied
        self.assertEqual(self.resident.current_bed, self.bed2)
        self.assertEqual(transfer_req.status, RoomTransferRequest.Status.COMPLETED)
