from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from pharmacies.models import Pharmacy 
from django.http import JsonResponse

@login_required
def inventory_view(request):
    pharmacies = Pharmacy.objects.all()
    return render(request, 'inventory/inventory.html', {
        'pharmacies': pharmacies
    })



def pharmacy_list_api(request):
    user = request.user

    if user.is_superuser or user.role == 'ADMIN':
        pharmacies = Pharmacy.objects.all()
    elif user.role == 'MANAGER':
        pharmacies = user.managed_pharmacies.all()
    else:
        pharmacies = Pharmacy.objects.none()

    # ✅ Convert queryset to list of dicts
    data = [
        {"id": pharmacy.id, "name": pharmacy.name, "location": pharmacy.location}
        for pharmacy in pharmacies
    ]
    return JsonResponse(data, safe=False)