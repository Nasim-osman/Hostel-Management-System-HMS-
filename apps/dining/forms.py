from django import forms
from .models import MealMenu, MessFeedback


class MealMenuForm(forms.ModelForm):
    class Meta:
        model = MealMenu
        fields = ['meal_type', 'timing', 'veg_items', 'non_veg_items', 'is_active']
        widgets = {
            'meal_type': forms.Select(attrs={'class': 'form-select'}),
            'timing': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'e.g. 12:30 PM - 2:30 PM'}),
            'veg_items': forms.Textarea(attrs={'class': 'form-textarea', 'rows': 2, 'placeholder': 'Dishes separated by pipe |'}),
            'non_veg_items': forms.Textarea(attrs={'class': 'form-textarea', 'rows': 2, 'placeholder': 'Dishes separated by pipe |'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-checkbox h-4 w-4 text-blue-600'}),
        }


class MessFeedbackForm(forms.ModelForm):
    class Meta:
        model = MessFeedback
        fields = ['meal_type', 'rating', 'comments']
        widgets = {
            'meal_type': forms.Select(attrs={'class': 'form-select'}),
            'rating': forms.Select(choices=[(i, f"{i} Stars") for i in range(1, 6)], attrs={'class': 'form-select'}),
            'comments': forms.Textarea(attrs={'class': 'form-textarea', 'rows': 3, 'placeholder': 'Optional comments on meal quality...'}),
        }
