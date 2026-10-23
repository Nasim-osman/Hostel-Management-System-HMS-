from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from apps.accounts.decorators import role_required
from .models import VisitorLog
from .forms import VisitorCheckInForm
import uuid


@login_required
def visitor_list_view(request):
    if request.user.is_resident:
        resident = getattr(request.user, 'resident_profile', None)
        visitors = VisitorLog.objects.filter(resident=resident).order_by('-check_in_time')
    else:
        visitors = VisitorLog.objects.select_related('resident', 'resident__user').order_by('-check_in_time')
        status_filter = request.GET.get('status')
        if status_filter:
            visitors = visitors.filter(status=status_filter)

    active_count = VisitorLog.objects.filter(status='CHECKED_IN').count()
    return render(request, 'visitors/visitor_list.html', {
        'visitors': visitors,
        'active_count': active_count,
        'status_choices': VisitorLog.Status.choices,
        'selected_status': request.GET.get('status'),
    })


@login_required
@role_required(['ADMIN', 'WARDEN'])
def check_in_visitor_view(request):
    if request.method == 'POST':
        form = VisitorCheckInForm(request.POST)
        if form.is_valid():
            vis = form.save(commit=False)
            vis.recorded_by = request.user
            vis.gate_pass_no = f"GP-{timezone.now().strftime('%d%m')}-{uuid.uuid4().hex[:4].upper()}"
            vis.save()
            messages.success(request, f"Visitor '{vis.visitor_name}' checked in. Gate Pass: {vis.gate_pass_no}.")
            return redirect('visitors:visitor_list')
    else:
        form = VisitorCheckInForm()
    return render(request, 'visitors/check_in.html', {'form': form})


@login_required
@role_required(['ADMIN', 'WARDEN'])
def check_out_visitor_view(request, visitor_id):
    visitor = get_object_or_404(VisitorLog, id=visitor_id)
    if request.method == 'POST':
        visitor.status = VisitorLog.Status.CHECKED_OUT
        visitor.check_out_time = timezone.now()
        visitor.save()
        messages.success(request, f"Visitor '{visitor.visitor_name}' checked out successfully.")
    return redirect('visitors:visitor_list')
