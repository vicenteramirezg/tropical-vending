from django.db import models


class Machine(models.Model):
    MACHINE_TYPE_CHOICES = [
        ('Snack', 'Snack'),
        ('Soda', 'Soda'),
        ('Combo', 'Combo'),
    ]

    name = models.CharField(max_length=100)
    location = models.ForeignKey('core.Location', on_delete=models.CASCADE, related_name='machines')
    machine_type = models.CharField(max_length=100, choices=MACHINE_TYPE_CHOICES)
    model = models.CharField(max_length=100, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} - {self.machine_type} at {self.location.name}" 