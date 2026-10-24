from django.db import models
from django.conf import settings
from django.utils import timezone
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


class ResidentMealStatus(models.Model):
    resident = models.ForeignKey(ResidentProfile, on_delete=models.CASCADE, related_name='meal_statuses')
    date = models.DateField(default=timezone.now)
    breakfast = models.BooleanField(default=True, verbose_name="Breakfast ON/OFF")
    lunch = models.BooleanField(default=True, verbose_name="Lunch ON/OFF")
    dinner = models.BooleanField(default=True, verbose_name="Dinner ON/OFF")
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('resident', 'date')
        ordering = ['-date']
        verbose_name = 'Resident Meal Status'
        verbose_name_plural = 'Resident Meal Statuses'

    def __str__(self):
        b = 'ON' if self.breakfast else 'OFF'
        l = 'ON' if self.lunch else 'OFF'
        d = 'ON' if self.dinner else 'OFF'
        return f"{self.resident.student_id} ({self.date}): B:{b} | L:{l} | D:{d}"

