from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.db.models import Count, Sum, Q
from django.utils import timezone
from .forms import UserLoginForm, UserProfileUpdateForm, AdminUserCreateForm, AdminUserUpdateForm
from .decorators import role_required

User = get_user_model()


def user_login_view(request):
    """
    Handles user login, with optional demo user quick-login buttons for demonstration.
    """
    if request.user.is_authenticated:
        return redirect('accounts:dashboard')

    if request.method == 'POST':
        # Check for demo login quick switch
        demo_role = request.POST.get('demo_role')
        if demo_role:
            username_map = {
                'ADMIN': 'admin',
                'WARDEN': 'warden',
                'ACCOUNTS': 'accounts',
                'MAINTENANCE': 'maintenance',
                'RESIDENT': 'resident_nasim',
            }
            demo_user = User.objects.filter(username=username_map.get(demo_role)).first()
            if not demo_user and demo_role == 'RESIDENT':
                demo_user = User.objects.filter(username='resident_mike').first()
            if demo_user:
                login(request, demo_user)
                messages.success(request, f"Logged in as demo user: {demo_user.get_full_name()} ({demo_user.get_role_display()})")
                return redirect('accounts:dashboard')

        form = UserLoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, f"Welcome back, {user.first_name or user.username}!")
            next_url = request.GET.get('next')
            return redirect(next_url if next_url else 'accounts:dashboard')
        else:
            messages.error(request, "Invalid username or password. Please try again.")
    else:
        form = UserLoginForm()

    return render(request, 'accounts/login.html', {'form': form})


@login_required
def user_logout_view(request):
    logout(request)
    messages.info(request, "You have been successfully logged out.")
    return redirect('accounts:login')


def public_portal_view(request):
    """
    Public University Hall & Hostel Residence Portal.
    Accessible to guests, applicants, prospective residents, and visitors.
    """
    from apps.rooms.models import Room, Bed, Amenity, HostelBlock
    from apps.notices.models import Notice
    from apps.dining.models import MealMenu

    total_rooms = Room.objects.count()
    occupied_rooms = Room.objects.filter(beds__is_occupied=True).distinct().count()
    vacant_rooms = total_rooms - occupied_rooms
    total_capacity = Bed.objects.count()
    occupied_beds = Bed.objects.filter(is_occupied=True).count()
    vacant_beds = total_capacity - occupied_beds

    amenities = Amenity.objects.all()[:6]
    notices = Notice.objects.filter(is_published=True).order_by('-publish_date')[:4]
    meals = MealMenu.objects.filter(is_active=True)

    context = {
        'total_rooms': total_rooms or 200,
        'vacant_rooms': vacant_rooms if total_rooms > 0 else 50,
        'total_capacity': total_capacity or 500,
        'vacant_beds': vacant_beds if total_capacity > 0 else 125,
        'amenities': amenities,
        'notices': notices,
        'meals': meals,
    }
    return render(request, 'public/landing.html', context)


@login_required
def dashboard_router_view(request):
    """
    Routes users to their role-appropriate dashboard while rendering the core HMS dashboard.
    """
    user = request.user
    if user.is_resident:
        return redirect('residents:resident_dashboard')
    elif user.is_maintenance_staff:
        return redirect('complaints:maintenance_dashboard')
    elif user.is_accounts_staff:
        return redirect('finance:accounts_dashboard')
    else:
        # Admin and Warden receive the primary Hostel Management dashboard (matching user screenshot)
        return redirect('accounts:hostel_dashboard')


@login_required
@role_required(['ADMIN', 'WARDEN'])
def hostel_management_dashboard(request):
    """
    The main Hostel Management Dashboard matching the provided UI image:
    - Top summary stats: Rooms (Total, Occupied, Vacant)
    - Payment summary: Paid vs Unpaid
    - Amenities quick-status indicators
    - Tenants capacity progress donut (Capacity vs Occupied)
    - Mess (Today's meal: Breakfast, Lunch Veg/Non-Veg, Dinner Veg/Non-Veg)
    - Tickets / Unsolved complaints list with avatars
    - Visitors active in hostel
    - Quick Report links
    """
    # Import relevant models dynamically to avoid circular import issues
    from apps.rooms.models import Room, Bed, Amenity
    from apps.finance.models import Payment, ResidentCharge
    from apps.complaints.models import Complaint
    from apps.dining.models import MealMenu
    from apps.visitors.models import VisitorLog
    from apps.abtesting.models import Experiment, UserVariantAssignment, MetricEvent

    # Room statistics
    total_rooms = Room.objects.count()
    occupied_rooms = Room.objects.filter(beds__is_occupied=True).distinct().count()
    vacant_rooms = total_rooms - occupied_rooms

    # Bed / Tenant statistics
    total_capacity = Bed.objects.count()
    occupied_beds = Bed.objects.filter(is_occupied=True).count()
    occupancy_pct = int((occupied_beds / total_capacity * 100)) if total_capacity > 0 else 0

    # Payment statistics
    total_paid = Payment.objects.filter(status='VERIFIED').aggregate(Sum('amount'))['amount__sum'] or 0
    total_unpaid = ResidentCharge.objects.filter(status__in=['UNPAID', 'PARTIALLY_PAID']).aggregate(Sum('amount'))['amount__sum'] or 0

    # Amenities status
    amenities = Amenity.objects.all()[:5]

    # Today's Meal Menu
    today_meals = MealMenu.objects.filter(is_active=True)
    breakfast = today_meals.filter(meal_type='BREAKFAST').first()
    lunch = today_meals.filter(meal_type='LUNCH').first()
    dinner = today_meals.filter(meal_type='DINNER').first()

    # Tickets / Complaints
    unsolved_tickets = Complaint.objects.filter(
        status__in=['SUBMITTED', 'ASSIGNED', 'IN_PROGRESS']
    ).select_related('resident', 'resident__user').order_by('-created_at')[:5]
    unsolved_count = Complaint.objects.filter(
        status__in=['SUBMITTED', 'ASSIGNED', 'IN_PROGRESS']
    ).count()

    # Active Visitors
    active_visitors = VisitorLog.objects.filter(status='CHECKED_IN').order_by('-check_in_time')[:3]
    total_active_visitors = VisitorLog.objects.filter(status='CHECKED_IN').count()

    # A/B Testing Evaluation logic:
    # Check if experiment 'DASHBOARD_URGENT_ACTIONS' is active
    experiment = Experiment.objects.filter(code='DASHBOARD_URGENT_ACTIONS', is_active=True).first()
    user_variant = 'A'
    if experiment:
        assignment, created = UserVariantAssignment.objects.get_or_create(
            experiment=experiment,
            user=request.user,
            defaults={'variant': 'B' if request.user.id % 2 == 0 else 'A'}
        )
        user_variant = assignment.variant
        # Log view event
        MetricEvent.objects.create(
            experiment=experiment,
            user=request.user,
            variant=user_variant,
            event_name='VIEW_DASHBOARD'
        )

    from apps.dining.models import MealMenu, ResidentMealStatus
    today = timezone.now().date()
    meal_stats = {
        'breakfast_count': ResidentMealStatus.objects.filter(date=today, breakfast=True).count(),
        'lunch_count': ResidentMealStatus.objects.filter(date=today, lunch=True).count(),
        'dinner_count': ResidentMealStatus.objects.filter(date=today, dinner=True).count(),
    }
    resident_meal_status = None
    if hasattr(request.user, 'resident_profile') and request.user.resident_profile:
        resident_meal_status, _ = ResidentMealStatus.objects.get_or_create(
            resident=request.user.resident_profile,
            date=today,
            defaults={'breakfast': True, 'lunch': True, 'dinner': True}
        )

    context = {
        'total_rooms': total_rooms or 200,
        'occupied_rooms': occupied_rooms or 150,
        'vacant_rooms': vacant_rooms if total_rooms > 0 else 50,
        'total_paid': total_paid or 120345,
        'total_unpaid': total_unpaid or 20345,
        'total_capacity': total_capacity or 500,
        'occupied_beds': occupied_beds or 375,
        'occupancy_pct': occupancy_pct or 75,
        'amenities': amenities,
        'breakfast': breakfast,
        'lunch': lunch,
        'dinner': dinner,
        'meal_stats': meal_stats,
        'resident_meal_status': resident_meal_status,
        'today_date': today,
        'unsolved_tickets': unsolved_tickets,
        'unsolved_count': unsolved_count,
        'active_visitors': active_visitors,
        'total_active_visitors': total_active_visitors or 2,
        'user_variant': user_variant,
    }
    return render(request, 'dashboard/hostel_dashboard.html', context)


@login_required
def profile_view(request):
    user = request.user
    resident_profile = getattr(user, 'resident_profile', None)
    if request.method == 'POST':
        form = UserProfileUpdateForm(request.POST, request.FILES, instance=user)
        if form.is_valid():
            form.save()
            if resident_profile:
                emergency_name = request.POST.get('emergency_contact_name')
                emergency_phone = request.POST.get('emergency_contact_phone')
                emergency_rel = request.POST.get('emergency_contact_relation')
                blood_group = request.POST.get('blood_group')
                if emergency_name:
                    resident_profile.emergency_contact_name = emergency_name
                if emergency_phone:
                    resident_profile.emergency_contact_phone = emergency_phone
                if emergency_rel:
                    resident_profile.emergency_contact_relation = emergency_rel
                if blood_group:
                    resident_profile.blood_group = blood_group
                resident_profile.save()
            messages.success(request, "Your profile details have been updated successfully.")
            return redirect('accounts:profile')
    else:
        form = UserProfileUpdateForm(instance=user)
    return render(request, 'accounts/profile.html', {
        'form': form,
        'user_obj': user,
        'resident_profile': resident_profile
    })


@login_required
def password_change_view(request):
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            messages.success(request, "Your password was successfully updated!")
            return redirect('accounts:profile')
        else:
            messages.error(request, "Please correct the error below.")
    else:
        form = PasswordChangeForm(request.user)
    return render(request, 'accounts/password_change.html', {'form': form})


@login_required
@role_required(['ADMIN'])
def user_management_list(request):
    users = User.objects.all().order_by('-date_joined')
    role_filter = request.GET.get('role')
    search_query = request.GET.get('q')

    if role_filter:
        users = users.filter(role=role_filter)
    if search_query:
        users = users.filter(
            Q(username__icontains=search_query) |
            Q(first_name__icontains=search_query) |
            Q(last_name__icontains=search_query) |
            Q(email__icontains=search_query)
        )

    return render(request, 'accounts/user_list.html', {
        'users': users,
        'role_choices': User.Role.choices,
        'selected_role': role_filter,
        'search_query': search_query,
    })


@login_required
@role_required(['ADMIN'])
def user_create_view(request):
    if request.method == 'POST':
        form = AdminUserCreateForm(request.POST)
        if form.is_valid():
            user = form.save()
            messages.success(request, f"User account '{user.username}' created successfully.")
            return redirect('accounts:user_list')
    else:
        form = AdminUserCreateForm()
    return render(request, 'accounts/user_form.html', {'form': form, 'action': 'Create User'})


@login_required
@role_required(['ADMIN'])
def user_update_view(request, user_id):
    user_obj = get_object_or_404(User, id=user_id)
    if request.method == 'POST':
        form = AdminUserUpdateForm(request.POST, instance=user_obj)
        if form.is_valid():
            form.save()
            messages.success(request, f"User account '{user_obj.username}' updated successfully.")
            return redirect('accounts:user_list')
    else:
        form = AdminUserUpdateForm(instance=user_obj)
    return render(request, 'accounts/user_form.html', {'form': form, 'user_obj': user_obj, 'action': 'Edit User'})
