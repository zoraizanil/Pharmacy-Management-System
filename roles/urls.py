# accounts/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('api/managers/', views.get_all_managers, name='managers'),
    path('managers/', views.managers_view, name='managers_view'),
    path('api/staff/', views.get_all_staff, name='staff'),
    path('staff/', views.staff_view, name='staff_view'),
]
