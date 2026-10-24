from django.contrib.auth import login, get_user_model
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.exceptions import ValidationError
from django.utils import timezone
from apps.accounts.decorators import role_required, warden_or_admin_only, resident_access_only
from apps.rooms.models import Room, Bed
from apps.residents.models import ResidentProfile
from .models import SeatApplication, SeatAllocation, WaitingListEntry, RoomTransferRequest, CheckoutClearance
from .forms import SeatApplicationForm, PublicSeatApplicationForm, RoomTransferRequestForm, CheckoutClearanceRequestForm
from .services import AllocationService

User = get_user_model()


@login_required
def application_list_view(request):
    if request.user.is_resident:
        resident = getattr(request.user, 'resident_profile', None)
        applications = SeatApplication.objects.filter(resident=resident)
    else:
        applications = SeatApplication.objects.select_related('resident', 'resident__user', 'preferred_block').all()
        status_filter = request.GET.get('status')
        if status_filter:
            applications = applications.filter(status=status_filter)

    return render(request, 'allocations/application_list.html', {
        'applications': applications,
        'status_choices': SeatApplication.Status.choices,
        'selected_status': request.GET.get('status'),
    })


def apply_seat_view(request):
    """
    Hostel Seat Application view.
    - If user is already authenticated as a resident: simple room preference form.
    - If user is a new applicant / visitor: full registration and seat application form.
    """
    if request.user.is_authenticated:
        if not request.user.is_resident:
            messages.info(request, "Staff accounts cannot submit resident seat applications.")
            return redirect('accounts:dashboard')

        resident = getattr(request.user, 'resident_profile', None)
        if not resident:
            messages.error(request, "Resident profile required to apply for a hostel seat.")
            return redirect('accounts:dashboard')

        if resident.current_bed:
            messages.info(request, f"You are already allocated to Bed: {resident.current_bed}.")
            return redirect('residents:resident_dashboard')

        if request.method == 'POST':
            form = SeatApplicationForm(request.POST)
            if form.is_valid():
                app = form.save(commit=False)
                app.resident = resident
                app.save()
                messages.success(request, f"Seat application submitted successfully (Ref: #{app.id}). The Hall Warden will review it.")
                return redirect('allocations:application_list')
        else:
            form = SeatApplicationForm()

        return render(request, 'allocations/apply_seat.html', {'form': form, 'is_public': False})

    # Unauthenticated / New Student Application Workflow
    if request.method == 'POST':
        form = PublicSeatApplicationForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            student_id = data['student_id'].strip().upper()
            email = data['email'].strip().lower()

            # Check if user already exists
            if User.objects.filter(username=student_id).exists() or User.objects.filter(email=email).exists():
                messages.error(request, f"An account with Student ID '{student_id}' or Email '{email}' already exists. Please sign in.")
                return redirect('accounts:login')

            name_parts = data['full_name'].strip().split(' ', 1)
            first_name = name_parts[0]
            last_name = name_parts[1] if len(name_parts) > 1 else 'Student'

            # 1. Create User
            user = User.objects.create(
                username=student_id,
                email=email,
                first_name=first_name,
                last_name=last_name,
                phone_number=data['phone_number'],
                role=User.Role.RESIDENT,
                is_active=True
            )
            user.set_password(data['password'])
            user.save()

            # 2. Create ResidentProfile (Pending status)
            resident = ResidentProfile.objects.create(
                user=user,
                student_id=student_id,
                course=data['course'],
                batch_year=data['batch_year'],
                gender=data['gender'],
                blood_group=data['blood_group'] or 'O+',
                emergency_contact_name=data['guardian_name'],
                emergency_contact_phone=data['guardian_phone'],
                emergency_contact_relation=data['guardian_relation'],
                status=ResidentProfile.Status.APPLICANT,
                admission_date=timezone.now().date()
            )

            # 3. Create SeatApplication
            app = SeatApplication.objects.create(
                resident=resident,
                preferred_block=data['preferred_block'],
                preferred_room_type=data['preferred_room_type'],
                academic_year=data['academic_year'],
                status=SeatApplication.Status.PENDING
            )

            # 4. Auto login
            login(request, user)
            messages.success(request, f"Congratulations {first_name}! Your hostel seat application (Ref: #{app.id}) has been submitted to the Hall Warden.")
            return redirect('allocations:application_list')
    else:
        form = PublicSeatApplicationForm()

    return render(request, 'allocations/apply_seat.html', {'form': form, 'is_public': True})


def track_application_view(request):
    """
    Public seat application tracker for any applicant or visitor.
    """
    query = request.GET.get('q', '').strip()
    application = None
    if query:
        if query.isdigit():
            application = SeatApplication.objects.filter(id=int(query)).select_related('resident', 'resident__user', 'preferred_block').first()
        if not application:
            application = SeatApplication.objects.filter(resident__student_id__iexact=query).select_related('resident', 'resident__user', 'preferred_block').first()

    return render(request, 'allocations/track_application.html', {
        'query': query,
        'application': application
    })



@login_required
@warden_or_admin_only
def review_application_view(request, app_id):
    app = get_object_or_404(SeatApplication, id=app_id)
    if request.method == 'POST':
        action = request.POST.get('action')
        notes = request.POST.get('notes', '')
        app.reviewed_by = request.user
        app.review_date = timezone.now()
        app.review_notes = notes

        if action == 'approve':
            app.status = SeatApplication.Status.APPROVED
            messages.success(request, f"Application #{app.id} approved. You can now allocate an available bed.")
        elif action == 'reject':
            app.status = SeatApplication.Status.REJECTED
            messages.warning(request, f"Application #{app.id} rejected.")
        elif action == 'waitlist':
            app.status = SeatApplication.Status.WAITLISTED
            last_priority = WaitingListEntry.objects.count()
            WaitingListEntry.objects.create(
                application=app,
                priority_number=last_priority + 1,
                status=WaitingListEntry.Status.WAITING
            )
            messages.info(request, f"Application #{app.id} placed on the waiting list at position #{last_priority + 1}.")
        app.save()
        return redirect('allocations:application_list')

    available_beds = Bed.objects.filter(is_occupied=False).select_related('room', 'room__block')
    return render(request, 'allocations/review_application.html', {
        'application': app,
        'available_beds': available_beds
    })


@login_required
@warden_or_admin_only
def allocate_bed_view(request, app_id):
    app = get_object_or_404(SeatApplication, id=app_id)
    if request.method == 'POST':
        bed_id = request.POST.get('bed_id')
        notes = request.POST.get('notes', '')
        bed = get_object_or_404(Bed, id=bed_id)
        try:
            AllocationService.allocate_bed(
                resident=app.resident,
                bed=bed,
                actor=request.user,
                application=app,
                notes=notes
            )
            messages.success(request, f"Bed {bed} successfully allocated to {app.resident.student_id}.")
            return redirect('allocations:application_list')
        except ValidationError as e:
            messages.error(request, str(e))

    available_beds = Bed.objects.filter(is_occupied=False).select_related('room', 'room__block')
    return render(request, 'allocations/allocate_bed.html', {
        'application': app,
        'available_beds': available_beds
    })


@login_required
def waiting_list_view(request):
    entries = WaitingListEntry.objects.select_related('application', 'application__resident', 'application__resident__user').order_by('priority_number')
    return render(request, 'allocations/waiting_list.html', {'entries': entries})


@login_required
def transfer_list_view(request):
    if request.user.is_resident:
        resident = getattr(request.user, 'resident_profile', None)
        transfers = RoomTransferRequest.objects.filter(resident=resident)
    else:
        transfers = RoomTransferRequest.objects.select_related('resident', 'resident__user', 'current_bed', 'target_room').all()

    return render(request, 'allocations/transfer_list.html', {'transfers': transfers})


@login_required
@resident_access_only
def request_transfer_view(request):
    resident = getattr(request.user, 'resident_profile', None)
    if not resident or not resident.current_bed:
        messages.error(request, "You must have an active allocated bed to request a room transfer.")
        return redirect('residents:resident_dashboard')

    if request.method == 'POST':
        form = RoomTransferRequestForm(request.POST)
        if form.is_valid():
            req = form.save(commit=False)
            req.resident = resident
            req.current_bed = resident.current_bed
            req.save()
            messages.success(request, "Room transfer request submitted for warden review.")
            return redirect('allocations:transfer_list')
    else:
        form = RoomTransferRequestForm()
    return render(request, 'allocations/request_transfer.html', {'form': form, 'current_bed': resident.current_bed})


@login_required
@warden_or_admin_only
def process_transfer_view(request, transfer_id):
    transfer = get_object_or_404(RoomTransferRequest, id=transfer_id)
    if request.method == 'POST':
        action = request.POST.get('action')
        notes = request.POST.get('notes', '')
        if action == 'reject':
            transfer.status = RoomTransferRequest.Status.REJECTED
            transfer.decision_notes = notes
            transfer.processed_by = request.user
            transfer.save()
            messages.info(request, f"Transfer request #{transfer.id} rejected.")
            return redirect('allocations:transfer_list')
        elif action == 'transfer':
            new_bed_id = request.POST.get('new_bed_id')
            new_bed = get_object_or_404(Bed, id=new_bed_id)
            try:
                AllocationService.execute_room_transfer(transfer, new_bed, request.user)
                messages.success(request, f"Transfer completed: {transfer.resident.student_id} moved to {new_bed}.")
                return redirect('allocations:transfer_list')
            except ValidationError as e:
                messages.error(request, str(e))

    available_beds = Bed.objects.filter(is_occupied=False).select_related('room', 'room__block')
    return render(request, 'allocations/process_transfer.html', {
        'transfer': transfer,
        'available_beds': available_beds
    })


@login_required
def clearance_list_view(request):
    if request.user.is_resident:
        resident = getattr(request.user, 'resident_profile', None)
        clearances = CheckoutClearance.objects.filter(resident=resident)
    else:
        clearances = CheckoutClearance.objects.select_related('resident', 'resident__user').all()

    return render(request, 'allocations/clearance_list.html', {'clearances': clearances})


@login_required
@resident_access_only
def request_clearance_view(request):
    resident = getattr(request.user, 'resident_profile', None)
    if not resident:
        messages.error(request, "Resident profile required.")
        return redirect('accounts:dashboard')

    if request.method == 'POST':
        form = CheckoutClearanceRequestForm(request.POST)
        if form.is_valid():
            clr = form.save(commit=False)
            clr.resident = resident
            clr.save()
            messages.success(request, "Checkout clearance initiated. Pending Property, Accounts, and Warden review.")
            return redirect('allocations:clearance_list')
    else:
        form = CheckoutClearanceRequestForm()
    return render(request, 'allocations/request_clearance.html', {'form': form})


@login_required
def approve_clearance_step_view(request, clearance_id):
    clearance = get_object_or_404(CheckoutClearance, id=clearance_id)
    user = request.user
    step = request.POST.get('step')

    if step == 'property' and (user.is_warden or user.is_admin_user or user.is_maintenance_staff):
        clearance.property_clearance = True
        clearance.property_cleared_by = user
        clearance.status = CheckoutClearance.Status.IN_PROGRESS
        messages.success(request, "Property / Room clearance verified.")
    elif step == 'accounts' and (user.is_accounts_staff or user.is_admin_user):
        clearance.accounts_clearance = True
        clearance.accounts_cleared_by = user
        clearance.status = CheckoutClearance.Status.IN_PROGRESS
        messages.success(request, "Accounts & Fee dues clearance verified.")
    elif step == 'warden' and (user.is_warden or user.is_admin_user):
        if not (clearance.property_clearance and clearance.accounts_clearance):
            messages.error(request, "Cannot approve final checkout: Property and Accounts clearances must be completed first.")
            return redirect('allocations:clearance_list')
        clearance.warden_approval = True
        clearance.warden_approved_by = user
        try:
            AllocationService.finalize_checkout(clearance, user)
            messages.success(request, f"Resident {clearance.resident.student_id} checkout finalized and bed released.")
        except ValidationError as e:
            messages.error(request, str(e))
            return redirect('allocations:clearance_list')

    clearance.save()
    return redirect('allocations:clearance_list')
