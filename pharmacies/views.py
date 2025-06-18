from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .forms import PharmacyForm
from .models import Pharmacy
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



class AddPharmacyView(View):
    def get(self, request):
        # Render just the form HTML
        return render(request, 'pharmacies/add_pharmacy.html')  # Create this template

    def post(self, request):
        import json
        from django.http import JsonResponse
        data = json.loads(request.body)
        name = data.get('name')
        location = data.get('location')

        if not name or not location:
            return JsonResponse({'success': False, 'error': 'Missing fields'}, status=400)

        pharmacy = Pharmacy.objects.create(
            name=name,
            location=location,
            created_by=request.user,
            is_superuser_created=request.user.is_superuser
        )

        return JsonResponse({'success': True, 'pharmacy_id': pharmacy.id})

@csrf_exempt
def get_pharmacies(request):
    print("I'm called")
    pharmacies = Pharmacy.objects.all()
    print("here is the pharmacies", pharmacies)
    data = [{"id": p.id, "name": p.name} for p in pharmacies]
    print("here is the data", data)
    return JsonResponse(data, safe=False)

from django.http import JsonResponse
from .models import Pharmacy

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






@login_required
def pharmacy_list_view(request):
    # Superuser can see all, others only their created ones
    if request.user.is_superuser or request.user.role == 'ADMIN':
        pharmacies = Pharmacy.objects.all()
    else:
        pharmacies = Pharmacy.objects.filter(created_by=request.user)

    return render(request, 'pharmacies/pharmacy_list.html', {'pharmacies': pharmacies})



from django.shortcuts import get_object_or_404


# @login_required
# def delete_pharmacy_view(request, pk):
#     pharmacy = get_object_or_404(Pharmacy, pk=pk)

#     # Only creator or superuser can delete
#     if pharmacy.created_by != request.user and not request.user.is_superuser:
#         return redirect('pharmacy_list')

#     if request.method == 'POST':
#         pharmacy.delete()
#         return redirect('pharmacy_list')

#     return render(request, 'pharmacies/delete_pharmacy_confirm.html', {'pharmacy': pharmacy})

from django.contrib.auth.mixins import LoginRequiredMixin

class DeletePharmacyView(LoginRequiredMixin, View):
    def get(self, request):
        print("✅ DELETE view hit 1")
        pharmacies = Pharmacy.objects.all()
        return render(request, 'pharmacies/delete_pharmacy.html', {
            'pharmacies': pharmacies
        })

    def post(self, request):
        print("✅ DELETE view hit 2")
        try:
            data = json.loads(request.body)
            pharmacy_id = data.get('pharmacy_id')

            if not pharmacy_id:
                return JsonResponse({'success': False, 'error': 'Missing pharmacy ID'}, status=400)

            pharmacy = Pharmacy.objects.get(id=pharmacy_id)

            # Optional: Only allow owner/superuser to delete
            if request.user != pharmacy.created_by and not request.user.is_superuser:
                return JsonResponse({'success': False, 'error': 'Permission denied'}, status=403)

            pharmacy.delete()
            return JsonResponse({'success': True})
        except Pharmacy.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Pharmacy not found'}, status=404)
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)}, status=500)
        


# from django.views.decorators.csrf import csrf_exempt

# # views.py
# from django.http import JsonResponse
# from django.views.decorators.csrf import csrf_exempt
# from .models import Pharmacy

# @csrf_exempt
# def delete_pharmacy_by_id(request, pk):
#     if request.method == "POST":
#         try:
#             pharmacy = Pharmacy.objects.get(pk=pk)
#             pharmacy.delete()
#             return JsonResponse({"message": "Pharmacy deleted successfully."})
#         except Pharmacy.DoesNotExist:
#             return JsonResponse({"error": "Pharmacy not found."}, status=404)
#     return JsonResponse({"error": "Invalid request method."}, status=405)
