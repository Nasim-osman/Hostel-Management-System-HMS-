from django.urls import path
from . import views

app_name = 'residents'

urlpatterns = [
    path('', views.resident_list_view, name='resident_list'),
    path('new/', views.resident_create_view, name='resident_create'),
    path('dashboard/', views.resident_dashboard_view, name='resident_dashboard'),
    path('<int:resident_id>/', views.resident_detail_view, name='resident_detail'),
    path('<int:resident_id>/edit/', views.resident_edit_view, name='resident_edit'),
]
