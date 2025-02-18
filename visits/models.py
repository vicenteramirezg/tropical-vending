from django.db import models
from machines.models import VendingMachine

class Visit(models.Model):
    vending_machine = models.ForeignKey(VendingMachine, on_delete=models.CASCADE)
    date_visited = models.DateTimeField(auto_now_add=True)
    notes = models.TextField(blank=True)

    def __str__(self):
        return f"Visit to {self.vending_machine} on {self.date_visited}"