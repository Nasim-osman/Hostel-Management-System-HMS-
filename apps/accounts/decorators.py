from functools import wraps
from django.core.exceptions import PermissionDenied
from django.shortcuts import redirect
from django.contrib import messages


def role_required(allowed_roles):
    """
    Decorator for views that checks if the logged-in user belongs to allowed roles.
    allowed_roles can be a single role string or a list/tuple of role strings.
    """
    if isinstance(allowed_roles, str):
        allowed_roles = [allowed_roles]

    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return redirect('accounts:login')
            
            # Superuser always has admin privileges
            if request.user.is_superuser:
                return view_func(request, *args, **kwargs)
                
            if request.user.role not in allowed_roles:
                messages.error(request, "Access denied: You do not have permission to view this resource.")
                raise PermissionDenied("You do not have permission to perform this action.")
                
            return view_func(request, *args, **kwargs)
        return _wrapped_view
    return decorator


def resident_access_only(view_func):
    """Restricts access specifically to authenticated residents."""
    return role_required(['RESIDENT'])(view_func)


def staff_access_only(view_func):
    """Restricts access to management/staff (Admin, Warden, Accounts, Maintenance)."""
    return role_required(['ADMIN', 'WARDEN', 'ACCOUNTS', 'MAINTENANCE'])(view_func)


def warden_or_admin_only(view_func):
    """Restricts access to Warden or Administrator."""
    return role_required(['ADMIN', 'WARDEN'])(view_func)


def accounts_or_admin_only(view_func):
    """Restricts access to Accounts staff or Administrator."""
    return role_required(['ADMIN', 'ACCOUNTS'])(view_func)
