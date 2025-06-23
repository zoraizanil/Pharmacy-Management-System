# roles/views.py
from django.http import JsonResponse
from django.shortcuts import render
from django.db import connection
from django.contrib.auth.decorators import login_required

def managers_view(request):
    return render(request, 'roles/managers.html')

def staff_view(request):
    return render(request, 'roles/staff.html')

@login_required
def get_all_managers(request):
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT Manager_name, date_joined, email, name, location 
            FROM All_managers_V
        """)
        rows = cursor.fetchall()

    data = [
        {
            'manager_name': row[0],
            'date_joined': row[1],
            'email': row[2],
            'name': row[3],
            'location': row[4]
        }
        for row in rows
    ]
    return JsonResponse(data, safe=False)

@login_required
def get_all_staff(request):
    user = request.user
    
    if user.is_superuser or user.role == 'ADMIN':
        # Admin/Superuser sees all staff
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT Staff_name, date_joined, email, name, location, phm_id 
                FROM All_staff_V
            """)
            rows = cursor.fetchall()
    elif user.role == 'MANAGER':
        # Manager sees only staff from their assigned pharmacies
        with connection.cursor() as cursor:
            # Get pharmacies managed by this user
            cursor.execute("""
                SELECT pharmacy_id 
                FROM pharmacies_pharmacy_managers 
                WHERE customuser_id = %s
            """, [user.id])
            managed_pharmacies = cursor.fetchall()
            assigned_pharmacy_ids = [row[0] for row in managed_pharmacies]
            
            if assigned_pharmacy_ids:
                placeholders = ','.join(['%s'] * len(assigned_pharmacy_ids))
                cursor.execute(f"""
                    SELECT Staff_name, date_joined, email, name, location, phm_id 
                    FROM All_staff_V 
                    WHERE phm_id IN ({placeholders})
                """, assigned_pharmacy_ids)
                rows = cursor.fetchall()
            else:
                rows = []
    else:
        # Other roles see no staff
        rows = []

    data = [
        {
            'staff_name': row[0],
            'date_joined': row[1],
            'email': row[2],
            'name': row[3],
            'location': row[4]
        }
        for row in rows
    ]
    return JsonResponse(data, safe=False)