from django.contrib.auth import authenticate, login,logout,get_user_model
from django.shortcuts import render, redirect
from .forms import LoginForm
from pharmacies.models import Pharmacy
from django.views.decorators.csrf import csrf_exempt
import json
from django.http import JsonResponse
from accounts.models import CustomUser
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import AdminCreationForm, ManagerCreationForm, StaffCreationForm
from pharmacies.models import Pharmacy


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
                return redirect('dashboard')  # ✅ Always one dashboard
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


#usercreation starts from here 

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

            if CustomUser.objects.filter(username=username).exists():
                return JsonResponse({'success': False, 'error': 'Username already exists'}, status=400)

            user = CustomUser.objects.create_user(
                username=username,
                first_name=first_name,
                last_name=last_name,
                email=email,
                password=password1,
                role='ADMIN'
            )

            print(f"✅ Created admin user: {user.username} (ID: {user.id})")
            return JsonResponse({'success': True, 'message': 'Admin created successfully'})

        except Exception as e:
            print("❌ Exception occurred:", str(e))
            return JsonResponse({'success': False, 'error': str(e)}, status=500)

    return JsonResponse({'error': 'Method not allowed'}, status=405)




def create_manager_view(request):
    if request.method == 'GET':
        pharmacies = Pharmacy.objects.all()
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

            if CustomUser.objects.filter(username=username).exists():
                return JsonResponse({'success': False, 'error': 'Username already exists'}, status=400)

            user = CustomUser.objects.create_user(
                username=username,
                first_name=first_name,
                last_name=last_name,
                email=email,
                password=password1,
                role='MANAGER'
            )

            print(f"✅ Created user: {user.username} (ID: {user.id})")

            for pid in pharmacy_ids:
                try:
                    pharmacy = Pharmacy.objects.get(id=int(pid))
                    pharmacy.managers.add(user)
                except (Pharmacy.DoesNotExist, ValueError) as err:
                    print(f"⚠️ Skipping invalid pharmacy ID {pid}: {err}")

                print(f"🔗 Linked pharmacy ID {pharmacy.id} - {pharmacy.name} to user {user.username}")

            return JsonResponse({'success': True, 'message': 'Manager created successfully'})

        except Exception as e:
            print("❌ Exception occurred:", str(e))
            return JsonResponse({'success': False, 'error': str(e)}, status=500)


@csrf_exempt
def create_staff_view(request):
    if request.method == 'GET':
        pharmacies = Pharmacy.objects.all()
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

            if CustomUser.objects.filter(username=username).exists():
                return JsonResponse({'success': False, 'error': 'Username already exists'}, status=400)

            user = CustomUser.objects.create_user(
                username=username,
                first_name=first_name,
                last_name=last_name,
                email=email,
                password=password1,
                role='STAFF'
            )

            print(f"✅ Created staff user: {user.username} (ID: {user.id})")

            for pid in pharmacy_ids:
                pharmacy = Pharmacy.objects.get(id=pid)
                pharmacy.staff.add(user)  # assuming staff is a ManyToManyField
                print(f"🔗 Linked pharmacy ID {pharmacy.id} - {pharmacy.name} to staff {user.username}")

            return JsonResponse({'success': True, 'message': 'Staff created successfully'})

        except Exception as e:
            print("❌ Exception occurred:", str(e))
            return JsonResponse({'success': False, 'error': str(e)}, status=500)

    return JsonResponse({'error': 'Method not allowed'}, status=405)

