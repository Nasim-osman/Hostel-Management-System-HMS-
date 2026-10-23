from django import forms
from .models import VisitorLog


class VisitorCheckInForm(forms.ModelForm):
    class Meta:
        model = VisitorLog
        fields = ['visitor_name', 'visitor_phone', 'resident', 'relationship', 'destination', 'purpose']
        widgets = {
            'visitor_name': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Visitor full name'}),
            'visitor_phone': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Contact number'}),
            'resident': forms.Select(attrs={'class': 'form-select'}),
            'relationship': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'e.g. Parent, Sibling, Friend'}),
            'destination': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'e.g. Building A | Floor 2nd | Room 201'}),
            'purpose': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Purpose of visit'}),
        }
