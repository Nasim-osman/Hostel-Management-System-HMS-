from django import forms
from django.contrib.auth import get_user_model
from .models import Complaint

User = get_user_model()


class ResidentComplaintForm(forms.ModelForm):
    class Meta:
        model = Complaint
        fields = ['title', 'category', 'priority', 'description']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'e.g. Water not coming in bathroom'}),
            'category': forms.Select(attrs={'class': 'form-select'}),
            'priority': forms.Select(attrs={'class': 'form-select'}),
            'description': forms.Textarea(attrs={'class': 'form-textarea', 'rows': 4, 'placeholder': 'Describe the problem clearly...'}),
        }


class ComplaintAssignmentForm(forms.ModelForm):
    assigned_to = forms.ModelChoiceField(
        queryset=User.objects.filter(role=User.Role.MAINTENANCE),
        widget=forms.Select(attrs={'class': 'form-select'}),
        required=True
    )

    class Meta:
        model = Complaint
        fields = ['assigned_to', 'priority']
        widgets = {
            'priority': forms.Select(attrs={'class': 'form-select'}),
        }


class ComplaintResolutionForm(forms.ModelForm):
    class Meta:
        model = Complaint
        fields = ['status', 'resolution_notes']
        widgets = {
            'status': forms.Select(attrs={'class': 'form-select'}),
            'resolution_notes': forms.Textarea(attrs={'class': 'form-textarea', 'rows': 3, 'placeholder': 'Detail the corrective action taken...'}),
        }
