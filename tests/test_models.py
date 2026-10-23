from django.test import TestCase
from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model
from decimal import Decimal

from apps.rooms.models import HostelBlock, Room, Bed, Amenity
from apps.residents.models import ResidentProfile
from apps.finance.models import FeeCategory, ResidentCharge, Payment

User = get_user_model()


class ModelUnitTests(TestCase):
    def setUp(self):
        self.block = HostelBlock.objects.create(name='Test Block', code='TB-1')
        self.room = Room.objects.create(
            block=self.block,
            room_number='101',
            floor=1,
            room_type=Room.RoomType.DOUBLE,
            capacity=2,
            base_fee=Decimal('5000.00')
        )
        self.bed_a = Bed.objects.create(room=self.room, bed_number='Bed-A')
        self.bed_b = Bed.objects.create(room=self.room, bed_number='Bed-B')

        self.user = User.objects.create_user(
            username='test_student',
            password='password123',
            role=User.Role.RESIDENT
        )
        self.resident = ResidentProfile.objects.create(
            user=self.user,
            student_id='TEST-RES-001',
            course='Computer Science'
        )

    def test_room_capacity_and_occupancy(self):
        """UT-001: Room bed capacity and vacancy calculations."""
        self.assertEqual(self.room.capacity, 2)
        self.assertEqual(self.room.available_beds_count, 2)
        self.assertEqual(self.room.occupied_beds_count, 0)
        self.assertFalse(self.room.is_full)

        self.bed_a.is_occupied = True
        self.bed_a.save()

        self.assertEqual(self.room.available_beds_count, 1)
        self.assertEqual(self.room.occupied_beds_count, 1)

    def test_bed_clean_prevents_capacity_exceeded(self):
        """UT-002: Exceeding room capacity triggers validation error."""
        extra_bed = Bed(room=self.room, bed_number='Bed-C')
        with self.assertRaises(ValidationError):
            extra_bed.clean()

    def test_charge_and_balance_calculation(self):
        """UT-003: Resident charge balance remaining calculation."""
        fee_cat = FeeCategory.objects.create(name='Hostel Rent', default_amount=Decimal('5000.00'))
        charge = ResidentCharge.objects.create(
            resident=self.resident,
            fee_category=fee_cat,
            description='Semester Rent',
            amount=Decimal('5000.00'),
            due_date='2026-11-01'
        )
        self.assertEqual(charge.balance_remaining, Decimal('5000.00'))

        charge.paid_amount = Decimal('2000.00')
        charge.save()
        self.assertEqual(charge.balance_remaining, Decimal('3000.00'))
