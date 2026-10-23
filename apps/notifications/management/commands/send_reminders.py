from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from apps.finance.models import ResidentCharge
from apps.allocations.models import SeatApplication
from apps.complaints.models import Complaint
from apps.attendance.models import OutpassRequest
from apps.notifications.models import notify_user, InAppNotification
from django.contrib.auth import get_user_model

User = get_user_model()


class Command(BaseCommand):
    help = 'Executes automated reminder workflows for fees, overdue outpasses, pending applications, and tickets.'

    def handle(self, *args, **options):
        now = timezone.now()
        today = now.date()
        reminders_sent = 0

        self.stdout.write("Running HMS Automated Reminder Service...")

        # 1. Overdue & Upcoming Fees (due within 3 days or already overdue)
        three_days_ahead = today + timedelta(days=3)
        unpaid_charges = ResidentCharge.objects.filter(
            status__in=['UNPAID', 'PARTIALLY_PAID'],
            due_date__lte=three_days_ahead
        ).select_related('resident', 'resident__user')

        for charge in unpaid_charges:
            user = charge.resident.user
            # Avoid sending identical reminder within 24 hours
            recent_remind = InAppNotification.objects.filter(
                recipient=user,
                notification_type=InAppNotification.NotificationType.FEE_DUE,
                created_at__gte=now - timedelta(hours=24)
            ).exists()

            if not recent_remind:
                due_status = "OVERDUE" if charge.due_date < today else f"due on {charge.due_date}"
                notify_user(
                    recipient=user,
                    title=f"Fee Reminder: {charge.description}",
                    message=f"Your charge of ₹{charge.balance_remaining} is {due_status}. Please settle dues promptly.",
                    notification_type=InAppNotification.NotificationType.FEE_DUE,
                    link="/finance/fees/"
                )
                reminders_sent += 1

        # 2. Overdue Outpasses (expected return passed, status still DEPARTED or APPROVED)
        overdue_outpasses = OutpassRequest.objects.filter(
            status__in=['DEPARTED', 'APPROVED'],
            expected_return_time__lt=now
        ).select_related('resident', 'resident__user')

        wardens = User.objects.filter(role=User.Role.WARDEN)

        for outpass in overdue_outpasses:
            outpass.status = OutpassRequest.Status.OVERDUE
            outpass.save()

            for warden in wardens:
                notify_user(
                    recipient=warden,
                    title=f"ALERT: Overdue Outpass - {outpass.resident.student_id}",
                    message=f"Resident {outpass.resident.user.get_full_name()} was expected to return at {outpass.expected_return_time.strftime('%I:%M %p')}. Contact: {outpass.parent_contact}.",
                    notification_type=InAppNotification.NotificationType.OUTPASS,
                    link="/attendance/outpasses/"
                )
                reminders_sent += 1

        # 3. Pending Seat Applications (older than 48 hours)
        old_pending_apps = SeatApplication.objects.filter(
            status=SeatApplication.Status.PENDING,
            applied_at__lt=now - timedelta(hours=48)
        )
        if old_pending_apps.exists():
            for warden in wardens:
                notify_user(
                    recipient=warden,
                    title="Pending Seat Applications Awaiting Review",
                    message=f"There are {old_pending_apps.count()} pending seat applications waiting for review.",
                    notification_type=InAppNotification.NotificationType.APPLICATION,
                    link="/allocations/applications/"
                )
                reminders_sent += 1

        # 4. Unassigned High/Urgent Priority Tickets
        urgent_tickets = Complaint.objects.filter(
            status=Complaint.Status.SUBMITTED,
            priority__in=['HIGH', 'URGENT']
        )
        if urgent_tickets.exists():
            for warden in wardens:
                notify_user(
                    recipient=warden,
                    title=f"Urgent Complaint Pending Assignment ({urgent_tickets.count()})",
                    message="Urgent maintenance tickets require immediate assignment to maintenance staff.",
                    notification_type=InAppNotification.NotificationType.COMPLAINT,
                    link="/complaints/"
                )
                reminders_sent += 1

        self.stdout.write(self.style.SUCCESS(f"Successfully processed reminders. Total notifications created: {reminders_sent}"))
