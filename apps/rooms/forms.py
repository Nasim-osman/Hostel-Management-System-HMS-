from django import forms
from .models import Room, Bed, HostelBlock, Amenity


class RoomForm(forms.ModelForm):
    class Meta:
        model = Room
        fields = ['block', 'room_number', 'floor', 'room_type', 'capacity', 'base_fee', 'is_active']
        widgets = {
            'block': forms.Select(attrs={'class': 'form-select'}),
            'room_number': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'e.g. 101'}),
            'floor': forms.NumberInput(attrs={'class': 'form-input'}),
            'room_type': forms.Select(attrs={'class': 'form-select'}),
            'capacity': forms.NumberInput(attrs={'class': 'form-input'}),
            'base_fee': forms.NumberInput(attrs={'class': 'form-input'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-checkbox h-4 w-4 text-blue-600'}),
        }


class BedForm(forms.ModelForm):
    class Meta:
        model = Bed
        fields = ['bed_number', 'is_occupied']
        widgets = {
            'bed_number': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'e.g. Bed-A'}),
            'is_occupied': forms.CheckboxInput(attrs={'class': 'form-checkbox h-4 w-4 text-blue-600'}),
        }


class AmenityUpdateForm(forms.ModelForm):
    class Meta:
        model = Amenity
        fields = ['status', 'description']
        widgets = {
            'status': forms.Select(attrs={'class': 'form-select'}),
            'description': forms.TextInput(attrs={'class': 'form-input'}),
        }
