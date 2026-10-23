from django.db import models
from django.conf import settings


class AuditLog(models.Model):
    class Action(models.TextChoices):
        CREATE = 'CREATE', 'Created Record'
        UPDATE = 'UPDATE', 'Updated Record'
        DELETE = 'DELETE', 'Deleted / Archived'
        APPROVE = 'APPROVE', 'Approved'
        REJECT = 'REJECT', 'Rejected'
        ALLOCATE = 'ALLOCATE', 'Seat Allocated'
        TRANSFER = 'TRANSFER', 'Room Transferred'
        VERIFY = 'VERIFY', 'Payment Verified'
        CLEARANCE = 'CLEARANCE', 'Clearance Finalized'
        EXPORT = 'EXPORT', 'Data Exported'
        LOGIN = 'LOGIN', 'User Logged In'

    actor = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='audit_actions')
    action = models.CharField(max_length=20, choices=Action.choices)
    module = models.CharField(max_length=50, help_text="e.g. Accounts, Allocations, Finance, Rooms")
    target_repr = models.CharField(max_length=255, help_text="Human readable summary of affected item")
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    details = models.TextField(blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-timestamp']

    def __str__(self):
        actor_name = self.actor.username if self.actor else "System"
        return f"[{self.timestamp.strftime('%Y-%m-%d %H:%M')}] {actor_name} -> {self.action} on {self.module} ({self.target_repr})"


def log_audit(actor, action, module, target_repr, ip_address=None, details=""):
    """
    Central utility function to record an immutable audit log entry.
    """
    return AuditLog.objects.create(
        actor=actor if (actor and actor.is_authenticated) else None,
        action=action,
        module=module,
        target_repr=str(target_repr)[:255],
        ip_address=ip_address,
        details=str(details)
    )
