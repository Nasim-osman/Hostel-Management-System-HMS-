from django.urls import path
from . import views

app_name = 'finance'

urlpatterns = [
    path('dashboard/', views.accounts_dashboard_view, name='accounts_dashboard'),
    path('payments/', views.payment_list_view, name='payment_list'),
    path('payments/record/', views.record_payment_view, name='record_payment'),
    path('payments/<int:payment_id>/verify/', views.verify_payment_view, name='verify_payment'),
    path('receipts/<str:receipt_number>/download/', views.download_receipt_pdf_view, name='download_receipt'),
    path('fees/', views.fee_list_view, name='fee_list'),
    path('fees/charge/', views.create_charge_view, name='create_charge'),
    path('fines/', views.fine_list_view, name='fine_list'),
    path('fines/issue/', views.issue_fine_view, name='issue_fine'),
    path('refunds/', views.refund_list_view, name='refund_list'),
    path('expenses/', views.expense_list_view, name='expense_list'),
    path('expenses/new/', views.add_expense_view, name='add_expense'),
]
