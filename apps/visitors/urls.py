from django.urls import path
from . import views

app_name = 'visitors'

urlpatterns = [
    path('', views.visitor_list_view, name='visitor_list'),
    path('check-in/', views.check_in_visitor_view, name='check_in'),
    path('<int:visitor_id>/check-out/', views.check_out_visitor_view, name='check_out'),
]
