from django.urls import path
from . import views

app_name = 'dining'

urlpatterns = [
    path('', views.meal_menu_view, name='meal_menu'),
    path('<int:meal_id>/edit/', views.edit_menu_view, name='edit_menu'),
    path('feedback/', views.submit_feedback_view, name='submit_feedback'),
]
