from django.db import models
from machines.models import Location, VendingMachine
from inventory.models import Product

class Visit(models.Model):
    location = models.ForeignKey(Location, on_delete=models.CASCADE, related_name='visits')
    date_visited = models.DateTimeField()  # Remove auto_now_add=True
    notes = models.TextField(blank=True)

    def __str__(self):
        return f"Visit to {self.location.name} on {self.date_visited}"

class MachineRefill(models.Model):
    visit = models.ForeignKey(Visit, on_delete=models.CASCADE, related_name='machine_refills')
    vending_machine = models.ForeignKey(VendingMachine, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    units_added = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.units_added} units of {self.product.name} added to {self.vending_machine.name}"