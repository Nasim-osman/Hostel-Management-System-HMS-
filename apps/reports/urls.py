from django.urls import path
from . import views

app_name = 'reports'

urlpatterns = [
    path('', views.reports_overview_view, name='reports_overview'),
    path('export/<str:export_type>/', views.export_data_csv_view, name='export_csv'),
    path('search/', views.global_search_view, name='global_search'),
]
