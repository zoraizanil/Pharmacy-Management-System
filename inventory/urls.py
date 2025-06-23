from django.urls import path
from . import views
from pharmacies.views import pharmacy_list_api as shared_pharmacy_list_api

urlpatterns = [
    # ... other routes
    path('inv/', views.inventory_view, name='inventory'),
    path('api/pharmacies/', shared_pharmacy_list_api, name='get_pharmacies'),
    path('upload-inventory-excel/', views.upload_inventory_excel, name='upload_inventory_excel'),
    path('see-inventory/', views.see_inventory_view, name='see_inventory'),
    path('api/inventory/', views.get_inventory_by_pharmacy, name='get_inventory_by_pharmacy'),
]