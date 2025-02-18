from django.db import models
from machines.models import VendingMachine

class Product(models.Model):
    name = models.CharField(max_length=100)
    barcode = models.CharField(max_length=20, unique=True, blank=True, null=True)

    def __str__(self):
        return self.name

class StockRecord(models.Model):
    vending_machine = models.ForeignKey(VendingMachine, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    stock_level = models.IntegerField()

    def __str__(self):
        return f"{self.product.name} at {self.vending_machine}: {self.stock_level} units"