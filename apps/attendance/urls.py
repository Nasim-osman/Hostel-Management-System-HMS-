from django.urls import path
from . import views

app_name = 'attendance'

urlpatterns = [
    path('', views.attendance_overview_view, name='attendance_overview'),
    path('mark/', views.mark_attendance_view, name='mark_attendance'),
    path('outpasses/', views.outpass_list_view, name='outpass_list'),
    path('outpasses/request/', views.request_outpass_view, name='request_outpass'),
    path('outpasses/<int:outpass_id>/approve/', views.approve_outpass_view, name='approve_outpass'),
]
