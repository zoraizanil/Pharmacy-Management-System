from django.db import models

class AllStaffV(models.Model):
    staff_name = models.CharField(max_length=255)
    date_joined = models.DateField()
    email = models.EmailField()
    name = models.CharField(max_length=255)       # Assuming 'name' is for pharmacy/hospital/etc.
    location = models.CharField(max_length=255)
    phm_id = models.IntegerField()

    class Meta:
        managed = False  # Since it's a DB View, Django should not try to create/alter it
        db_table = 'All_staff_V'  # Exact name of the view in your database


from django.db import models

class AllManagersV(models.Model):
    manager_name = models.CharField(max_length=255)
    date_joined = models.DateField()
    email = models.EmailField()
    name = models.CharField(max_length=255)     # Possibly branch/pharmacy name
    location = models.CharField(max_length=255)

    class Meta:
        managed = False  # Django will not try to create or modify this view
        db_table = 'All_managers_V'
