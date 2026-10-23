from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from apps.accounts.decorators import role_required
from .models import AuditLog


@login_required
@role_required(['ADMIN'])
def audit_log_list_view(request):
    logs = AuditLog.objects.select_related('actor').all()

    action_filter = request.GET.get('action')
    module_filter = request.GET.get('module')
    search_q = request.GET.get('q')

    if action_filter:
        logs = logs.filter(action=action_filter)
    if module_filter:
        logs = logs.filter(module=module_filter)
    if search_q:
        logs = logs.filter(
            Q(target_repr__icontains=search_q) |
            Q(actor__username__icontains=search_q) |
            Q(details__icontains=search_q)
        )

    return render(request, 'audit/audit_list.html', {
        'logs': logs[:200],
        'action_choices': AuditLog.Action.choices,
        'selected_action': action_filter,
        'selected_module': module_filter,
        'search_q': search_q,
    })
