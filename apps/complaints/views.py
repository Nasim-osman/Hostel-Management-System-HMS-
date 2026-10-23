from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.db.models import Q, Count
import uuid

from apps.accounts.decorators import role_required, resident_access_only
from .models import Complaint
from .forms import ResidentComplaintForm, ComplaintAssignmentForm, ComplaintResolutionForm


@login_required
def complaint_list_view(request):
    if request.user.is_resident:
        resident = getattr(request.user, 'resident_profile', None)
        complaints = Complaint.objects.filter(resident=resident)
    elif request.user.is_maintenance_staff:
        complaints = Complaint.objects.filter(assigned_to=request.user)
    else:
        complaints = Complaint.objects.select_related('resident', 'resident__user', 'assigned_to', 'room').all()

    # Filters
    status_filter = request.GET.get('status')
    category_filter = request.GET.get('category')
    priority_filter = request.GET.get('priority')
    search_q = request.GET.get('q')

    if status_filter:
        complaints = complaints.filter(status=status_filter)
    if category_filter:
        complaints = complaints.filter(category=category_filter)
    if priority_filter:
        complaints = complaints.filter(priority=priority_filter)
    if search_q:
        complaints = complaints.filter(
            Q(ticket_number__icontains=search_q) |
            Q(title__icontains=search_q) |
            Q(description__icontains=search_q) |
            Q(resident__student_id__icontains=search_q)
        )

    return render(request, 'complaints/complaint_list.html', {
        'complaints': complaints,
        'status_choices': Complaint.Status.choices,
        'category_choices': Complaint.Category.choices,
        'priority_choices': Complaint.Priority.choices,
        'selected_status': status_filter,
        'selected_category': category_filter,
        'selected_priority': priority_filter,
        'search_q': search_q,
    })


@login_required
def complaint_detail_view(request, ticket_id):
    complaint = get_object_or_404(
        Complaint.objects.select_related('resident', 'resident__user', 'assigned_to', 'room'),
        id=ticket_id
    )

    if request.user.is_resident and complaint.resident.user != request.user:
        messages.error(request, "Permission denied: You can only view your own complaints.")
        return redirect('complaints:complaint_list')

    assignment_form = None
    resolution_form = None

    if request.user.is_warden or request.user.is_admin_user:
        assignment_form = ComplaintAssignmentForm(instance=complaint)
    if request.user.is_maintenance_staff or request.user.is_warden or request.user.is_admin_user:
        resolution_form = ComplaintResolutionForm(instance=complaint)

    return render(request, 'complaints/complaint_detail.html', {
        'complaint': complaint,
        'assignment_form': assignment_form,
        'resolution_form': resolution_form,
    })


@login_required
@resident_access_only
def submit_complaint_view(request):
    resident = getattr(request.user, 'resident_profile', None)
    if not resident:
        messages.error(request, "Resident profile required to log a maintenance ticket.")
        return redirect('accounts:dashboard')

    if request.method == 'POST':
        form = ResidentComplaintForm(request.POST)
        if form.is_valid():
            complaint = form.save(commit=False)
            complaint.resident = resident
            complaint.room = resident.current_room
            complaint.ticket_number = f"HMS-TICK-{timezone.now().strftime('%Y%m')}-{uuid.uuid4().hex[:5].upper()}"
            complaint.save()
            messages.success(request, f"Maintenance ticket #{complaint.ticket_number} created.")
            return redirect('complaints:complaint_list')
    else:
        form = ResidentComplaintForm()

    return render(request, 'complaints/submit_complaint.html', {'form': form, 'current_room': resident.current_room})


@login_required
@role_required(['ADMIN', 'WARDEN'])
def assign_complaint_view(request, ticket_id):
    complaint = get_object_or_404(Complaint, id=ticket_id)
    if request.method == 'POST':
        form = ComplaintAssignmentForm(request.POST, instance=complaint)
        if form.is_valid():
            comp = form.save(commit=False)
            comp.status = Complaint.Status.ASSIGNED
            comp.save()
            messages.success(request, f"Ticket #{comp.ticket_number} assigned to {comp.assigned_to.get_full_name()}.")
    return redirect('complaints:complaint_detail', ticket_id=complaint.id)


@login_required
@role_required(['ADMIN', 'WARDEN', 'MAINTENANCE'])
def resolve_complaint_view(request, ticket_id):
    complaint = get_object_or_404(Complaint, id=ticket_id)
    if request.method == 'POST':
        form = ComplaintResolutionForm(request.POST, instance=complaint)
        if form.is_valid():
            comp = form.save(commit=False)
            if comp.status == Complaint.Status.RESOLVED:
                comp.resolved_at = timezone.now()
            comp.save()
            messages.success(request, f"Ticket #{comp.ticket_number} updated to {comp.get_status_display()}.")
    return redirect('complaints:complaint_detail', ticket_id=complaint.id)


@login_required
@role_required(['MAINTENANCE'])
def maintenance_dashboard_view(request):
    assigned_tickets = Complaint.objects.filter(assigned_to=request.user).order_by('-created_at')
    open_count = assigned_tickets.filter(status__in=['ASSIGNED', 'IN_PROGRESS']).count()
    resolved_count = assigned_tickets.filter(status__in=['RESOLVED', 'CLOSED']).count()

    context = {
        'assigned_tickets': assigned_tickets,
        'open_count': open_count,
        'resolved_count': resolved_count,
    }
    return render(request, 'complaints/maintenance_dashboard.html', context)
