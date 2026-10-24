from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.utils import timezone
from datetime import timedelta, datetime
from apps.accounts.decorators import role_required, resident_access_only
from .models import MealMenu, MessFeedback, ResidentMealStatus
from .forms import MealMenuForm, MessFeedbackForm


@login_required
def meal_menu_view(request):
    meals = MealMenu.objects.all().order_by('meal_type')
    feedbacks = MessFeedback.objects.select_related('resident', 'resident__user')[:10]
    
    meal_status = None
    tomorrow_status = None
    if request.user.is_resident and hasattr(request.user, 'resident_profile'):
        today = timezone.now().date()
        tomorrow = today + timedelta(days=1)
        meal_status, _ = ResidentMealStatus.objects.get_or_create(
            resident=request.user.resident_profile,
            date=today,
            defaults={'breakfast': True, 'lunch': True, 'dinner': True}
        )
        tomorrow_status, _ = ResidentMealStatus.objects.get_or_create(
            resident=request.user.resident_profile,
            date=tomorrow,
            defaults={'breakfast': True, 'lunch': True, 'dinner': True}
        )

    # Meal counts for staff/admin
    today_date = timezone.now().date()
    stats = {
        'breakfast_count': ResidentMealStatus.objects.filter(date=today_date, breakfast=True).count(),
        'lunch_count': ResidentMealStatus.objects.filter(date=today_date, lunch=True).count(),
        'dinner_count': ResidentMealStatus.objects.filter(date=today_date, dinner=True).count(),
    }

    return render(request, 'dining/menu_list.html', {
        'meals': meals,
        'feedbacks': feedbacks,
        'meal_status': meal_status,
        'tomorrow_status': tomorrow_status,
        'stats': stats,
    })


@login_required
@role_required(['ADMIN', 'WARDEN'])
def edit_menu_view(request, meal_id):
    meal = get_object_or_404(MealMenu, id=meal_id)
    if request.method == 'POST':
        form = MealMenuForm(request.POST, instance=meal)
        if form.is_valid():
            form.save()
            messages.success(request, f"{meal.get_meal_type_display()} menu updated successfully.")
            return redirect('dining:meal_menu')
    else:
        form = MealMenuForm(instance=meal)
    return render(request, 'dining/menu_form.html', {'form': form, 'meal': meal})


@login_required
@resident_access_only
def submit_feedback_view(request):
    resident = getattr(request.user, 'resident_profile', None)
    if not resident:
        messages.error(request, "Resident profile required.")
        return redirect('accounts:dashboard')

    if request.method == 'POST':
        form = MessFeedbackForm(request.POST)
        if form.is_valid():
            fb = form.save(commit=False)
            fb.resident = resident
            fb.save()
            messages.success(request, "Thank you! Your mess meal feedback has been recorded.")
            return redirect('dining:meal_menu')
    else:
        form = MessFeedbackForm()
    return render(request, 'dining/feedback_form.html', {'form': form})


@login_required
@resident_access_only
def toggle_meal_status_view(request):
    """
    Toggles a resident's meal ON or OFF for today or a target date.
    Supports regular POST form submissions and AJAX requests.
    """
    resident = getattr(request.user, 'resident_profile', None)
    if not resident:
        if request.headers.get('x-requested-with') == 'XMLHttpRequest' or request.content_type == 'application/json':
            return JsonResponse({'success': False, 'error': 'Resident profile not found'}, status=400)
        messages.error(request, "Resident profile required.")
        return redirect('accounts:dashboard')

    if request.method == 'POST':
        meal_type = request.POST.get('meal_type', 'all').lower()
        target_date_str = request.POST.get('date')
        if target_date_str:
            try:
                target_date = datetime.strptime(target_date_str, '%Y-%m-%d').date()
            except ValueError:
                target_date = timezone.now().date()
        else:
            target_date = timezone.now().date()

        meal_status, _ = ResidentMealStatus.objects.get_or_create(
            resident=resident,
            date=target_date,
            defaults={'breakfast': True, 'lunch': True, 'dinner': True}
        )

        action = request.POST.get('action', 'toggle')

        if meal_type == 'breakfast':
            meal_status.breakfast = not meal_status.breakfast if action == 'toggle' else (action == 'on')
        elif meal_type == 'lunch':
            meal_status.lunch = not meal_status.lunch if action == 'toggle' else (action == 'on')
        elif meal_type == 'dinner':
            meal_status.dinner = not meal_status.dinner if action == 'toggle' else (action == 'on')
        elif meal_type == 'all':
            new_val = not (meal_status.breakfast and meal_status.lunch and meal_status.dinner) if action == 'toggle' else (action == 'on')
            meal_status.breakfast = new_val
            meal_status.lunch = new_val
            meal_status.dinner = new_val

        meal_status.save()

        msg = f"Meal status for {target_date.strftime('%b %d, %Y')} updated: Breakfast {'ON' if meal_status.breakfast else 'OFF'}, Lunch {'ON' if meal_status.lunch else 'OFF'}, Dinner {'ON' if meal_status.dinner else 'OFF'}."
        
        if request.headers.get('x-requested-with') == 'XMLHttpRequest' or request.content_type == 'application/json':
            return JsonResponse({
                'success': True,
                'date': str(target_date),
                'breakfast': meal_status.breakfast,
                'lunch': meal_status.lunch,
                'dinner': meal_status.dinner,
                'message': msg
            })

        messages.success(request, msg)
        referer = request.META.get('HTTP_REFERER')
        return redirect(referer if referer else 'residents:resident_dashboard')

    return redirect('dining:meal_menu')

