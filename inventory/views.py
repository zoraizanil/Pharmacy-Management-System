from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from pharmacies.models import Pharmacy 
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from pharmacies.forms import PharmacyForm
from pharmacies.models import Pharmacy
from django.shortcuts import render, get_object_or_404, redirect
from django.shortcuts import render, redirect
from django.shortcuts import render
from django.shortcuts import render, redirect
from django.contrib import messages
from django.http import JsonResponse
import json
from django.views.decorators.csrf import csrf_exempt
from django.contrib import messages
from django.shortcuts import redirect
from django.utils.decorators import method_decorator
from django.views import View

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

    # data = [
    #     {"id": pharmacy.id, "name": pharmacy.name}
    #     for pharmacy in pharmacies
    # ]
    return JsonResponse(pharmacies, safe=False)