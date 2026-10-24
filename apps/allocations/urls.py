from django.urls import path
from . import views

app_name = 'allocations'

urlpatterns = [
    path('applications/', views.application_list_view, name='application_list'),
    path('applications/apply/', views.apply_seat_view, name='apply_seat'),
    path('apply/', views.apply_seat_view),
    path('track/', views.track_application_view, name='track_application'),
    path('applications/<int:app_id>/review/', views.review_application_view, name='review_application'),
    path('applications/<int:app_id>/allocate/', views.allocate_bed_view, name='allocate_bed'),
    path('waiting-list/', views.waiting_list_view, name='waiting_list'),
    path('transfers/', views.transfer_list_view, name='transfer_list'),
    path('transfers/request/', views.request_transfer_view, name='request_transfer'),
    path('transfers/<int:transfer_id>/process/', views.process_transfer_view, name='process_transfer'),
    path('clearance/', views.clearance_list_view, name='clearance_list'),
    path('clearances/', views.clearance_list_view),
    path('clearance/request/', views.request_clearance_view, name='request_clearance'),
    path('clearance/<int:clearance_id>/approve-step/', views.approve_clearance_step_view, name='approve_clearance_step'),
]
