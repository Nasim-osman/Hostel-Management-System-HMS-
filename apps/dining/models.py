from django.db import models
from django.conf import settings
from apps.residents.models import ResidentProfile


class MealMenu(models.Model):
    class MealType(models.TextChoices):
        BREAKFAST = 'BREAKFAST', 'Breakfast'
        LUNCH = 'LUNCH', 'Lunch'
        DINNER = 'DINNER', 'Dinner'

    meal_type = models.CharField(max_length=20, choices=MealType.choices, unique=True)
    timing = models.CharField(max_length=50, blank=True, help_text="e.g. 7:30 AM - 9:30 AM")
    veg_items = models.TextField(help_text="Veg dishes, e.g. Sprouts | 3 Chapatis | Rice | Dal")
    non_veg_items = models.TextField(blank=True, help_text="Non-veg alternative, e.g. Egg Biryani")
    is_active = models.BooleanField(default=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['meal_type']

    def __str__(self):
        return f"{self.get_meal_type_display()} Menu"


class MessFeedback(models.Model):
    resident = models.ForeignKey(ResidentProfile, on_delete=models.CASCADE, related_name='meal_feedbacks')
    meal_type = models.CharField(max_length=20, choices=MealMenu.MealType.choices)
    rating = models.PositiveSmallIntegerField(help_text="Rating from 1 to 5")
    comments = models.TextField(blank=True)
    created_at = models.DateField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.resident.student_id} - {self.meal_type} ({self.rating}/5)"
