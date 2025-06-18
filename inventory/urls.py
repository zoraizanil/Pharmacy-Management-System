from django.urls import path
from . import views

urlpatterns = [
    # ... other routes
    path('inv/', views.inventory_view, name='inventory'),
    path('api/pharmacies/', views.pharmacy_list_api, name='get_pharmacies'),
]