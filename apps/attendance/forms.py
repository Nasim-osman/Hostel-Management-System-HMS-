from django import forms
from .models import AttendanceRecord, OutpassRequest


class OutpassRequestForm(forms.ModelForm):
    class Meta:
        model = OutpassRequest
        fields = ['purpose', 'destination_address', 'departure_time', 'expected_return_time', 'parent_contact']
        widgets = {
            'purpose': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'e.g. Weekend Home Visit'}),
            'destination_address': forms.Textarea(attrs={'class': 'form-textarea', 'rows': 2, 'placeholder': 'Home or destination address'}),
            'departure_time': forms.DateTimeInput(attrs={'class': 'form-input', 'type': 'datetime-local'}),
            'expected_return_time': forms.DateTimeInput(attrs={'class': 'form-input', 'type': 'datetime-local'}),
            'parent_contact': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Parent contact number'}),
        }
