from django.urls import path
from . import views

app_name = 'notices'

urlpatterns = [
    path('', views.notice_list_view, name='notice_list'),
    path('new/', views.notice_create_view, name='notice_create'),
    path('<int:notice_id>/', views.notice_detail_view, name='notice_detail'),
    path('<int:notice_id>/edit/', views.notice_edit_view, name='notice_edit'),
]
