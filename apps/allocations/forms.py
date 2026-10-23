from django import forms
from .models import SeatApplication, RoomTransferRequest, CheckoutClearance
from apps.rooms.models import Room, Bed, HostelBlock


class SeatApplicationForm(forms.ModelForm):
    class Meta:
        model = SeatApplication
        fields = ['preferred_room_type', 'preferred_block', 'academic_year']
        widgets = {
            'preferred_room_type': forms.Select(attrs={'class': 'form-select'}),
            'preferred_block': forms.Select(attrs={'class': 'form-select'}),
            'academic_year': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'e.g. 2026-2027'}),
        }


class RoomTransferRequestForm(forms.ModelForm):
    class Meta:
        model = RoomTransferRequest
        fields = ['target_room', 'reason']
        widgets = {
            'target_room': forms.Select(attrs={'class': 'form-select'}),
            'reason': forms.Textarea(attrs={'class': 'form-textarea', 'rows': 3, 'placeholder': 'Provide reason for transfer request'}),
        }


class CheckoutClearanceRequestForm(forms.ModelForm):
    class Meta:
        model = CheckoutClearance
        fields = ['expected_checkout_date', 'clearance_notes']
        widgets = {
            'expected_checkout_date': forms.DateInput(attrs={'class': 'form-input', 'type': 'date'}),
            'clearance_notes': forms.Textarea(attrs={'class': 'form-textarea', 'rows': 2, 'placeholder': 'Optional departure remarks'}),
        }
