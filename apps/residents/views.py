from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q, Sum
from django.utils import timezone
from apps.accounts.decorators import role_required, warden_or_admin_only, resident_access_only
from .models import ResidentProfile
from .forms import ResidentRegistrationForm, ResidentUpdateForm


@login_required
@role_required(['ADMIN', 'WARDEN', 'ACCOUNTS'])
def resident_list_view(request):
    residents = ResidentProfile.objects.select_related('user', 'current_bed', 'current_bed__room', 'current_bed__room__block').all()
    
    status_filter = request.GET.get('status')
    gender_filter = request.GET.get('gender')
    search_q = request.GET.get('q')

    if status_filter:
        residents = residents.filter(status=status_filter)
    if gender_filter:
        residents = residents.filter(gender=gender_filter)
    if search_q:
        residents = residents.filter(
            Q(student_id__icontains=search_q) |
            Q(user__first_name__icontains=search_q) |
            Q(user__last_name__icontains=search_q) |
            Q(user__email__icontains=search_q) |
            Q(course__icontains=search_q)
        )

    total_residents = ResidentProfile.objects.count()
    active_count = ResidentProfile.objects.filter(status='ACTIVE').count()
    applicant_count = ResidentProfile.objects.filter(status='APPLICANT').count()

    context = {
        'residents': residents,
        'status_choices': ResidentProfile.Status.choices,
        'selected_status': status_filter,
        'selected_gender': gender_filter,
        'search_q': search_q,
        'total_residents': total_residents,
        'active_count': active_count,
        'applicant_count': applicant_count,
    }
    return render(request, 'residents/resident_list.html', context)


@login_required
def resident_detail_view(request, resident_id):
    resident = get_object_or_404(
        ResidentProfile.objects.select_related('user', 'current_bed', 'current_bed__room', 'current_bed__room__block'),
        id=resident_id
    )

    # Permission check: Residents may ONLY view their own profile
    if request.user.is_resident and request.user != resident.user:
        messages.error(request, "Permission denied: You can only view your own profile.")
        return redirect('residents:resident_dashboard')

    # Fetch resident related records
    from apps.finance.models import ResidentCharge, Payment
    from apps.complaints.models import Complaint
    from apps.attendance.models import OutpassRequest

    charges = ResidentCharge.objects.filter(resident=resident).order_by('-due_date')
    payments = Payment.objects.filter(resident=resident).order_by('-payment_date')
    complaints = Complaint.objects.filter(resident=resident).order_by('-created_at')
    outpasses = OutpassRequest.objects.filter(resident=resident).order_by('-departure_time')

    total_charged = charges.aggregate(Sum('amount'))['amount__sum'] or 0
    total_paid = payments.filter(status='VERIFIED').aggregate(Sum('amount'))['amount__sum'] or 0
    balance_due = max(0, total_charged - total_paid)

    context = {
        'resident': resident,
        'charges': charges,
        'payments': payments,
        'complaints': complaints,
        'outpasses': outpasses,
        'total_charged': total_charged,
        'total_paid': total_paid,
        'balance_due': balance_due,
    }
    return render(request, 'residents/resident_detail.html', context)


@login_required
@warden_or_admin_only
def resident_create_view(request):
    if request.method == 'POST':
        form = ResidentRegistrationForm(request.POST)
        if form.is_valid():
            resident = form.save()
            messages.success(request, f"Resident {resident.user.get_full_name()} ({resident.student_id}) registered successfully.")
            return redirect('residents:resident_detail', resident_id=resident.id)
    else:
        form = ResidentRegistrationForm()
    return render(request, 'residents/resident_form.html', {'form': form, 'action': 'Register Resident'})


@login_required
@warden_or_admin_only
def resident_edit_view(request, resident_id):
    resident = get_object_or_404(ResidentProfile, id=resident_id)
    if request.method == 'POST':
        form = ResidentUpdateForm(request.POST, instance=resident)
        if form.is_valid():
            form.save()
            messages.success(request, f"Resident record for {resident.student_id} updated successfully.")
            return redirect('residents:resident_detail', resident_id=resident.id)
    else:
        form = ResidentUpdateForm(instance=resident)
    return render(request, 'residents/resident_form.html', {'form': form, 'resident': resident, 'action': 'Edit Resident'})


@login_required
@resident_access_only
def resident_dashboard_view(request):
    """
    Personal self-service dashboard for authenticated residents.
    """
    resident = getattr(request.user, 'resident_profile', None)
    if not resident:
        messages.warning(request, "Resident profile not found. Please contact administration.")
        return render(request, 'residents/resident_dashboard_empty.html')

    from apps.finance.models import ResidentCharge, Payment
    from apps.complaints.models import Complaint
    from apps.attendance.models import OutpassRequest
    from apps.dining.models import MealMenu
    from apps.notices.models import Notice

    charges = ResidentCharge.objects.filter(resident=resident).order_by('-due_date')[:5]
    payments = Payment.objects.filter(resident=resident).order_by('-payment_date')[:5]
    complaints = Complaint.objects.filter(resident=resident).order_by('-created_at')[:5]
    outpasses = OutpassRequest.objects.filter(resident=resident).order_by('-departure_time')[:5]
    
    total_charged = ResidentCharge.objects.filter(resident=resident).aggregate(Sum('amount'))['amount__sum'] or 0
    total_paid = Payment.objects.filter(resident=resident, status='VERIFIED').aggregate(Sum('amount'))['amount__sum'] or 0
    balance_due = max(0, total_charged - total_paid)

    from apps.dining.models import MealMenu, ResidentMealStatus
    today = timezone.now().date()
    meal_status, _ = ResidentMealStatus.objects.get_or_create(
        resident=resident,
        date=today,
        defaults={'breakfast': True, 'lunch': True, 'dinner': True}
    )
    today_meals = MealMenu.objects.filter(is_active=True)
    recent_notices = Notice.objects.filter(is_published=True).order_by('-publish_date')[:4]

    context = {
        'resident': resident,
        'charges': charges,
        'payments': payments,
        'complaints': complaints,
        'outpasses': outpasses,
        'total_charged': total_charged,
        'total_paid': total_paid,
        'balance_due': balance_due,
        'today_meals': today_meals,
        'meal_status': meal_status,
        'today_date': today,
        'recent_notices': recent_notices,
    }
    return render(request, 'residents/resident_dashboard.html', context)
