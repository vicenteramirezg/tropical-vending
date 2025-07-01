from django.db import models


class Location(models.Model):
    name = models.CharField(max_length=100)
    address = models.TextField()
    route = models.CharField(max_length=50, null=True, blank=True, help_text="Route designation for restocking planning")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name 