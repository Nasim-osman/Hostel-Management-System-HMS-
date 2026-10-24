from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    path('login/', views.user_login_view, name='login'),
    path('logout/', views.user_logout_view, name='logout'),
    path('dashboard/', views.dashboard_router_view, name='dashboard'),
    path('dashboard/hostel/', views.hostel_management_dashboard, name='hostel_dashboard'),
    path('profile/', views.profile_view, name='profile'),
    path('password-change/', views.password_change_view, name='password_change'),
    path('users/', views.user_management_list, name='user_list'),
    path('admin/users/', views.user_management_list),
    path('users/new/', views.user_create_view, name='user_create'),
    path('users/<int:user_id>/edit/', views.user_update_view, name='user_update'),
]
