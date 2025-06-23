from django.urls import path
from . import views

urlpatterns = [
    path('sales/', views.sales_view, name='sales_view'),
    path('api/sales/', views.get_sales_data, name='get_sales_data'),
    path('submit-sale/', views.submit_sale, name='submit_sale'),
]
