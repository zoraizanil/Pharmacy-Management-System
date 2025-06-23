from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.http import JsonResponse
from django.http import HttpResponse
import pandas as pd
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt  
from django.core.files.storage import FileSystemStorage
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.http import require_POST
# from .models import InventoryUpload
import openpyxl
import datetime
from django.db import connection

@login_required
def inventory_view(request):
    # Get all pharmacies using raw SQL
    with connection.cursor() as cursor:
        cursor.execute("SELECT id, name, location FROM pharmacies_pharmacy")
        pharmacies_data = cursor.fetchall()
    
    pharmacies = [{'id': row[0], 'name': row[1], 'location': row[2]} for row in pharmacies_data]
    return render(request, 'inventory/inventory.html', {
        'pharmacies': pharmacies
    })

@login_required
def see_inventory_view(request):
    # Get all pharmacies using raw SQL
    with connection.cursor() as cursor:
        cursor.execute("SELECT id, name, location FROM pharmacies_pharmacy")
        pharmacies_data = cursor.fetchall()
    
    pharmacies = [{'id': row[0], 'name': row[1], 'location': row[2]} for row in pharmacies_data]
    return render(request, 'inventory/see_inventory.html', {
        'pharmacies': pharmacies
    })

def pharmacy_list_api(request):
    user = request.user
    pharmacies_data = []

    with connection.cursor() as cursor:
        if user.is_superuser or user.role == 'ADMIN':
            cursor.execute("SELECT id, name, location FROM pharmacies_pharmacy")
            pharmacies_data = cursor.fetchall()
        elif user.role == 'MANAGER':
            # Get pharmacies managed by this user
            cursor.execute("""
                SELECT p.id, p.name, p.location 
                FROM pharmacies_pharmacy p
                INNER JOIN pharmacies_pharmacy_managers pm ON p.id = pm.pharmacy_id
                WHERE pm.customuser_id = %s
            """, [user.id])
            pharmacies_data = cursor.fetchall()

    # ✅ Convert queryset to list of dicts
    data = [
        {"id": row[0], "name": row[1], "location": row[2]}
        for row in pharmacies_data
    ]
    return JsonResponse(data, safe=False)

@login_required
def get_inventory_by_pharmacy(request):
    pharmacy_id = request.GET.get('pharmacy_id')
    user = request.user
    print(f"[DEBUG] User: {user}, pharmacy_id: {pharmacy_id}")
    inventory_items = []
    
    with connection.cursor() as cursor:
        if pharmacy_id:
            cursor.execute("""
                SELECT i.PRD_code, i.MED_NAME, p.name as pharmacy_name, p.location, i.QTY, i.PRICE, i.MANUFACTURE_DATE, i.EXPIRY_DATE
                FROM inventory i
                JOIN pharmacies_pharmacy p ON i.ID = p.id
                WHERE i.ID = %s
            """, [pharmacy_id])
            inventory_items = cursor.fetchall()
        else:
            assigned_pharmacy_ids = set()
            cursor.execute("SELECT assigned_pharmacy_id FROM accounts_customuser WHERE id = %s", [user.id])
            assigned_pharmacy_result = cursor.fetchone()
            if assigned_pharmacy_result and assigned_pharmacy_result[0]:
                assigned_pharmacy_ids.add(assigned_pharmacy_result[0])
            cursor.execute("""
                SELECT pharmacy_id 
                FROM pharmacies_pharmacy_managers 
                WHERE customuser_id = %s
            """, [user.id])
            managed_pharmacies = cursor.fetchall()
            assigned_pharmacy_ids.update([row[0] for row in managed_pharmacies])
            if user.is_superuser or user.role == 'ADMIN':
                cursor.execute("SELECT id FROM pharmacies_pharmacy")
                all_pharmacies = cursor.fetchall()
                assigned_pharmacy_ids.update([row[0] for row in all_pharmacies])
            print(f"[DEBUG] Assigned pharmacy IDs: {assigned_pharmacy_ids}")
            if assigned_pharmacy_ids:
                placeholders = ','.join(['%s'] * len(assigned_pharmacy_ids))
                cursor.execute(f"""
                    SELECT i.PRD_code, i.MED_NAME, p.name as pharmacy_name, p.location, i.QTY, i.PRICE, i.MANUFACTURE_DATE, i.EXPIRY_DATE
                    FROM inventory i
                    JOIN pharmacies_pharmacy p ON i.ID = p.id
                    WHERE i.ID IN ({placeholders})
                """, list(assigned_pharmacy_ids))
                inventory_items = cursor.fetchall()
    print(f"[DEBUG] Inventory items count: {len(inventory_items)}")
    data = [
        {
            'prd_code': item[0],
            'name': item[1],
            'pharmacy_name': item[2],
            'location': item[3],
            'qty': item[4],
            'price': item[5],
            'manufacturedate': item[6],
            'expirydate': item[7],
        }
        for item in inventory_items
    ]
    print(f"[DEBUG] Data sent to frontend: {data}")
    return JsonResponse({'success': True, 'data': data})

from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
import openpyxl
from datetime import date

@require_POST
@login_required
def upload_inventory_excel(request):
    file = request.FILES.get('uploaded_file')
    if not file or not file.name.endswith('.xlsx'):
        return JsonResponse({'success': False, 'message': 'Please upload a valid .xlsx file.'})

    try:
        wb = openpyxl.load_workbook(file)
        ws = wb.active
        rows = list(ws.iter_rows(min_row=2, values_only=True))  # Skip header

        pharmacy_id = int(request.POST.get("pharmacy_id", 0))
        pharmacy_name = request.POST.get("pharmacy_name", "")

        if not pharmacy_id or not pharmacy_name:
            return JsonResponse({'success': False, 'message': 'Pharmacy selection is required.'})

        uploaded_data = []

        with connection.cursor() as cursor:
            for row in rows:
                if not row or len(row) < 6:
                    continue  # Skip invalid rows

                # Insert inventory item using raw SQL
                cursor.execute("""
                    INSERT INTO inventory 
                    (PRD_code, MED_NAME, QTY, PRICE, MANUFACTURE_DATE, EXPIRY_DATE, ID, PHARMACY_NAME, LOADED_DATE, LOADED_BY_USER)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """, [
                    str(row[0]) if row[0] else '',
                    str(row[1]) if row[1] else '',
                    int(row[2]) if row[2] else 0,
                    int(row[3]) if row[3] else 0,
                    row[4] if row[4] else None,
                    row[5] if row[5] else None,
                    pharmacy_id,
                    pharmacy_name,
                    date.today(),
                    request.user.id,
                ])

                uploaded_data.append({
                    "MED_NAME": str(row[1]) if row[1] else '',
                    "QTY": int(row[2]) if row[2] else 0,
                    "PRICE": int(row[3]) if row[3] else 0
                })

        return JsonResponse({
            'success': True,
            'message': f'{len(uploaded_data)} inventory items uploaded successfully.',
            'data': uploaded_data
        })

    except Exception as e:
        return JsonResponse({'success': False, 'message': f'Error: {str(e)}'})

