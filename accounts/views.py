from django.contrib.auth import authenticate, login,logout,get_user_model
from django.shortcuts import render, redirect
from .forms import LoginForm
from django.views.decorators.csrf import csrf_exempt
import json
from django.http import JsonResponse
from accounts.models import CustomUser
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import AdminCreationForm, ManagerCreationForm, StaffCreationForm
from django.db import connection
from django.contrib.auth.hashers import make_password
from datetime import datetime


@login_required
def dashboard(request):
    return render(request, 'dashboard.html')

def login_view(request):
    error = None

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        if username and password:
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                if hasattr(user, 'role') and user.role == 'STAFF':
                    return redirect('staff_dashboard')
                return redirect('dashboard')  
            else:
                error = "Invalid username or password"
        else:
            error = "Both fields are required"

    return render(request, 'index.html', {'error': error})



def custom_logout_view(request):
    try:

        logout(request)
        messages.success(request, "You have been logged out successfully.")
    except Exception as e:
        print(f"this is error {e}")


    return redirect('login') 

from django.shortcuts import render

def home(request):
    return render(request, 'home.html')



User = get_user_model()

@csrf_exempt
def create_admin_view(request):
    if request.method == 'GET':
        return render(request, 'accounts/create_admin.html')

    elif request.method == 'POST':
        try:
            data = json.loads(request.body)
            print("🔵 Raw data received from frontend:", data)

            username = data.get('username')
            first_name = data.get('first_name')
            last_name = data.get('last_name')
            email = data.get('email')
            password1 = data.get('password1')
            password2 = data.get('password2')

            print("📥 Parsed data:")
            print(f"  Username: {username}")
            print(f"  First Name: {first_name}")
            print(f"  Last Name: {last_name}")
            print(f"  Email: {email}")
            print(f"  Password1: {password1}")
            print(f"  Password2: {password2}")

            if not all([username, first_name, last_name, email, password1, password2]):
                return JsonResponse({'success': False, 'error': 'Missing fields'}, status=400)

            if password1 != password2:
                return JsonResponse({'success': False, 'error': 'Passwords do not match'}, status=400)

            # Check if username exists using raw SQL
            with connection.cursor() as cursor:
                cursor.execute("SELECT COUNT(*) FROM accounts_customuser WHERE username = %s", [username])
                user_exists = cursor.fetchone()[0]
                
                if user_exists:
                    return JsonResponse({'success': False, 'error': 'Username already exists'}, status=400)

                # Create user using raw SQL
                hashed_password = make_password(password1)
                cursor.execute("""
                    INSERT INTO accounts_customuser 
                    (username, first_name, last_name, email, password, role, is_staff, is_superuser, is_active, date_joined) 
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """, [username, first_name, last_name, email, hashed_password, 'ADMIN', True, True, True, datetime.now()])
                
                # Get the created user ID
                cursor.execute("SELECT id FROM accounts_customuser WHERE username = %s", [username])
                user_id = cursor.fetchone()[0]

            print(f"✅ Created admin user: {username} (ID: {user_id})")
            return JsonResponse({'success': True, 'message': 'Admin created successfully'})

        except Exception as e:
            print("❌ Exception occurred:", str(e))
            return JsonResponse({'success': False, 'error': str(e)}, status=500)

    return JsonResponse({'error': 'Method not allowed'}, status=405)




def create_manager_view(request):
    if request.method == 'GET':
        # Get all pharmacies using raw SQL
        with connection.cursor() as cursor:
            cursor.execute("SELECT id, name, location FROM pharmacies_pharmacy")
            pharmacies_data = cursor.fetchall()
        
        pharmacies = [{'id': row[0], 'name': row[1], 'location': row[2]} for row in pharmacies_data]
        
        return render(request, 'accounts/create_manager.html', {
            'pharmacies': pharmacies,
            'selected_pharmacies': [], 
        })

    elif request.method == 'POST':
        try:
            data = json.loads(request.body)
            print("🔵 Raw data received from frontend:", data)

            username = data.get('username')
            first_name = data.get('first_name')
            last_name = data.get('last_name')
            email = data.get('email')
            password1 = data.get('password1')
            password2 = data.get('password2')
            pharmacy_ids = data.get('pharmacies', [])

            print("📥 Parsed data:")
            print(f"  Username: {username}")
            print(f"  First Name: {first_name}")
            print(f"  Last Name: {last_name}")
            print(f"  Email: {email}")
            print(f"  Password1: {password1}")
            print(f"  Password2: {password2}")
            print(f"  Pharmacy IDs: {pharmacy_ids}")

            if not all([username, first_name, last_name, email, password1, password2]):
                return JsonResponse({'success': False, 'error': 'Missing fields'}, status=400)

            if password1 != password2:
                return JsonResponse({'success': False, 'error': 'Passwords do not match'}, status=400)

            # Check if username exists using raw SQL
            with connection.cursor() as cursor:
                cursor.execute("SELECT COUNT(*) FROM accounts_customuser WHERE username = %s", [username])
                user_exists = cursor.fetchone()[0]
                
                if user_exists:
                    return JsonResponse({'success': False, 'error': 'Username already exists'}, status=400)

                # Create user using raw SQL
                hashed_password = make_password(password1)
                cursor.execute("""
                    INSERT INTO accounts_customuser 
                    (username, first_name, last_name, email, password, role, is_staff, is_superuser, is_active, date_joined) 
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """, [username, first_name, last_name, email, hashed_password, 'MANAGER', True, False, True, datetime.now()])
                
                # Get the created user ID
                cursor.execute("SELECT id FROM accounts_customuser WHERE username = %s", [username])
                user_id = cursor.fetchone()[0]

                print(f"✅ Created user: {username} (ID: {user_id})")

                # Link pharmacies to manager using raw SQL
                for pid in pharmacy_ids:
                    try:
                        # Check if pharmacy exists
                        cursor.execute("SELECT id, name FROM pharmacies_pharmacy WHERE id = %s", [int(pid)])
                        pharmacy_result = cursor.fetchone()
                        
                        if pharmacy_result:
                            pharmacy_id, pharmacy_name = pharmacy_result
                            # Insert into many-to-many relationship table
                            cursor.execute("""
                                INSERT INTO pharmacies_pharmacy_managers (pharmacy_id, customuser_id) 
                                VALUES (%s, %s)
                            """, [pharmacy_id, user_id])
                            print(f"🔗 Linked pharmacy ID {pharmacy_id} - {pharmacy_name} to user {username}")
                        else:
                            print(f"⚠️ Skipping invalid pharmacy ID {pid}: Pharmacy not found")
                    except (ValueError, Exception) as err:
                        print(f"⚠️ Skipping invalid pharmacy ID {pid}: {err}")

            return JsonResponse({'success': True, 'message': 'Manager created successfully'})

        except Exception as e:
            print("❌ Exception occurred:", str(e))
            return JsonResponse({'success': False, 'error': str(e)}, status=500)


@csrf_exempt
def create_staff_view(request):
    if request.method == 'GET':
        user = request.user
        pharmacies = []
        
        with connection.cursor() as cursor:
            if user.is_superuser or (hasattr(user, 'role') and user.role == 'ADMIN'):
                cursor.execute("SELECT id, name, location FROM pharmacies_pharmacy")
                pharmacies_data = cursor.fetchall()
            elif hasattr(user, 'role') and user.role == 'MANAGER':
                # Get pharmacies managed by this user
                cursor.execute("""
                    SELECT p.id, p.name, p.location 
                    FROM pharmacies_pharmacy p
                    INNER JOIN pharmacies_pharmacy_managers pm ON p.id = pm.pharmacy_id
                    WHERE pm.customuser_id = %s
                """, [user.id])
                pharmacies_data = cursor.fetchall()
            else:
                pharmacies_data = []
        
        pharmacies = [{'id': row[0], 'name': row[1], 'location': row[2]} for row in pharmacies_data]
        
        return render(request, 'accounts/create_staff.html', {
            'pharmacies': pharmacies
        })

    elif request.method == 'POST':
        try:
            data = json.loads(request.body)
            print("🔵 Raw data received from frontend:", data)

            username = data.get('username')
            first_name = data.get('first_name')
            last_name = data.get('last_name')
            email = data.get('email')
            password1 = data.get('password1')
            password2 = data.get('password2')
            pharmacy_id = data.get('assigned_pharmacy')

            print("📥 Parsed data:")
            print(f"  Username: {username}")
            print(f"  First Name: {first_name}")
            print(f"  Last Name: {last_name}")
            print(f"  Email: {email}")
            print(f"  Password1: {password1}")
            print(f"  Password2: {password2}")
            print(f"  Pharmacy ID: {pharmacy_id}")

            if not all([username, first_name, last_name, email, password1, password2]):
                return JsonResponse({'success': False, 'error': 'Missing fields'}, status=400)

            if password1 != password2:
                return JsonResponse({'success': False, 'error': 'Passwords do not match'}, status=400)

            # Check if username exists using raw SQL
            with connection.cursor() as cursor:
                cursor.execute("SELECT COUNT(*) FROM accounts_customuser WHERE username = %s", [username])
                user_exists = cursor.fetchone()[0]
                
                if user_exists:
                    return JsonResponse({'success': False, 'error': 'Username already exists'}, status=400)

                if not pharmacy_id:
                    return JsonResponse({'success': False, 'error': 'A pharmacy must be assigned'}, status=400)

                # Check if pharmacy exists
                cursor.execute("SELECT id, name FROM pharmacies_pharmacy WHERE id = %s", [int(pharmacy_id)])
                pharmacy_result = cursor.fetchone()
                
                if not pharmacy_result:
                    return JsonResponse({'success': False, 'error': 'Invalid Pharmacy selected'}, status=400)
                
                pharmacy_id_int, pharmacy_name = pharmacy_result

                # Create user using raw SQL
                hashed_password = make_password(password1)
                cursor.execute("""
                    INSERT INTO accounts_customuser 
                    (username, first_name, last_name, email, password, role, assigned_pharmacy_id, is_staff, is_superuser, is_active, date_joined) 
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """, [username, first_name, last_name, email, hashed_password, 'STAFF', pharmacy_id_int, True, False, True, datetime.now()])
                
                # Get the created user ID
                cursor.execute("SELECT id FROM accounts_customuser WHERE username = %s", [username])
                user_id = cursor.fetchone()[0]

                print(f"✅ Created staff user: {username} (ID: {user_id})")
                print(f"🔗 Assigned pharmacy ID {pharmacy_id_int} - {pharmacy_name} to staff {username}")

            return JsonResponse({'success': True, 'message': 'Staff created successfully'})

        except Exception as e:
            print("❌ Exception occurred:", str(e))
            return JsonResponse({'success': False, 'error': str(e)}, status=500)

    return JsonResponse({'error': 'Method not allowed'}, status=405)


@login_required
def staff_dashboard(request):
    pharmacy = None
    products = []
    
    with connection.cursor() as cursor:
        # Get user's assigned pharmacy
        cursor.execute("""
            SELECT p.id, p.name, p.location 
            FROM pharmacies_pharmacy p
            INNER JOIN accounts_customuser u ON p.id = u.assigned_pharmacy_id
            WHERE u.id = %s
        """, [request.user.id])
        pharmacy_result = cursor.fetchone()
        
        if pharmacy_result:
            pharmacy = {'id': pharmacy_result[0], 'name': pharmacy_result[1], 'location': pharmacy_result[2]}
            
            # Get inventory for this pharmacy
            cursor.execute("""
                SELECT PRD_code, MED_NAME, QTY, PRICE, MANUFACTURE_DATE, EXPIRY_DATE
                FROM inventory 
                WHERE ID = %s
            """, [pharmacy['id']])
            inventory_data = cursor.fetchall()
            
            products = [
                {
                    'PRD_code': row[0],
                    'MED_NAME': row[1],
                    'QTY': row[2],
                    'PRICE': row[3],
                    'MANUFACTURE_DATE': row[4],
                    'EXPIRY_DATE': row[5]
                }
                for row in inventory_data
            ]
    
    return render(request, 'sales/sale_dashboard.html', {'pharmacy': pharmacy, 'products': products})

