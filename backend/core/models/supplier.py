from django.db import models


class Supplier(models.Model):
    name = models.CharField(max_length=100, unique=True, db_index=True, help_text="Supplier name (e.g., Walmart, Sams Club)")
    contact_person = models.CharField(max_length=100, blank=True, default='', help_text="Primary contact person")
    phone = models.CharField(max_length=20, blank=True, default='', help_text="Contact phone number")
    email = models.EmailField(blank=True, default='', help_text="Contact email address")
    address = models.TextField(blank=True, default='', help_text="Supplier address")
    notes = models.TextField(blank=True, default='', help_text="Additional notes about the supplier")
    is_active = models.BooleanField(default=True, help_text="Whether this supplier is currently active")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [
            models.Index(fields=['name']),
            models.Index(fields=['is_active']),
            models.Index(fields=['created_at']),
        ]
        ordering = ['name']

    def __str__(self):
        return self.name
    
    @property
    def purchase_count(self):
        """Return the number of wholesale purchases from this supplier"""
        return self.wholesale_purchases.count()
    
    @property
    def total_spent(self):
        """Return the total amount spent with this supplier"""
        from decimal import Decimal
        return self.wholesale_purchases.aggregate(
            total=models.Sum('total_cost')
        )['total'] or Decimal('0.00') 