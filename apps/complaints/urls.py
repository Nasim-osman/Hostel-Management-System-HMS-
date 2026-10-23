from django.urls import path
from . import views

app_name = 'complaints'

urlpatterns = [
    path('', views.complaint_list_view, name='complaint_list'),
    path('submit/', views.submit_complaint_view, name='submit_complaint'),
    path('dashboard/', views.maintenance_dashboard_view, name='maintenance_dashboard'),
    path('<int:ticket_id>/', views.complaint_detail_view, name='complaint_detail'),
    path('<int:ticket_id>/assign/', views.assign_complaint_view, name='assign_complaint'),
    path('<int:ticket_id>/resolve/', views.resolve_complaint_view, name='resolve_complaint'),
]
