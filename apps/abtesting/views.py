from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from apps.accounts.decorators import role_required
from .models import Experiment, UserVariantAssignment, MetricEvent


@login_required
@role_required(['ADMIN', 'WARDEN'])
def ab_test_dashboard_view(request):
    """
    Renders the A/B testing analytics report showing real conversion metrics for Variant A vs B.
    """
    experiment = Experiment.objects.filter(code='DASHBOARD_URGENT_ACTIONS').first()
    if not experiment:
        experiment = Experiment.objects.create(
            name="Hostel Dashboard Urgent Pending Actions Layout",
            code="DASHBOARD_URGENT_ACTIONS",
            hypothesis="Displaying an elevated, high-contrast urgent pending-actions banner at the top of the dashboard increases warden/admin engagement with unassigned tickets and pending applications by at least 25%.",
            variant_a_name="Standard Grid Layout",
            variant_b_name="Prioritized Pending Actions Panel",
            primary_metric="Urgent Action Click Rate"
        )

    # Calculate real metrics
    views_a = MetricEvent.objects.filter(experiment=experiment, variant='A', event_name='VIEW_DASHBOARD').count()
    clicks_a = MetricEvent.objects.filter(experiment=experiment, variant='A', event_name='CLICK_ACTION_ITEM').count()
    ctr_a = round((clicks_a / views_a * 100), 2) if views_a > 0 else 0.0

    views_b = MetricEvent.objects.filter(experiment=experiment, variant='B', event_name='VIEW_DASHBOARD').count()
    clicks_b = MetricEvent.objects.filter(experiment=experiment, variant='B', event_name='CLICK_ACTION_ITEM').count()
    ctr_b = round((clicks_b / views_b * 100), 2) if views_b > 0 else 0.0

    improvement = round(ctr_b - ctr_a, 2)
    relative_lift = round(((ctr_b - ctr_a) / ctr_a * 100), 2) if ctr_a > 0 else 0.0

    context = {
        'experiment': experiment,
        'views_a': views_a,
        'clicks_a': clicks_a,
        'ctr_a': ctr_a,
        'views_b': views_b,
        'clicks_b': clicks_b,
        'ctr_b': ctr_b,
        'improvement': improvement,
        'relative_lift': relative_lift,
        'total_participants': UserVariantAssignment.objects.filter(experiment=experiment).count(),
    }
    return render(request, 'abtesting/ab_dashboard.html', context)


@login_required
def track_metric_event_view(request):
    """
    API endpoint for logging user interaction with A/B variant items.
    """
    if request.method == 'POST':
        event_name = request.POST.get('event_name', 'CLICK_ACTION_ITEM')
        experiment = Experiment.objects.filter(code='DASHBOARD_URGENT_ACTIONS').first()
        if experiment:
            assignment = UserVariantAssignment.objects.filter(experiment=experiment, user=request.user).first()
            variant = assignment.variant if assignment else 'A'
            MetricEvent.objects.create(
                experiment=experiment,
                user=request.user,
                variant=variant,
                event_name=event_name
            )
            return JsonResponse({'status': 'success', 'recorded_event': event_name})
    return JsonResponse({'status': 'ignored'}, status=400)
