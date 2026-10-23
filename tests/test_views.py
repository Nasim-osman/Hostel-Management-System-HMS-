from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from decimal import Decimal
from apps.residents.models import ResidentProfile
from apps.finance.models import Payment
from apps.complaints.models import Complaint

User = get_user_model()


class ViewIntegrationTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.admin = User.objects.create_user(username='admin_test', password='password123', role=User.Role.ADMIN, is_superuser=True)
        self.resident_u = User.objects.create_user(username='mike_test', password='password123', role=User.Role.RESIDENT)
        self.resident = ResidentProfile.objects.create(user=self.resident_u, student_id='RES-INT-01')

    def test_login_flow(self):
        """IT-004: Valid login redirects to dashboard router."""
        response = self.client.post(reverse('accounts:login'), {
            'username': 'admin_test',
            'password': 'password123'
        })
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('accounts:dashboard'))

    def test_export_csv_view(self):
        """IT-005: Admin can generate CSV export of rooms."""
        self.client.login(username='admin_test', password='password123')
        response = self.client.get(reverse('reports:export_csv', kwargs={'export_type': 'rooms'}))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers['Content-Type'], 'text/csv')
        self.assertIn('attachment; filename="HMS_Export_rooms_', response.headers['Content-Disposition'])

    def test_resident_submit_complaint(self):
        """IT-006: Resident submits maintenance complaint."""
        self.client.login(username='mike_test', password='password123')
        response = self.client.post(reverse('complaints:submit_complaint'), {
            'title': 'Test Water Tap Issue',
            'category': 'PLUMBING',
            'priority': 'MEDIUM',
            'description': 'Water tap loose and leaking continuously.'
        })
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Complaint.objects.filter(title='Test Water Tap Issue').exists())

    def test_download_receipt_pdf(self):
        """IT-007: Official verified receipt PDF download."""
        payment = Payment.objects.create(
            receipt_number='HMS-REC-TEST-9999',
            resident=self.resident,
            amount=Decimal('5000.00'),
            payment_date='2026-10-23',
            status=Payment.Status.VERIFIED,
            recorded_by=self.admin
        )
        self.client.login(username='mike_test', password='password123')
        response = self.client.get(reverse('finance:download_receipt', kwargs={'receipt_number': payment.receipt_number}))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers['Content-Type'], 'application/pdf')
        self.assertIn('HMS-Receipt-HMS-REC-TEST-9999.pdf', response.headers['Content-Disposition'])

    def test_resident_dashboard_view_renders_successfully(self):
        """IT-008: Resident dashboard renders without FieldError and handles outpasses."""
        from apps.attendance.models import OutpassRequest
        from django.utils import timezone
        from datetime import timedelta
        
        OutpassRequest.objects.create(
            resident=self.resident,
            purpose='Weekend Family Visit',
            destination_address='Dhanmondi, Dhaka',
            departure_time=timezone.now(),
            expected_return_time=timezone.now() + timedelta(days=2),
            parent_contact='+880 1711-223344'
        )
        self.client.login(username='mike_test', password='password123')
        response = self.client.get(reverse('residents:resident_dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertIn('Hostel Fee Balance', response.content.decode('utf-8'))

    def test_bangladeshi_number_and_currency_formatting(self):
        """IT-009: Test South Asian / Bangladeshi lakh grouping format."""
        from apps.finance.templatetags.hms_tags import bd_format, taka
        self.assertEqual(bd_format(120345), '1,20,345')
        self.assertEqual(bd_format(20345), '20,345')
        self.assertEqual(bd_format(1000000), '10,00,000')
        self.assertEqual(bd_format(500), '500')
        self.assertEqual(taka(120345), '৳ 1,20,345')

