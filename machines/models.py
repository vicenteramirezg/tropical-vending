from django.db import models

class Location(models.Model):
    name = models.CharField(max_length=100)
    address_1 = models.CharField(max_length=255)
    address_2 = models.CharField(max_length=255, blank=True, null=True)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    zip_code = models.CharField(max_length=20, blank=True, null=True)
    last_visited = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.name}"

class VendingMachine(models.Model):
    location = models.ForeignKey(Location, on_delete=models.CASCADE, related_name='machines')
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name