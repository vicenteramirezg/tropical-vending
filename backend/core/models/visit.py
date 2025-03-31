from django.db import models
from django.contrib.auth.models import User


class Visit(models.Model):
    location = models.ForeignKey('core.Location', on_delete=models.CASCADE, related_name='visits')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='visits')
    visit_date = models.DateTimeField()
    notes = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Visit to {self.location.name} on {self.visit_date.date()}" 