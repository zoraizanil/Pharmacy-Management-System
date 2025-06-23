from django.db import models

class Sale(models.Model):
    sale_id = models.CharField(max_length=255, primary_key=True)
    prd_name = models.CharField(max_length=255)
    qty = models.IntegerField()
    price = models.IntegerField()
    pharmacyid = models.IntegerField()
    staff_id = models.IntegerField()

    class Meta:
        managed = False  # Since the table is already created in the database
        db_table = 'SALE'

    def __str__(self):
        return f"{self.sale_id} - {self.prd_name}"
