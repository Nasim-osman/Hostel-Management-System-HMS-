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


class PublicSeatApplicationForm(forms.Form):
    # Student / User details
    full_name = forms.CharField(max_length=150, widget=forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'e.g. Nasim Ahmed'}))
    email = forms.EmailField(widget=forms.EmailInput(attrs={'class': 'form-input', 'placeholder': 'student@university.edu'}))
    phone_number = forms.CharField(max_length=20, widget=forms.TextInput(attrs={'class': 'form-input', 'placeholder': '+880 1712 345678'}))
    student_id = forms.CharField(max_length=50, widget=forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'e.g. DU-CSE-2024-045'}))
    course = forms.CharField(max_length=100, widget=forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'e.g. Computer Science & Engineering'}))
    batch_year = forms.CharField(max_length=20, initial='2024-2028', widget=forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'e.g. 2024-2028'}))
    gender = forms.ChoiceField(choices=[('MALE', 'Male'), ('FEMALE', 'Female')], widget=forms.Select(attrs={'class': 'form-select'}))
    blood_group = forms.CharField(max_length=5, required=False, widget=forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'e.g. B+'}))
    
    # Guardian details
    guardian_name = forms.CharField(max_length=100, widget=forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Parent or Guardian Full Name'}))
    guardian_phone = forms.CharField(max_length=20, widget=forms.TextInput(attrs={'class': 'form-input', 'placeholder': '+880 1819 000000'}))
    guardian_relation = forms.CharField(max_length=50, initial='Father', widget=forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'e.g. Father / Mother'}))
    home_district = forms.CharField(max_length=100, required=False, widget=forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'e.g. Dhaka / Chittagong / Sylhet'}))

    # Hostel Application Details
    preferred_block = forms.ModelChoiceField(queryset=HostelBlock.objects.all(), required=False, widget=forms.Select(attrs={'class': 'form-select'}))
    preferred_room_type = forms.ChoiceField(choices=Room.RoomType.choices, initial=Room.RoomType.DOUBLE, widget=forms.Select(attrs={'class': 'form-select'}))
    academic_year = forms.CharField(max_length=20, initial='2026-2027', widget=forms.TextInput(attrs={'class': 'form-input'}))
    
    # Account Password
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-input', 'placeholder': 'Choose password for HMS student portal login'}))



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
