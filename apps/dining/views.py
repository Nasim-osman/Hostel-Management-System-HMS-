from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from apps.accounts.decorators import role_required, resident_access_only
from .models import MealMenu, MessFeedback
from .forms import MealMenuForm, MessFeedbackForm


@login_required
def meal_menu_view(request):
    meals = MealMenu.objects.all().order_by('meal_type')
    feedbacks = MessFeedback.objects.select_related('resident', 'resident__user')[:10]
    return render(request, 'dining/menu_list.html', {'meals': meals, 'feedbacks': feedbacks})


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
