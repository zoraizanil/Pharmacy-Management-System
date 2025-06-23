from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .forms import PharmacyForm
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
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import connection



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

        # Create pharmacy using raw SQL
        with connection.cursor() as cursor:
            cursor.execute("""
                INSERT INTO pharmacies_pharmacy (name, location, created_by_id, is_superuser_created)
                VALUES (%s, %s, %s, %s)
            """, [name, location, request.user.id, request.user.is_superuser])
            
            # Get the created pharmacy ID
            cursor.execute("SELECT TOP 1 id FROM pharmacies_pharmacy WHERE name = %s AND location = %s ORDER BY id DESC", [name, location])
            pharmacy_id = cursor.fetchone()[0]

        return JsonResponse({'success': True, 'pharmacy_id': pharmacy_id})

@csrf_exempt
def get_pharmacies(request):
    print("I'm called")
    # Get all pharmacies using raw SQL
    with connection.cursor() as cursor:
        cursor.execute("SELECT id, name, location FROM pharmacies_pharmacy")
        pharmacies_data = cursor.fetchall()
    
    data = [{"id": row[0], "name": row[1], "location": row[2]} for row in pharmacies_data]
    print("here is the data", data)
    return JsonResponse(data, safe=False)

from django.http import JsonResponse

def pharmacy_list_api(request):
    user = request.user
    pharmacies_query_data = []

    with connection.cursor() as cursor:
        if user.is_superuser or getattr(user, 'role', None) == 'ADMIN':
            cursor.execute("SELECT id, name, location FROM pharmacies_pharmacy")
            pharmacies_query_data = cursor.fetchall()
        elif getattr(user, 'role', None) == 'MANAGER':
            # Get pharmacies managed by this user
            cursor.execute("""
                SELECT p.id, p.name, p.location 
                FROM pharmacies_pharmacy p
                INNER JOIN pharmacies_pharmacy_managers pm ON p.id = pm.pharmacy_id
                WHERE pm.customuser_id = %s
            """, [user.id])
            pharmacies_query_data = cursor.fetchall()
        else:
            # For staff, show only their single assigned pharmacy
            if hasattr(user, 'assigned_pharmacy') and user.assigned_pharmacy:
                cursor.execute("SELECT id, name, location FROM pharmacies_pharmacy WHERE id = %s", [user.assigned_pharmacy.id])
                pharmacies_query_data = cursor.fetchall()

    data = [
        {"id": row[0], "name": row[1], "location": row[2]}
        for row in pharmacies_query_data
    ]
    
    # Return in a structured format that the frontend expects
    return JsonResponse({"success": True, "pharmacies": data})






@login_required
def pharmacy_list_view(request):
    # Superuser can see all, others only their created ones
    with connection.cursor() as cursor:
        if request.user.is_superuser or request.user.role == 'ADMIN':
            cursor.execute("SELECT id, name, location FROM pharmacies_pharmacy")
        else:
            cursor.execute("SELECT id, name, location FROM pharmacies_pharmacy WHERE created_by_id = %s", [request.user.id])
        
        pharmacies_data = cursor.fetchall()

    pharmacies = [{'id': row[0], 'name': row[1], 'location': row[2]} for row in pharmacies_data]
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

class DeletePharmacyView(LoginRequiredMixin, View):
    def get(self, request):
        print("✅ DELETE view hit 1")
        # Get all pharmacies using raw SQL
        with connection.cursor() as cursor:
            cursor.execute("SELECT id, name, location FROM pharmacies_pharmacy")
            pharmacies_data = cursor.fetchall()
        
        pharmacies = [{'id': row[0], 'name': row[1], 'location': row[2]} for row in pharmacies_data]
        
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

            # Support multiple IDs (comma-separated string)
            if isinstance(pharmacy_id, str) and ',' in pharmacy_id:
                ids = [int(pid) for pid in pharmacy_id.split(',') if pid.strip().isdigit()]
            else:
                ids = [int(pharmacy_id)] if str(pharmacy_id).isdigit() else []

            if not ids:
                return JsonResponse({'success': False, 'error': 'Invalid pharmacy ID(s)'}, status=400)

            deleted_count = 0
            with connection.cursor() as cursor:
                for pid in ids:
                    try:
                        # Check if pharmacy exists and get creator info
                        cursor.execute("SELECT created_by_id FROM pharmacies_pharmacy WHERE id = %s", [pid])
                        pharmacy_result = cursor.fetchone()
                        
                        if pharmacy_result:
                            created_by_id = pharmacy_result[0]
                            # Optional: Only allow owner/superuser to delete
                            if request.user.id != created_by_id and not request.user.is_superuser:
                                continue  # skip unauthorized
                            
                            # Delete pharmacy using raw SQL
                            cursor.execute("DELETE FROM pharmacies_pharmacy WHERE id = %s", [pid])
                            deleted_count += 1
                    except Exception:
                        continue

            if deleted_count == 0:
                return JsonResponse({'success': False, 'error': 'No pharmacies deleted (not found or no permission)'}, status=404)

            return JsonResponse({'success': True, 'message': f'{deleted_count} pharmacy(s) deleted.'})
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
#         pharmacy = Pharmacy.objects.get(pk=pk)
#         pharmacy.delete()
#         return JsonResponse({"message": "Pharmacy deleted successfully."})
#     except Pharmacy.DoesNotExist:
#         return JsonResponse({"error": "Pharmacy not found."}, status=404)
#     return JsonResponse({"error": "Invalid request method."}, status=405)
