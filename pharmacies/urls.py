from django.urls import path
from .views import AddPharmacyView, pharmacy_list_view, DeletePharmacyView,get_pharmacies,pharmacy_list_api

urlpatterns = [
     path('add-pharmacy/', AddPharmacyView.as_view(), name='add_pharmacy'),
    path('list/', pharmacy_list_view, name='pharmacy_list'),
    # path('delete/', delete_pharmacy, name='delete_pharmacy'),
    path("delete/", DeletePharmacyView.as_view(), name="delete_pharmacy"),
    path('api/pharmacies/', pharmacy_list_api, name='get_pharmacies'),
]
