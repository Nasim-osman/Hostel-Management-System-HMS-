from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponse, Http404
from django.db import transaction
from django.db.models import Sum, Q
from django.utils import timezone
from decimal import Decimal
import uuid

from apps.accounts.decorators import role_required, accounts_or_admin_only
from .models import FeeCategory, ResidentCharge, Payment, Fine, Refund, HostelExpense
from .forms import ResidentChargeForm, PaymentRecordForm, FineForm, RefundForm, HostelExpenseForm
from .receipts import generate_receipt_pdf


@login_required
@role_required(['ADMIN', 'ACCOUNTS'])
def accounts_dashboard_view(request):
    total_paid = Payment.objects.filter(status='VERIFIED').aggregate(Sum('amount'))['amount__sum'] or Decimal('0.00')
    total_unpaid = ResidentCharge.objects.filter(status__in=['UNPAID', 'PARTIALLY_PAID']).aggregate(Sum('amount'))['amount__sum'] or Decimal('0.00')
    pending_payments_count = Payment.objects.filter(status='PENDING').count()
    total_expenses = HostelExpense.objects.aggregate(Sum('amount'))['amount__sum'] or Decimal('0.00')
    total_fines = Fine.objects.aggregate(Sum('amount'))['amount__sum'] or Decimal('0.00')

    recent_payments = Payment.objects.select_related('resident', 'resident__user').order_by('-payment_date')[:6]
    recent_expenses = HostelExpense.objects.order_by('-expense_date')[:6]

    context = {
        'total_paid': total_paid,
        'total_unpaid': total_unpaid,
        'pending_payments_count': pending_payments_count,
        'total_expenses': total_expenses,
        'total_fines': total_fines,
        'recent_payments': recent_payments,
        'recent_expenses': recent_expenses,
    }
    return render(request, 'finance/accounts_dashboard.html', context)


@login_required
def payment_list_view(request):
    if request.user.is_resident:
        resident = getattr(request.user, 'resident_profile', None)
        payments = Payment.objects.filter(resident=resident).order_by('-payment_date')
    else:
        payments = Payment.objects.select_related('resident', 'resident__user', 'charge').order_by('-payment_date')
        status_filter = request.GET.get('status')
        if status_filter:
            payments = payments.filter(status=status_filter)

    return render(request, 'finance/payment_list.html', {
        'payments': payments,
        'status_choices': Payment.Status.choices,
        'selected_status': request.GET.get('status'),
    })


@login_required
@accounts_or_admin_only
def record_payment_view(request):
    if request.method == 'POST':
        form = PaymentRecordForm(request.POST)
        if form.is_valid():
            payment = form.save(commit=False)
            payment.recorded_by = request.user
            # Generate unique receipt number
            payment.receipt_number = f"HMS-REC-{timezone.now().strftime('%Y%m')}-{uuid.uuid4().hex[:6].upper()}"
            payment.status = Payment.Status.VERIFIED
            payment.verified_by = request.user
            
            with transaction.atomic():
                payment.save()
                # Update charge if linked
                if payment.charge:
                    charge = payment.charge
                    charge.paid_amount += payment.amount
                    if charge.paid_amount >= charge.amount:
                        charge.status = ResidentCharge.Status.PAID
                    else:
                        charge.status = ResidentCharge.Status.PARTIALLY_PAID
                    charge.save()

            messages.success(request, f"Payment recorded successfully. Receipt #{payment.receipt_number} generated.")
            return redirect('finance:payment_list')
    else:
        initial_data = {}
        charge_id = request.GET.get('charge_id')
        if charge_id:
            charge = get_object_or_404(ResidentCharge, id=charge_id)
            initial_data = {
                'resident': charge.resident,
                'charge': charge,
                'amount': charge.balance_remaining,
                'payment_date': timezone.now().date(),
            }
        form = PaymentRecordForm(initial=initial_data)

    return render(request, 'finance/record_payment.html', {'form': form})


@login_required
@accounts_or_admin_only
def verify_payment_view(request, payment_id):
    payment = get_object_or_404(Payment, id=payment_id)
    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'verify':
            with transaction.atomic():
                payment.status = Payment.Status.VERIFIED
                payment.verified_by = request.user
                payment.save()
                if payment.charge:
                    charge = payment.charge
                    charge.paid_amount += payment.amount
                    if charge.paid_amount >= charge.amount:
                        charge.status = ResidentCharge.Status.PAID
                    else:
                        charge.status = ResidentCharge.Status.PARTIALLY_PAID
                    charge.save()
            messages.success(request, f"Payment #{payment.receipt_number} verified.")
        elif action == 'reject':
            payment.status = Payment.Status.REJECTED
            payment.save()
            messages.warning(request, f"Payment #{payment.receipt_number} marked as rejected.")
    return redirect('finance:payment_list')


@login_required
def download_receipt_pdf_view(request, receipt_number):
    """
    Downloads branded PDF receipt. Enforces resident isolation.
    """
    payment = get_object_or_404(Payment.objects.select_related('resident', 'resident__user', 'charge'), receipt_number=receipt_number)
    
    # Resident isolation check
    if request.user.is_resident and payment.resident.user != request.user:
        messages.error(request, "Permission denied: You can only download receipts for your own payments.")
        raise Http404("Receipt not found or permission denied.")

    pdf_buffer = generate_receipt_pdf(payment)
    response = HttpResponse(pdf_buffer, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="HMS-Receipt-{payment.receipt_number}.pdf"'
    return response


@login_required
def fee_list_view(request):
    if request.user.is_resident:
        resident = getattr(request.user, 'resident_profile', None)
        charges = ResidentCharge.objects.filter(resident=resident)
    else:
        charges = ResidentCharge.objects.select_related('resident', 'resident__user', 'fee_category').all()
        status_filter = request.GET.get('status')
        if status_filter:
            charges = charges.filter(status=status_filter)

    return render(request, 'finance/fee_list.html', {
        'charges': charges,
        'status_choices': ResidentCharge.Status.choices,
        'selected_status': request.GET.get('status'),
    })


@login_required
@accounts_or_admin_only
def create_charge_view(request):
    if request.method == 'POST':
        form = ResidentChargeForm(request.POST)
        if form.is_valid():
            charge = form.save()
            messages.success(request, f"Charge of ৳{charge.amount} assigned to {charge.resident.student_id}.")
            return redirect('finance:fee_list')
    else:
        form = ResidentChargeForm()
    return render(request, 'finance/create_charge.html', {'form': form})


@login_required
def fine_list_view(request):
    if request.user.is_resident:
        resident = getattr(request.user, 'resident_profile', None)
        fines = Fine.objects.filter(resident=resident)
    else:
        fines = Fine.objects.select_related('resident', 'resident__user', 'issued_by').all()
    return render(request, 'finance/fine_list.html', {'fines': fines})


@login_required
@role_required(['ADMIN', 'WARDEN', 'ACCOUNTS'])
def issue_fine_view(request):
    if request.method == 'POST':
        form = FineForm(request.POST)
        if form.is_valid():
            fine = form.save(commit=False)
            fine.issued_by = request.user
            fine.save()
            messages.success(request, f"Fine of ₹{fine.amount} issued to {fine.resident.student_id}.")
            return redirect('finance:fine_list')
    else:
        form = FineForm()
    return render(request, 'finance/issue_fine.html', {'form': form})


@login_required
def refund_list_view(request):
    if request.user.is_resident:
        resident = getattr(request.user, 'resident_profile', None)
        refunds = Refund.objects.filter(resident=resident)
    else:
        refunds = Refund.objects.select_related('resident', 'resident__user', 'approved_by').all()
    return render(request, 'finance/refund_list.html', {'refunds': refunds})


@login_required
@role_required(['ADMIN', 'ACCOUNTS'])
def expense_list_view(request):
    expenses = HostelExpense.objects.select_related('recorded_by').all()
    total_amount = expenses.aggregate(Sum('amount'))['amount__sum'] or 0
    return render(request, 'finance/expense_list.html', {'expenses': expenses, 'total_amount': total_amount})


@login_required
@role_required(['ADMIN', 'ACCOUNTS'])
def add_expense_view(request):
    if request.method == 'POST':
        form = HostelExpenseForm(request.POST)
        if form.is_valid():
            expense = form.save(commit=False)
            expense.recorded_by = request.user
            expense.save()
            messages.success(request, f"Expense '{expense.title}' of ₹{expense.amount} recorded.")
            return redirect('finance:expense_list')
    else:
        form = HostelExpenseForm()
    return render(request, 'finance/expense_form.html', {'form': form})
