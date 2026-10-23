from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from apps.accounts.decorators import role_required, resident_access_only
from apps.residents.models import ResidentProfile
from .models import AttendanceRecord, OutpassRequest
from .forms import OutpassRequestForm


@login_required
def attendance_overview_view(request):
    today = timezone.now().date()
    records = AttendanceRecord.objects.filter(date=today).select_related('resident', 'resident__user')
    total_residents = ResidentProfile.objects.filter(status='ACTIVE').count()
    present_count = records.filter(status='PRESENT').count()
    outpass_count = records.filter(status='OUTPASS').count()
    absent_count = records.filter(status='ABSENT').count()

    return render(request, 'attendance/attendance_overview.html', {
        'today': today,
        'records': records,
        'total_residents': total_residents,
        'present_count': present_count,
        'outpass_count': outpass_count,
        'absent_count': absent_count,
    })


@login_required
@role_required(['ADMIN', 'WARDEN'])
def mark_attendance_view(request):
    today = timezone.now().date()
    residents = ResidentProfile.objects.filter(status='ACTIVE').select_related('user', 'current_bed', 'current_bed__room')

    if request.method == 'POST':
        for res in residents:
            status_val = request.POST.get(f'status_{res.id}', 'PRESENT')
            remarks = request.POST.get(f'remarks_{res.id}', '')
            AttendanceRecord.objects.update_or_create(
                resident=res,
                date=today,
                defaults={
                    'status': status_val,
                    'remarks': remarks,
                    'marked_by': request.user
                }
            )
        messages.success(request, f"Daily attendance recorded for {today}.")
        return redirect('attendance:attendance_overview')

    # Existing records for today
    existing = {rec.resident_id: rec.status for rec in AttendanceRecord.objects.filter(date=today)}
    return render(request, 'attendance/mark_attendance.html', {
        'today': today,
        'residents': residents,
        'existing': existing,
    })


@login_required
def outpass_list_view(request):
    if request.user.is_resident:
        resident = getattr(request.user, 'resident_profile', None)
        outpasses = OutpassRequest.objects.filter(resident=resident).order_by('-created_at')
    else:
        outpasses = OutpassRequest.objects.select_related('resident', 'resident__user').order_by('-created_at')
        status_filter = request.GET.get('status')
        if status_filter:
            outpasses = outpasses.filter(status=status_filter)

    return render(request, 'attendance/outpass_list.html', {
        'outpasses': outpasses,
        'status_choices': OutpassRequest.Status.choices,
        'selected_status': request.GET.get('status'),
    })


@login_required
@resident_access_only
def request_outpass_view(request):
    resident = getattr(request.user, 'resident_profile', None)
    if not resident:
        messages.error(request, "Resident profile required.")
        return redirect('accounts:dashboard')

    if request.method == 'POST':
        form = OutpassRequestForm(request.POST)
        if form.is_valid():
            req = form.save(commit=False)
            req.resident = resident
            req.save()
            messages.success(request, "Outpass request submitted for Warden review.")
            return redirect('attendance:outpass_list')
    else:
        form = OutpassRequestForm()
    return render(request, 'attendance/request_outpass.html', {'form': form})


@login_required
@role_required(['ADMIN', 'WARDEN'])
def approve_outpass_view(request, outpass_id):
    outpass = get_object_or_404(OutpassRequest, id=outpass_id)
    if request.method == 'POST':
        action = request.POST.get('action')
        remarks = request.POST.get('remarks', '')
        outpass.approved_by = request.user
        outpass.remarks = remarks
        if action == 'approve':
            outpass.status = OutpassRequest.Status.APPROVED
            messages.success(request, f"Outpass #{outpass.id} approved.")
        elif action == 'reject':
            outpass.status = OutpassRequest.Status.REJECTED
            messages.info(request, f"Outpass #{outpass.id} rejected.")
        elif action == 'depart':
            outpass.status = OutpassRequest.Status.DEPARTED
            messages.info(request, f"Departure confirmed for {outpass.resident.student_id}.")
        elif action == 'return':
            outpass.status = OutpassRequest.Status.RETURNED
            outpass.actual_return_time = timezone.now()
            messages.success(request, f"Safe return recorded for {outpass.resident.student_id}.")
        outpass.save()
    return redirect('attendance:outpass_list')
