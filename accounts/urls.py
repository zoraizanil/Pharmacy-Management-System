# accounts/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('', views.login_view, name='login'),
    path('dashboard', views.dashboard, name='dashboard'),
    path('logout/', views.custom_logout_view, name='log_out'),
    # path('home', views.home, name='home'),
    path('home-page/', views.home, name='home'),
    # User creation
    path('create-admin/', views.create_admin_view, name='create_admin'),
    path('create-manager/', views.create_manager_view, name='create_manager'),
    path('create-staff/', views.create_staff_view, name='create_staff'),
    path('staff-dashboard/', views.staff_dashboard, name='staff_dashboard'),
]
