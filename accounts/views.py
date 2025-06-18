from django.contrib.auth import authenticate, login
from django.shortcuts import render, redirect
from .forms import LoginForm
from pharmacies.models import Pharmacy
from django.views.decorators.csrf import csrf_exempt
import json
from django.http import JsonResponse
from accounts.models import CustomUser

# def login_view(request):
#     form = LoginForm(request.POST or None)
#     error = None

#     if request.method == 'POST':
#         if form.is_valid():
#             username = form.cleaned_data['username']
#             password = form.cleaned_data['password']
#             print(f'Username entered: {username}')
#             print(f'Password entered: {password}')
#             user = authenticate(request, username=username, password=password)

#             if user is not None:
#                 login(request, user)
#                 print(f'{username} has logged in successfully.')  
#                 return redirect('dashboard')
#             else:
#                 error = "Invalid username or password"
#                 print('Authentication failed.')  

#     return render(request, 'index.html', {'form': form, 'error': error})

# from django.contrib.auth import authenticate, login
# from django.shortcuts import render, redirect
# from django.utils.http import url_has_allowed_host_and_scheme
# from django.conf import settings

# def login_view(request):
#     form = LoginForm(request.POST or None)
#     error = None

#     if request.method == 'POST':
#         if form.is_valid():
#             username = form.cleaned_data['username']
#             password = form.cleaned_data['password']
#             print(f'Username entered: {username}')
#             print(f'Password entered: {password}')
#             user = authenticate(request, username=username, password=password)

#             if user is not None:
#                 login(request, user)
#                 print(f'{username} has logged in successfully.')  
#                 next_url = request.GET.get('next')
#                 if next_url and url_has_allowed_host_and_scheme(next_url, allowed_hosts={request.get_host()}):
#                     return redirect(next_url)
#                 return redirect('dashboard')
#             else:
#                 error = "Invalid username or password"
#                 print('Authentication failed.')

#     return render(request, 'index.html', {'form': form, 'error': error})
from django.contrib.auth.decorators import login_required
@login_required
def dashboard(request):
    return render(request, 'dashboard.html')

# accounts/views.py
from django.contrib.auth import authenticate, login
from django.shortcuts import render, redirect
from .forms import LoginForm

from django.contrib.auth import authenticate, login
from django.shortcuts import render, redirect

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


from django.contrib.auth.decorators import login_required
from django.shortcuts import render



from django.contrib.auth import logout
from django.shortcuts import redirect
from django.contrib import messages

def custom_logout_view(request):
    logout(request)
    messages.success(request, "You have been logged out successfully.")
    return redirect('login') 

from django.shortcuts import render

def home(request):
    return render(request, 'home.html')


# accounts/views.py (continued)

from .forms import AdminCreationForm, ManagerCreationForm, StaffCreationForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from pharmacies.models import Pharmacy

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


from django.shortcuts import render
from django.http import JsonResponse
from accounts.models import CustomUser
from pharmacies.models import Pharmacy
import json

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


from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from pharmacies.models import  Pharmacy
import json

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



# @login_required
# def create_manager_view(request):
#     if request.method == 'POST':
#         form = ManagerCreationForm(request.POST)

#         print("Form data received:", request.POST)
#         if form.is_valid():
#             form.save()
#             return redirect('dashboard')
#     else:
#         form = ManagerCreationForm()
#     return render(request, 'accounts/create_manager.html', {'form': form})



@login_required
def admin_dashboard(request):
    return render(request, 'accounts/admin_dashboard.html')

@login_required
def manager_dashboard(request):
    return render(request, 'accounts/manager_dashboard.html')

@login_required
def sale_dashboard(request):
    return render(request, 'accounts/sale_dashboard.html')
