from django import forms
from django.db import connection

class LoginForm(forms.Form):
    username = forms.CharField()
    password = forms.CharField(widget=forms.PasswordInput)

from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import CustomUser
from pharmacies.models import Pharmacy

class AdminCreationForm(UserCreationForm):
    class Meta:
        model = CustomUser
        fields = ['username', 'first_name', 'last_name', 'email', 'password1', 'password2']

    def save(self, commit=True):
        user = super().save(commit=False)
        user.role = 'ADMIN'
        if commit:
            user.save()
        return user


from pharmacies.models import Pharmacy

# accounts/forms.py

class ManagerCreationForm(UserCreationForm):
    # Custom field that uses raw SQL to get pharmacies
    pharmacies = forms.MultipleChoiceField(
        choices=[],
        required=True,
        widget=forms.CheckboxSelectMultiple
    )

    class Meta:
        model = CustomUser
        fields = ['username', 'first_name', 'last_name', 'email', 'password1', 'password2', 'pharmacies']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Populate pharmacies choices using raw SQL
        with connection.cursor() as cursor:
            cursor.execute("SELECT id, name FROM pharmacies_pharmacy ORDER BY name")
            pharmacies_data = cursor.fetchall()
        
        self.fields['pharmacies'].choices = [(str(row[0]), row[1]) for row in pharmacies_data]

    def clean(self):
        cleaned_data = super().clean()
        print("\n=== ManagerCreationForm Clean Method ===")
        print("Cleaned data:", cleaned_data)
        
        # Validate that at least one pharmacy is selected
        pharmacies = cleaned_data.get('pharmacies')
        if not pharmacies:
            print("No pharmacies selected")
            raise forms.ValidationError("Please select at least one pharmacy")
        print("Selected pharmacies:", pharmacies)
        return cleaned_data

    def save(self, commit=True):
        print("\n=== ManagerCreationForm Save Method ===")
        user = super().save(commit=False)
        user.role = 'MANAGER'
        print("Creating manager with role:", user.role)
        
        if commit:
            try:
                user.save()
                print("User saved successfully")
                pharmacy_ids = self.cleaned_data['pharmacies']
                print("Assigning pharmacies:", pharmacy_ids)
                
                # Link pharmacies to manager using raw SQL
                with connection.cursor() as cursor:
                    for pharmacy_id in pharmacy_ids:
                        cursor.execute("""
                            INSERT INTO pharmacies_pharmacy_managers (pharmacy_id, customuser_id) 
                            VALUES (%s, %s)
                        """, [int(pharmacy_id), user.id])
                        print(f"Added manager to pharmacy ID: {pharmacy_id}")
            except Exception as e:
                print("Error in save method:", str(e))
                raise
        return user


class StaffCreationForm(UserCreationForm):
    # Custom field that uses raw SQL to get pharmacies
    assigned_pharmacy = forms.ChoiceField(
        choices=[],
        required=True
    )

    class Meta:
        model = CustomUser
        fields = ['username', 'first_name', 'last_name', 'email', 'password1', 'password2', 'assigned_pharmacy']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Populate pharmacy choices using raw SQL
        with connection.cursor() as cursor:
            cursor.execute("SELECT id, name FROM pharmacies_pharmacy ORDER BY name")
            pharmacies_data = cursor.fetchall()
        
        self.fields['assigned_pharmacy'].choices = [('', 'Select a pharmacy')] + [(str(row[0]), row[1]) for row in pharmacies_data]

    def save(self, commit=True):
        user = super().save(commit=False)
        user.role = 'STAFF'
        
        # Get pharmacy ID from form data
        pharmacy_id = self.cleaned_data.get('assigned_pharmacy')
        if pharmacy_id:
            user.assigned_pharmacy_id = int(pharmacy_id)
        
        if commit:
            user.save()
        return user
