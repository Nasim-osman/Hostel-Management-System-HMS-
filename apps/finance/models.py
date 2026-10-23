from django.db import models
from django.conf import settings
from decimal import Decimal
from apps.residents.models import ResidentProfile


class FeeCategory(models.Model):
    class Frequency(models.TextChoices):
        MONTHLY = 'MONTHLY', 'Monthly'
        SEMESTER = 'SEMESTER', 'Semester'
        ANNUAL = 'ANNUAL', 'Annual'
        ONE_TIME = 'ONE_TIME', 'One-Time Deposit'

    name = models.CharField(max_length=100, unique=True, help_text="e.g. Hostel Rent, Mess Fee, Caution Deposit")
    default_amount = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('5000.00'))
    frequency = models.CharField(max_length=20, choices=Frequency.choices, default=Frequency.MONTHLY)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name_plural = 'Fee Categories'
        ordering = ['name']

    def __str__(self):
        return f"{self.name} (₹{self.default_amount} / {self.get_frequency_display()})"


class ResidentCharge(models.Model):
    class Status(models.TextChoices):
        UNPAID = 'UNPAID', 'Unpaid'
        PARTIALLY_PAID = 'PARTIALLY_PAID', 'Partially Paid'
        PAID = 'PAID', 'Fully Paid'
        WAIVED = 'WAIVED', 'Waived'

    resident = models.ForeignKey(ResidentProfile, on_delete=models.CASCADE, related_name='charges')
    fee_category = models.ForeignKey(FeeCategory, on_delete=models.PROTECT, related_name='charges')
    description = models.CharField(max_length=200, help_text="e.g. October 2026 Hostel Rent")
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    paid_amount = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    due_date = models.DateField()
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.UNPAID)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-due_date', '-created_at']

    def __str__(self):
        return f"{self.resident.student_id} - {self.description} (৳{self.amount})"

    @property
    def balance_remaining(self):
        return max(Decimal('0.00'), self.amount - self.paid_amount)


class Payment(models.Model):
    class PaymentMethod(models.TextChoices):
        BKASH = 'BKASH', 'bKash'
        NAGAD = 'NAGAD', 'Nagad'
        ROCKET = 'ROCKET', 'Rocket (DBBL)'
        BANK_TRANSFER = 'BANK_TRANSFER', 'Bank Deposit / Sonali Bank'
        CARD = 'CARD', 'Debit / Credit Card'
        CASH = 'CASH', 'Cash Counter'
        UPI = 'UPI', 'MFS / Online'
        CHEQUE = 'CHEQUE', 'Cheque / Demand Draft'

    class Status(models.TextChoices):
        PENDING_VERIFICATION = 'PENDING', 'Pending Verification'
        VERIFIED = 'VERIFIED', 'Verified / Completed'
        REJECTED = 'REJECTED', 'Rejected'

    receipt_number = models.CharField(max_length=50, unique=True, help_text="Unique HMS receipt number, e.g. HMS-REC-2026-0001")
    resident = models.ForeignKey(ResidentProfile, on_delete=models.PROTECT, related_name='payments')
    charge = models.ForeignKey(ResidentCharge, on_delete=models.SET_NULL, null=True, blank=True, related_name='payments')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_date = models.DateField()
    payment_method = models.CharField(max_length=20, choices=PaymentMethod.choices, default=PaymentMethod.UPI)
    transaction_reference = models.CharField(max_length=100, blank=True, help_text="Bank Ref / UPI UTR / Cash receipt number")
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.VERIFIED)
    recorded_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name='recorded_payments')
    verified_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='verified_payments')
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-payment_date', '-created_at']

    def __str__(self):
        return f"{self.receipt_number} - {self.resident.student_id} (₹{self.amount})"


class Fine(models.Model):
    class Status(models.TextChoices):
        PENDING = 'PENDING', 'Pending'
        PAID = 'PAID', 'Paid'
        WAIVED = 'WAIVED', 'Waived'

    resident = models.ForeignKey(ResidentProfile, on_delete=models.CASCADE, related_name='fines')
    reason = models.CharField(max_length=200, help_text="Reason for penalty")
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    issued_date = models.DateField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
    issued_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name='issued_fines')
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ['-issued_date']

    def __str__(self):
        return f"Fine: {self.resident.student_id} - ₹{self.amount} ({self.reason})"


class Refund(models.Model):
    class Status(models.TextChoices):
        REQUESTED = 'REQUESTED', 'Requested'
        APPROVED = 'APPROVED', 'Approved'
        PROCESSED = 'PROCESSED', 'Processed / Paid Out'
        REJECTED = 'REJECTED', 'Rejected'

    resident = models.ForeignKey(ResidentProfile, on_delete=models.CASCADE, related_name='refunds')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    reason = models.CharField(max_length=200, help_text="e.g. Caution deposit return upon clearance")
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.REQUESTED)
    requested_date = models.DateField(auto_now_add=True)
    approved_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='approved_refunds')
    processed_date = models.DateField(null=True, blank=True)
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ['-requested_date']

    def __str__(self):
        return f"Refund: {self.resident.student_id} - ₹{self.amount} ({self.get_status_display()})"


class HostelExpense(models.Model):
    class Category(models.TextChoices):
        UTILITIES = 'UTILITIES', 'Electricity & Water'
        MAINTENANCE = 'MAINTENANCE', 'Repairs & Maintenance'
        MESS_SUPPLIES = 'MESS_SUPPLIES', 'Mess / Kitchen Supplies'
        CLEANING = 'CLEANING', 'Housekeeping & Sanitation'
        STAFF = 'STAFF', 'Staff Honorarium / Wages'
        MISCELLANEOUS = 'MISC', 'Administrative / Miscellaneous'

    category = models.CharField(max_length=30, choices=Category.choices, default=Category.UTILITIES)
    title = models.CharField(max_length=200)
    payee = models.CharField(max_length=150, help_text="Vendor or service provider name")
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    expense_date = models.DateField()
    invoice_number = models.CharField(max_length=100, blank=True)
    recorded_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name='recorded_expenses')
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-expense_date', '-created_at']

    def __str__(self):
        return f"Expense: {self.title} - ₹{self.amount} ({self.get_category_display()})"
