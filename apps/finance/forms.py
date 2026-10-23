from django import forms
from .models import FeeCategory, ResidentCharge, Payment, Fine, Refund, HostelExpense


class ResidentChargeForm(forms.ModelForm):
    class Meta:
        model = ResidentCharge
        fields = ['resident', 'fee_category', 'description', 'amount', 'due_date']
        widgets = {
            'resident': forms.Select(attrs={'class': 'form-select'}),
            'fee_category': forms.Select(attrs={'class': 'form-select'}),
            'description': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'e.g. November 2026 Hostel Rent'}),
            'amount': forms.NumberInput(attrs={'class': 'form-input'}),
            'due_date': forms.DateInput(attrs={'class': 'form-input', 'type': 'date'}),
        }


class PaymentRecordForm(forms.ModelForm):
    class Meta:
        model = Payment
        fields = ['resident', 'charge', 'amount', 'payment_date', 'payment_method', 'transaction_reference', 'notes']
        widgets = {
            'resident': forms.Select(attrs={'class': 'form-select'}),
            'charge': forms.Select(attrs={'class': 'form-select'}),
            'amount': forms.NumberInput(attrs={'class': 'form-input'}),
            'payment_date': forms.DateInput(attrs={'class': 'form-input', 'type': 'date'}),
            'payment_method': forms.Select(attrs={'class': 'form-select'}),
            'transaction_reference': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'UPI UTR / Cheque No / Bank Ref'}),
            'notes': forms.Textarea(attrs={'class': 'form-textarea', 'rows': 2}),
        }


class FineForm(forms.ModelForm):
    class Meta:
        model = Fine
        fields = ['resident', 'reason', 'amount', 'notes']
        widgets = {
            'resident': forms.Select(attrs={'class': 'form-select'}),
            'reason': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Reason for fine'}),
            'amount': forms.NumberInput(attrs={'class': 'form-input'}),
            'notes': forms.Textarea(attrs={'class': 'form-textarea', 'rows': 2}),
        }


class RefundForm(forms.ModelForm):
    class Meta:
        model = Refund
        fields = ['resident', 'amount', 'reason', 'notes']
        widgets = {
            'resident': forms.Select(attrs={'class': 'form-select'}),
            'amount': forms.NumberInput(attrs={'class': 'form-input'}),
            'reason': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'e.g. Caution deposit return'}),
            'notes': forms.Textarea(attrs={'class': 'form-textarea', 'rows': 2}),
        }


class HostelExpenseForm(forms.ModelForm):
    class Meta:
        model = HostelExpense
        fields = ['category', 'title', 'payee', 'amount', 'expense_date', 'invoice_number', 'description']
        widgets = {
            'category': forms.Select(attrs={'class': 'form-select'}),
            'title': forms.TextInput(attrs={'class': 'form-input'}),
            'payee': forms.TextInput(attrs={'class': 'form-input'}),
            'amount': forms.NumberInput(attrs={'class': 'form-input'}),
            'expense_date': forms.DateInput(attrs={'class': 'form-input', 'type': 'date'}),
            'invoice_number': forms.TextInput(attrs={'class': 'form-input'}),
            'description': forms.Textarea(attrs={'class': 'form-textarea', 'rows': 2}),
        }
