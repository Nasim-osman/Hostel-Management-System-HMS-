from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta
from decimal import Decimal

from apps.rooms.models import HostelBlock, Room, Bed, Amenity
from apps.residents.models import ResidentProfile
from apps.allocations.models import SeatApplication, SeatAllocation, WaitingListEntry, RoomTransferRequest, CheckoutClearance
from apps.finance.models import FeeCategory, ResidentCharge, Payment, Fine, Refund, HostelExpense
from apps.complaints.models import Complaint
from apps.dining.models import MealMenu, MessFeedback
from apps.visitors.models import VisitorLog
from apps.attendance.models import AttendanceRecord, OutpassRequest
from apps.notices.models import Notice
from apps.notifications.models import notify_user, InAppNotification
from apps.abtesting.models import Experiment, UserVariantAssignment, MetricEvent

User = get_user_model()


class Command(BaseCommand):
    help = 'Populates the HMS database with realistic, industry-standard demo data matching dashboard statistics.'

    def handle(self, *args, **options):
        self.stdout.write("Seeding HMS database with demonstration records...")

        # 1. Create Core Role Users
        users_data = [
            {'username': 'admin', 'email': 'admin@hms.university.edu', 'first_name': 'Admin', 'last_name': 'Nasim', 'role': User.Role.ADMIN, 'phone': '+880 1711 000001'},
            {'username': 'warden', 'email': 'warden@hms.university.edu', 'first_name': 'Warden', 'last_name': 'Nasim', 'role': User.Role.WARDEN, 'phone': '+880 1819 000002'},
            {'username': 'accounts', 'email': 'accounts@hms.university.edu', 'first_name': 'Accounts', 'last_name': 'Nasim', 'role': User.Role.ACCOUNTS, 'phone': '+880 1912 000003'},
            {'username': 'maintenance', 'email': 'maintenance@hms.university.edu', 'first_name': 'Maintenance', 'last_name': 'Nasim', 'role': User.Role.MAINTENANCE, 'phone': '+880 1515 000004'},
        ]

        created_users = {}
        for u in users_data:
            user, created = User.objects.get_or_create(
                username=u['username'],
                defaults={
                    'email': u['email'],
                    'first_name': u['first_name'],
                    'last_name': u['last_name'],
                    'role': u['role'],
                    'phone_number': u['phone'],
                    'is_staff': True if u['role'] in [User.Role.ADMIN, User.Role.WARDEN] else False,
                    'is_superuser': True if u['role'] == User.Role.ADMIN else False,
                }
            )
            user.set_password('demo1234')
            user.save()
            created_users[u['username']] = user

        admin_user = created_users['admin']
        warden_user = created_users['warden']
        accounts_user = created_users['accounts']
        maintenance_user = created_users['maintenance']

        # 2. Amenities (Matching screenshot: Light, Water, Wifi, Laundry, Hot Water)
        amenities_data = [
            {'name': 'Light', 'icon': 'lightbulb', 'status': Amenity.Status.OPERATIONAL, 'desc': 'All electrical lines operational.'},
            {'name': 'Water', 'icon': 'tint', 'status': Amenity.Status.OPERATIONAL, 'desc': 'Clean filtered water supply 24/7.'},
            {'name': 'Wifi', 'icon': 'wifi', 'status': Amenity.Status.OPERATIONAL, 'desc': 'High-speed campus fiber active.'},
            {'name': 'Laundry', 'icon': 'tshirt', 'status': Amenity.Status.OPERATIONAL, 'desc': 'Automated washing units in Block A & B.'},
            {'name': 'Hot Water', 'icon': 'shower', 'status': Amenity.Status.OPERATIONAL, 'desc': 'Solar water geysers active.'},
        ]
        for a in amenities_data:
            Amenity.objects.update_or_create(name=a['name'], defaults={'status': a['status'], 'description': a['desc']})

        # 3. Blocks & Rooms Setup (Exact numbers: Total 200 Rooms, 500 Capacity, 375 Occupied, 50 Vacant Rooms)
        block_a, _ = HostelBlock.objects.get_or_create(name='Building A', defaults={'code': 'BLK-A', 'gender_policy': HostelBlock.GenderPolicy.MALE, 'total_floors': 3})
        block_b, _ = HostelBlock.objects.get_or_create(name='Building B', defaults={'code': 'BLK-B', 'gender_policy': HostelBlock.GenderPolicy.COED, 'total_floors': 3})

        all_beds = []
        all_rooms = []
        
        # We will create 200 rooms: 150 occupied rooms (with 375 occupied beds) and 50 vacant rooms (with 125 vacant beds). Total capacity = 500 beds!
        # Rooms 1 to 150: occupied rooms. (e.g. mix of Double and Triple sharing: 75 Double (150 beds) + 75 Triple (225 beds) = 375 beds occupied)
        # Rooms 151 to 200: 50 vacant rooms (e.g. 25 Double (50 beds) + 25 Triple (75 beds) = 125 beds vacant).
        # Total = 200 rooms, 500 beds, 375 occupied beds (75%), 50 vacant rooms! EXACT MATCH TO SCREENSHOT!
        
        existing_rooms_count = Room.objects.count()
        if existing_rooms_count < 200:
            Room.objects.all().delete()
            Bed.objects.all().delete()

            # Create occupied rooms
            for r_idx in range(1, 151):
                block = block_a if r_idx <= 100 else block_b
                floor = ((r_idx - 1) % 3) + 1
                room_num = f"{floor}{r_idx:02d}"
                capacity = 3 if r_idx > 75 else 2
                room = Room.objects.create(
                    block=block,
                    room_number=room_num,
                    floor=floor,
                    room_type=Room.RoomType.TRIPLE if capacity == 3 else Room.RoomType.DOUBLE,
                    capacity=capacity,
                    base_fee=Decimal('6000.00') if capacity == 2 else Decimal('4500.00'),
                    is_active=True
                )
                all_rooms.append(room)
                for b_idx in range(1, capacity + 1):
                    bed = Bed.objects.create(
                        room=room,
                        bed_number=f"Bed-{chr(64 + b_idx)}",
                        is_occupied=True # occupied!
                    )
                    all_beds.append(bed)

            # Create 50 vacant rooms
            for r_idx in range(151, 201):
                block = block_b
                floor = ((r_idx - 1) % 3) + 1
                room_num = f"{floor}{r_idx:02d}"
                capacity = 3 if r_idx > 175 else 2
                room = Room.objects.create(
                    block=block,
                    room_number=room_num,
                    floor=floor,
                    room_type=Room.RoomType.TRIPLE if capacity == 3 else Room.RoomType.DOUBLE,
                    capacity=capacity,
                    base_fee=Decimal('6000.00') if capacity == 2 else Decimal('4500.00'),
                    is_active=True
                )
                all_rooms.append(room)
                for b_idx in range(1, capacity + 1):
                    bed = Bed.objects.create(
                        room=room,
                        bed_number=f"Bed-{chr(64 + b_idx)}",
                        is_occupied=False # vacant!
                    )
                    all_beds.append(bed)

        # 4. Create Key Named Residents (Exact match to screenshot tickets: Mike Ross, Jennifer Grint, Casey Allen, Tina Harris, Rick Butcher)
        named_residents_data = [
            {'username': 'resident_nasim', 'name': ('Resident', 'Nasim'), 'email': 'resident.nasim@student.edu', 'id': 'DU-CSE-2022-001', 'course': 'Computer Science & Eng. (B.Sc)', 'room_idx': 0, 'ticket': 'Water not Comming', 'category': Complaint.Category.PLUMBING},
            {'username': 'resident_mike', 'name': ('Resident', 'Nasim'), 'email': 'resident.mike@student.edu', 'id': 'DU-CSE-2022-002', 'course': 'Computer Science & Eng. (B.Sc)', 'room_idx': 1, 'ticket': 'Light is not available since last night', 'category': Complaint.Category.ELECTRICAL},
            {'username': 'resident_casey', 'name': ('Casey', 'Allen'), 'email': 'casey.a@student.edu', 'id': 'BUET-ME-2022-003', 'course': 'Mechanical Engineering', 'room_idx': 2, 'ticket': 'Wifi is not working since past week, please fix it.', 'category': Complaint.Category.WIFI},
            {'username': 'resident_tina', 'name': ('Tina', 'Harris'), 'email': 'tina.h@student.edu', 'id': 'JU-IIT-2023-004', 'course': 'Information Technology (B.Sc)', 'room_idx': 3, 'ticket': 'Laundry is not working properly, please look into this quickly', 'category': Complaint.Category.LAUNDRY},
            {'username': 'resident_rick', 'name': ('Rick', 'Butcher'), 'email': 'rick.b@student.edu', 'id': 'SUST-SWE-2022-005', 'course': 'Software Engineering (B.Sc)', 'room_idx': 4, 'ticket': 'Hot water tap is broken, please fix it urgently', 'category': Complaint.Category.PLUMBING},
        ]

        occupied_beds_query = list(Bed.objects.filter(is_occupied=True)[:10])

        created_residents = []
        for idx, nr in enumerate(named_residents_data):
            user, _ = User.objects.get_or_create(
                username=nr['username'],
                defaults={
                    'email': nr['email'],
                    'first_name': nr['name'][0],
                    'last_name': nr['name'][1],
                    'role': User.Role.RESIDENT,
                    'phone_number': f'+880 1712 1000{idx+1}'
                }
            )
            user.set_password('demo1234')
            user.save()

            assigned_bed = occupied_beds_query[idx] if idx < len(occupied_beds_query) else None

            resident, _ = ResidentProfile.objects.update_or_create(
                user=user,
                defaults={
                    'student_id': nr['id'],
                    'course': nr['course'],
                    'batch_year': '2022-2026',
                    'gender': ResidentProfile.Gender.MALE if idx % 2 == 0 else ResidentProfile.Gender.FEMALE,
                    'blood_group': 'B+' if idx % 2 == 0 else 'O+',
                    'emergency_contact_name': f"Md. Guardian of {nr['name'][0]}",
                    'emergency_contact_phone': f'+880 1819 9900{idx+1}',
                    'emergency_contact_relation': 'Parent / Guardian',
                    'status': ResidentProfile.Status.ACTIVE,
                    'admission_date': timezone.now().date() - timedelta(days=60),
                    'current_bed': assigned_bed
                }
            )
            created_residents.append((resident, nr))

        # 5. Complaints / Tickets (Exact match to screenshot tickets!)
        Complaint.objects.all().delete()
        for idx, (res, nr) in enumerate(created_residents):
            Complaint.objects.create(
                ticket_number=f"HMS-TICK-2026-00{idx+1}",
                resident=res,
                room=res.current_room,
                title=nr['ticket'],
                category=nr['category'],
                priority=Complaint.Priority.HIGH if idx < 2 else Complaint.Priority.MEDIUM,
                status=Complaint.Status.SUBMITTED if idx == 0 else Complaint.Status.IN_PROGRESS,
                description=f"Resident reports: {nr['ticket']}. Please inspect immediately.",
                assigned_to=maintenance_user if idx > 0 else None,
                created_at=timezone.now() - timedelta(hours=(idx * 4 + 2))
            )

        # 6. Mess / Dining Menu (Exact match to screenshot: Breakfast 3 Idli Sambar, Lunch Veg/Non-Veg, Dinner Veg/Non-Veg)
        MealMenu.objects.all().delete()
        MealMenu.objects.create(
            meal_type=MealMenu.MealType.BREAKFAST,
            timing='7:30 AM - 9:30 AM',
            veg_items='3 Idli Sambar',
            non_veg_items='Boiled Eggs',
            is_active=True
        )
        MealMenu.objects.create(
            meal_type=MealMenu.MealType.LUNCH,
            timing='12:30 PM - 2:30 PM',
            veg_items='Sprouts | 3 Chapatis | Rice | Dal',
            non_veg_items='Egg Biryani',
            is_active=True
        )
        MealMenu.objects.create(
            meal_type=MealMenu.MealType.DINNER,
            timing='7:30 PM - 9:30 PM',
            veg_items='Sprouts | 3 Chapatis | Rice | Dal',
            non_veg_items='Egg Curry | 3 Chapatis | Rice',
            is_active=True
        )

        # 7. Active Visitors (Exact match to screenshot: Total 2, Building A | Floor 2nd | Room 201, Building A | Floor 1st | Room 103)
        VisitorLog.objects.all().delete()
        VisitorLog.objects.create(
            visitor_name='Arthur Ross',
            visitor_phone='+880 1711 881001',
            resident=created_residents[0][0],
            relationship='Father',
            destination='Building A | Floor 2nd | Room 201',
            purpose='Semester visit & family luggage drop-off',
            status=VisitorLog.Status.CHECKED_IN,
            gate_pass_no='GP-2601',
            recorded_by=warden_user
        )
        VisitorLog.objects.create(
            visitor_name='Sarah Grint',
            visitor_phone='+880 1819 881002',
            resident=created_residents[1][0],
            relationship='Mother',
            destination='Building A | Floor 1st | Room 103',
            purpose='Book delivery & care package',
            status=VisitorLog.Status.CHECKED_IN,
            gate_pass_no='GP-2602',
            recorded_by=warden_user
        )

        # 8. Finance (Exact match to screenshot stats: Paid ৳ 1,20,345 & Unpaid ৳ 20,345)
        Payment.objects.all().delete()
        ResidentCharge.objects.all().delete()
        FeeCategory.objects.all().delete()
        rent_cat = FeeCategory.objects.create(name='Hostel Accommodation Rent', default_amount=Decimal('15000.00'), frequency=FeeCategory.Frequency.SEMESTER)
        mess_cat = FeeCategory.objects.create(name='Mess & Dining Dues', default_amount=Decimal('12000.00'), frequency=FeeCategory.Frequency.SEMESTER)
        caution_cat = FeeCategory.objects.create(name='Caution Deposit', default_amount=Decimal('5000.00'), frequency=FeeCategory.Frequency.ONE_TIME)

        # Unpaid Charge (₹ 20,345 exact match!)
        unpaid_charge = ResidentCharge.objects.create(
            resident=created_residents[0][0],
            fee_category=rent_cat,
            description='Semester 1 Accommodation Fee',
            amount=Decimal('20345.00'),
            paid_amount=Decimal('0.00'),
            due_date=timezone.now().date() + timedelta(days=7),
            status=ResidentCharge.Status.UNPAID
        )

        # Paid Payment (₹ 1,20,345 exact match!)
        paid_charge = ResidentCharge.objects.create(
            resident=created_residents[1][0],
            fee_category=rent_cat,
            description='Annual Hostel Dues & Caution Deposit',
            amount=Decimal('120345.00'),
            paid_amount=Decimal('120345.00'),
            due_date=timezone.now().date() - timedelta(days=15),
            status=ResidentCharge.Status.PAID
        )

        Payment.objects.create(
            receipt_number='HMS-REC-202610-8A7B9C',
            resident=created_residents[1][0],
            charge=paid_charge,
            amount=Decimal('120345.00'),
            payment_date=timezone.now().date() - timedelta(days=14),
            payment_method=Payment.PaymentMethod.BANK_TRANSFER,
            transaction_reference='SONALI-DUC20261023881',
            status=Payment.Status.VERIFIED,
            recorded_by=accounts_user,
            verified_by=accounts_user,
            notes='Full semester accommodation dues & hall caution deposit verified via Sonali Bank.'
        )

        # Operating Expenses
        HostelExpense.objects.all().delete()
        HostelExpense.objects.create(
            category=HostelExpense.Category.UTILITIES,
            title='Monthly Electricity Grid Bill',
            payee='Dhaka Power Distribution Company (DPDC)',
            amount=Decimal('42500.00'),
            expense_date=timezone.now().date() - timedelta(days=5),
            invoice_number='INV-DPDC-9981',
            recorded_by=accounts_user
        )
        HostelExpense.objects.create(
            category=HostelExpense.Category.MESS_SUPPLIES,
            title='Bulk Provisions & Grocery Supply',
            payee='Karwan Bazar Wholesale Agro Market',
            amount=Decimal('68200.00'),
            expense_date=timezone.now().date() - timedelta(days=8),
            invoice_number='KBZ-8821',
            recorded_by=accounts_user
        )

        # 9. Seat Applications & Waiting List Entries
        SeatApplication.objects.all().delete()
        WaitingListEntry.objects.all().delete()
        app1 = SeatApplication.objects.create(
            resident=created_residents[0][0],
            preferred_room_type=Room.RoomType.DOUBLE,
            preferred_block=block_a,
            status=SeatApplication.Status.ALLOCATED,
            reviewed_by=warden_user
        )
        app2 = SeatApplication.objects.create(
            resident=created_residents[1][0],
            preferred_room_type=Room.RoomType.DOUBLE,
            preferred_block=block_a,
            status=SeatApplication.Status.ALLOCATED,
            reviewed_by=warden_user
        )

        # Pending application for waiting list demonstration
        waiting_user, _ = User.objects.get_or_create(
            username='resident_pending_1',
            defaults={'email': 'pending1@student.edu', 'first_name': 'David', 'last_name': 'Palmer', 'role': User.Role.RESIDENT}
        )
        waiting_user.set_password('demo1234')
        waiting_user.save()

        waiting_res, _ = ResidentProfile.objects.get_or_create(
            user=waiting_user,
            defaults={'student_id': 'HMS-RES-2026-099', 'course': 'Architecture B.Arch', 'status': ResidentProfile.Status.APPLICANT}
        )
        waiting_app = SeatApplication.objects.create(
            resident=waiting_res,
            preferred_room_type=Room.RoomType.SINGLE,
            preferred_block=block_b,
            status=SeatApplication.Status.WAITLISTED
        )
        WaitingListEntry.objects.create(
            application=waiting_app,
            priority_number=1,
            status=WaitingListEntry.Status.WAITING
        )

        # 10. Notices
        Notice.objects.all().delete()
        Notice.objects.create(
            title='Hostel Night Roll-Call Curfew Hours Announcement',
            category=Notice.Category.GENERAL,
            target_audience=Notice.TargetAudience.ALL,
            content='All residents are requested to be inside hostel premises by 9:30 PM. Outpasses must be logged digitally 24 hours prior.',
            is_published=True,
            created_by=warden_user
        )
        Notice.objects.create(
            title='Scheduled High-Speed Wifi Router Upgrade in Block A',
            category=Notice.Category.MAINTENANCE,
            target_audience=Notice.TargetAudience.RESIDENTS_ONLY,
            content='Network maintenance scheduled on Saturday between 2:00 PM and 4:00 PM. Hotspots will remain active in the library lounge.',
            is_published=True,
            created_by=warden_user
        )

        # 11. In-App Notifications
        InAppNotification.objects.all().delete()
        notify_user(
            recipient=warden_user,
            title='5 Maintenance Complaints Logged Today',
            message='Plumbing and electrical tickets have been logged by residents. Please assign to maintenance staff.',
            notification_type=InAppNotification.NotificationType.COMPLAINT,
            link='/complaints/'
        )
        notify_user(
            recipient=created_residents[0][0].user,
            title='Upcoming Fee Due Alert',
            message='Your Semester 1 Fee Invoice of ₹ 20,345 is due on ' + (timezone.now().date() + timedelta(days=7)).strftime('%B %d, %Y'),
            notification_type=InAppNotification.NotificationType.FEE_DUE,
            link='/finance/fees/'
        )

        # 12. A/B Testing Experiment Setup
        exp, _ = Experiment.objects.get_or_create(
            code='DASHBOARD_URGENT_ACTIONS',
            defaults={
                'name': 'Hostel Dashboard Urgent Pending Actions Layout',
                'hypothesis': 'Placing an urgent pending-actions banner at the top of the dashboard increases action item resolution rate.',
                'variant_a_name': 'Standard Grid Layout',
                'variant_b_name': 'Prioritized Pending Actions Panel',
                'primary_metric': 'Urgent Action CTR'
            }
        )
        UserVariantAssignment.objects.get_or_create(experiment=exp, user=admin_user, defaults={'variant': 'B'})
        UserVariantAssignment.objects.get_or_create(experiment=exp, user=warden_user, defaults={'variant': 'A'})
        
        # Seed simulated events for demonstration report
        MetricEvent.objects.all().delete()
        for _ in range(35):
            MetricEvent.objects.create(experiment=exp, user=warden_user, variant='A', event_name='VIEW_DASHBOARD')
        for _ in range(7):
            MetricEvent.objects.create(experiment=exp, user=warden_user, variant='A', event_name='CLICK_ACTION_ITEM')

        for _ in range(40):
            MetricEvent.objects.create(experiment=exp, user=admin_user, variant='B', event_name='VIEW_DASHBOARD')
        for _ in range(16):
            MetricEvent.objects.create(experiment=exp, user=admin_user, variant='B', event_name='CLICK_ACTION_ITEM')

        self.stdout.write(self.style.SUCCESS("Demo database successfully populated!"))
        self.stdout.write("Created demo users with password 'demo1234':")
        self.stdout.write("  - Admin: admin / demo1234")
        self.stdout.write("  - Warden: warden / demo1234")
        self.stdout.write("  - Accounts: accounts / demo1234")
        self.stdout.write("  - Maintenance: maintenance / demo1234")
        self.stdout.write("  - Resident: resident_mike / demo1234")
