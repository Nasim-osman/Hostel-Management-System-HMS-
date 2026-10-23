from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from apps.residents.models import ResidentProfile

User = get_user_model()


class RBACTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.admin = User.objects.create_user(username='admin_u', password='password123', role=User.Role.ADMIN, is_superuser=True)
        self.warden = User.objects.create_user(username='warden_u', password='password123', role=User.Role.WARDEN)
        self.accounts = User.objects.create_user(username='accounts_u', password='password123', role=User.Role.ACCOUNTS)
        self.maintenance = User.objects.create_user(username='maint_u', password='password123', role=User.Role.MAINTENANCE)

        self.resident1_u = User.objects.create_user(username='res1_u', password='password123', role=User.Role.RESIDENT)
        self.resident1 = ResidentProfile.objects.create(user=self.resident1_u, student_id='RES-001')

        self.resident2_u = User.objects.create_user(username='res2_u', password='password123', role=User.Role.RESIDENT)
        self.resident2 = ResidentProfile.objects.create(user=self.resident2_u, student_id='RES-002')

    def test_unauthenticated_user_redirected_to_login(self):
        """SEC-001: Unauthenticated request to protected dashboard redirects to login."""
        response = self.client.get(reverse('accounts:hostel_dashboard'))
        self.assertEqual(response.status_code, 302)
        self.assertIn('/accounts/login/', response.url)

    def test_resident_cannot_access_audit_logs(self):
        """SEC-002: Resident cannot view admin audit logs (raises 403 PermissionDenied)."""
        self.client.login(username='res1_u', password='password123')
        response = self.client.get(reverse('audit:audit_list'))
        self.assertEqual(response.status_code, 403)

    def test_resident_cannot_access_user_management(self):
        """SEC-003: Resident cannot view user account management list."""
        self.client.login(username='res1_u', password='password123')
        response = self.client.get(reverse('accounts:user_list'))
        self.assertEqual(response.status_code, 403)

    def test_resident_cannot_view_other_resident_profile(self):
        """SEC-004: IDOR Protection: Resident cannot inspect another resident's profile details."""
        self.client.login(username='res1_u', password='password123')
        # Resident 1 tries to access Resident 2's profile URL directly
        response = self.client.get(reverse('residents:resident_detail', kwargs={'resident_id': self.resident2.id}))
        # Redirected back to own dashboard with error message
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('residents:resident_dashboard'))

    def test_admin_can_access_audit_logs(self):
        """SEC-005: Administrator successfully views audit log."""
        self.client.login(username='admin_u', password='password123')
        response = self.client.get(reverse('audit:audit_list'))
        self.assertEqual(response.status_code, 200)

    def test_warden_can_access_hostel_dashboard(self):
        """SEC-006: Hostel Warden accesses primary hostel dashboard."""
        self.client.login(username='warden_u', password='password123')
        response = self.client.get(reverse('accounts:hostel_dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Hostel Management")
