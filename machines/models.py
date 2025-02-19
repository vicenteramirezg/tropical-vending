from django.db import models

class Location(models.Model):
    name = models.CharField(max_length=100)
    address = models.TextField()

    def __str__(self):
        return self.name

class VendingMachine(models.Model):
    location = models.ForeignKey(Location, on_delete=models.CASCADE, related_name='machines')
    name = models.CharField(max_length=100)
    last_visited = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return self.name