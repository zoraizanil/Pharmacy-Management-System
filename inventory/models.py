from django.db import models
from django.conf import settings

class Inventory(models.Model):
    PRD_code = models.CharField(max_length=255)
    MED_NAME = models.CharField(max_length=255)
    QTY = models.BigIntegerField()
    PRICE = models.IntegerField()
    MANUFACTURE_DATE = models.DateField()
    EXPIRY_DATE = models.DateField()
    ID = models.BigIntegerField(primary_key=True)
    PHARMACY_NAME = models.CharField(max_length=255)
    LOADED_DATE = models.DateField()
    LOADED_BY_USER = models.BigIntegerField()

    class Meta:
        managed = False
        db_table = 'inventory'

    def __str__(self):
        return f"{self.MED_NAME} ({self.PRD_code})"
