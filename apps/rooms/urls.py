from django.urls import path
from . import views

app_name = 'rooms'

urlpatterns = [
    path('', views.room_list_view, name='room_list'),
    path('new/', views.room_create_view, name='room_create'),
    path('<int:room_id>/', views.room_detail_view, name='room_detail'),
    path('<int:room_id>/edit/', views.room_edit_view, name='room_edit'),
    path('amenities/', views.amenity_list_view, name='amenity_list'),
    path('amenities/<int:amenity_id>/toggle/', views.amenity_toggle_view, name='amenity_toggle'),
]
