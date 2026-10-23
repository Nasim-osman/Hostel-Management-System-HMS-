import csv
from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseForbidden
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.db.models import Count, Sum, Q

from apps.accounts.decorators import role_required, staff_access_only
from apps.audit.models import log_audit
from apps.residents.models import ResidentProfile
from apps.rooms.models import Room, Bed
from apps.finance.models import Payment, ResidentCharge, HostelExpense
from apps.complaints.models import Complaint
from apps.visitors.models import VisitorLog
from apps.notices.models import Notice


@login_required
@staff_access_only
def reports_overview_view(request):
    """
    Hostel analytical reports overview.
    """
    total_rooms = Room.objects.count()
    total_beds = Bed.objects.count()
    occupied_beds = Bed.objects.filter(is_occupied=True).count()
    vacant_beds = total_beds - occupied_beds

    total_fees_collected = Payment.objects.filter(status='VERIFIED').aggregate(Sum('amount'))['amount__sum'] or 0
    total_pending_dues = ResidentCharge.objects.filter(status__in=['UNPAID', 'PARTIALLY_PAID']).aggregate(Sum('amount'))['amount__sum'] or 0

    total_tickets = Complaint.objects.count()
    resolved_tickets = Complaint.objects.filter(status__in=['RESOLVED', 'CLOSED']).count()

    context = {
        'total_rooms': total_rooms,
        'total_beds': total_beds,
        'occupied_beds': occupied_beds,
        'vacant_beds': vacant_beds,
        'total_fees_collected': total_fees_collected,
        'total_pending_dues': total_pending_dues,
        'total_tickets': total_tickets,
        'resolved_tickets': resolved_tickets,
    }
    return render(request, 'reports/reports_overview.html', context)


@login_required
@staff_access_only
def export_data_csv_view(request, export_type):
    """
    Authorized CSV Export for reporting and compliance with strict audit logging.
    """
    timestamp = timezone.now().strftime('%Y%m%d_%H%M%S')
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="HMS_Export_{export_type}_{timestamp}.csv"'
    writer = csv.writer(response)

    user = request.user

    if export_type == 'residents':
        if not (user.is_admin_user or user.is_warden):
            return HttpResponseForbidden("Permission denied.")
        writer.writerow(['Resident ID', 'First Name', 'Last Name', 'Email', 'Phone', 'Course', 'Gender', 'Status', 'Room', 'Bed', 'Admission Date'])
        for r in ResidentProfile.objects.select_related('user', 'current_bed', 'current_bed__room').all():
            bed_str = str(r.current_bed.bed_number) if r.current_bed else 'N/A'
            room_str = str(r.current_bed.room.room_number) if r.current_bed else 'N/A'
            writer.writerow([r.student_id, r.user.first_name, r.user.last_name, r.user.email, r.user.phone_number or '', r.course, r.get_gender_display(), r.get_status_display(), room_str, bed_str, r.admission_date or ''])

    elif export_type == 'rooms':
        writer.writerow(['Block', 'Room Number', 'Floor', 'Room Type', 'Capacity', 'Occupied Beds', 'Available Beds', 'Status'])
        for rm in Room.objects.select_related('block').prefetch_related('beds').all():
            writer.writerow([rm.block.name, rm.room_number, rm.floor, rm.get_room_type_display(), rm.capacity, rm.occupied_beds_count, rm.available_beds_count, 'Active' if rm.is_active else 'Inactive'])

    elif export_type == 'payments':
        if not (user.is_admin_user or user.is_accounts_staff or user.is_warden):
            return HttpResponseForbidden("Permission denied.")
        writer.writerow(['Receipt No', 'Resident ID', 'Resident Name', 'Amount (₹)', 'Date', 'Method', 'Reference', 'Status', 'Verified By'])
        for p in Payment.objects.select_related('resident', 'resident__user', 'verified_by').all():
            verifier = p.verified_by.get_full_name() if p.verified_by else 'N/A'
            writer.writerow([p.receipt_number, p.resident.student_id, p.resident.user.get_full_name(), p.amount, p.payment_date, p.get_payment_method_display(), p.transaction_reference, p.get_status_display(), verifier])

    elif export_type == 'complaints':
        writer.writerow(['Ticket No', 'Title', 'Category', 'Priority', 'Status', 'Resident ID', 'Room', 'Assigned To', 'Created Date', 'Resolved Date'])
        for c in Complaint.objects.select_related('resident', 'room', 'assigned_to').all():
            assigned = c.assigned_to.get_full_name() if c.assigned_to else 'Unassigned'
            room_str = str(c.room.room_number) if c.room else 'N/A'
            writer.writerow([c.ticket_number, c.title, c.get_category_display(), c.get_priority_display(), c.get_status_display(), c.resident.student_id, room_str, assigned, c.created_at.strftime('%Y-%m-%d'), c.resolved_at.strftime('%Y-%m-%d') if c.resolved_at else 'N/A'])

    elif export_type == 'visitors':
        writer.writerow(['Visitor Name', 'Phone', 'Resident ID', 'Destination', 'Purpose', 'Check In Time', 'Check Out Time', 'Status', 'Gate Pass'])
        for v in VisitorLog.objects.select_related('resident').all():
            writer.writerow([v.visitor_name, v.visitor_phone, v.resident.student_id, v.destination, v.purpose, v.check_in_time.strftime('%Y-%m-%d %H:%M'), v.check_out_time.strftime('%Y-%m-%d %H:%M') if v.check_out_time else 'N/A', v.get_status_display(), v.gate_pass_no])

    elif export_type == 'expenses':
        if not (user.is_admin_user or user.is_accounts_staff):
            return HttpResponseForbidden("Permission denied.")
        writer.writerow(['Date', 'Category', 'Title', 'Payee', 'Amount (₹)', 'Invoice No', 'Recorded By'])
        for e in HostelExpense.objects.select_related('recorded_by').all():
            writer.writerow([e.expense_date, e.get_category_display(), e.title, e.payee, e.amount, e.invoice_number, e.recorded_by.get_full_name() or e.recorded_by.username])

    else:
        return HttpResponse("Invalid export type.", status=400)

    # Log audit event
    log_audit(
        actor=user,
        action='EXPORT',
        module='Reports',
        target_repr=f"Exported {export_type} CSV",
        ip_address=request.META.get('REMOTE_ADDR')
    )

    return response


@login_required
def global_search_view(request):
    """
    Unified global search with server-side permission filtering.
    """
    query = request.GET.get('q', '').strip()
    results = {
        'query': query,
        'residents': [],
        'rooms': [],
        'complaints': [],
        'payments': [],
        'notices': [],
        'visitors': [],
    }

    if query:
        # Search rooms (all authenticated users)
        results['rooms'] = Room.objects.filter(
            Q(room_number__icontains=query) | Q(block__name__icontains=query)
        ).select_related('block')[:5]

        # Search notices
        results['notices'] = Notice.objects.filter(
            Q(title__icontains=query) | Q(content__icontains=query)
        )[:5]

        # Search complaints
        if request.user.is_resident:
            results['complaints'] = Complaint.objects.filter(
                resident__user=request.user
            ).filter(Q(ticket_number__icontains=query) | Q(title__icontains=query))[:5]
        else:
            results['complaints'] = Complaint.objects.filter(
                Q(ticket_number__icontains=query) | Q(title__icontains=query) | Q(resident__student_id__icontains=query)
            ).select_related('resident')[:5]

        # Staff only searches
        if request.user.is_staff_member:
            results['residents'] = ResidentProfile.objects.filter(
                Q(student_id__icontains=query) |
                Q(user__first_name__icontains=query) |
                Q(user__last_name__icontains=query) |
                Q(course__icontains=query)
            ).select_related('user')[:5]

            results['visitors'] = VisitorLog.objects.filter(
                Q(visitor_name__icontains=query) | Q(destination__icontains=query) | Q(gate_pass_no__icontains=query)
            )[:5]

        if request.user.is_accounts_staff or request.user.is_admin_user:
            results['payments'] = Payment.objects.filter(
                Q(receipt_number__icontains=query) | Q(transaction_reference__icontains=query)
            )[:5]

    return render(request, 'reports/global_search_results.html', results)
