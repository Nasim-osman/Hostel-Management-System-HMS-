from django.db import models
from django.conf import settings


class Experiment(models.Model):
    name = models.CharField(max_length=150)
    code = models.CharField(max_length=50, unique=True, help_text="e.g. DASHBOARD_URGENT_ACTIONS")
    hypothesis = models.TextField()
    variant_a_name = models.CharField(max_length=100, default="Variant A: Standard Dashboard")
    variant_b_name = models.CharField(max_length=100, default="Variant B: Prioritized Urgent Actions Banner")
    primary_metric = models.CharField(max_length=100, default="Action Item Click-Through Rate (CTR)")
    is_active = models.BooleanField(default=True)
    start_date = models.DateTimeField(auto_now_add=True)
    end_date = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.name} ({self.code})"


class UserVariantAssignment(models.Model):
    experiment = models.ForeignKey(Experiment, on_delete=models.CASCADE, related_name='assignments')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='ab_assignments')
    variant = models.CharField(max_length=1, choices=[('A', 'Variant A'), ('B', 'Variant B')])
    assigned_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('experiment', 'user')

    def __str__(self):
        return f"{self.user.username} -> {self.experiment.code}: Variant {self.variant}"


class MetricEvent(models.Model):
    experiment = models.ForeignKey(Experiment, on_delete=models.CASCADE, related_name='events')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    variant = models.CharField(max_length=1, choices=[('A', 'Variant A'), ('B', 'Variant B')])
    event_name = models.CharField(max_length=100, help_text="e.g. VIEW_DASHBOARD, CLICK_ACTION_ITEM")
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-timestamp']

    def __str__(self):
        return f"[{self.experiment.code}] {self.variant} - {self.event_name} by {self.user.username}"
