from django.db import models


class VisitMachineRestock(models.Model):
    visit = models.ForeignKey('core.Visit', on_delete=models.CASCADE, related_name='machine_restocks')
    machine = models.ForeignKey('core.Machine', on_delete=models.CASCADE, related_name='restocks')
    notes = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('visit', 'machine')
        
    def __str__(self):
        return f"Restock for {self.machine} during {self.visit}" 