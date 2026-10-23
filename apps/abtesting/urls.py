from django.urls import path
from . import views

app_name = 'abtesting'

urlpatterns = [
    path('', views.ab_test_dashboard_view, name='ab_dashboard'),
    path('track/', views.track_metric_event_view, name='track_metric'),
]
