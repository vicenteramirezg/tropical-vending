from django.db import models


class Product(models.Model):
    PRODUCT_TYPES = (
        ('Soda', 'Soda'),
        ('Snack', 'Snack'),
    )
    
    name = models.CharField(max_length=100)
    product_type = models.CharField(max_length=20, choices=PRODUCT_TYPES, default='Soda')
    unit_type = models.CharField(max_length=50, default='unit', blank=True)  # Made optional with default
    image_url = models.URLField(max_length=255, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name
    
    @property
    def average_cost(self):
        """Calculate average cost of this product based on wholesale purchases"""
        purchases = self.wholesale_purchases.all()
        if not purchases:
            return 0
        
        total_quantity = sum(purchase.quantity for purchase in purchases)
        total_cost = sum(purchase.total_cost for purchase in purchases)
        
        return total_cost / total_quantity if total_quantity > 0 else 0 