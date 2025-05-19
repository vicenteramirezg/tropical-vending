from django.db import models
from decimal import Decimal


class ProductCost(models.Model):
    """
    Tracks historical product costs over time.
    Each record represents a change in product cost, typically from a wholesale purchase.
    """
    product = models.ForeignKey('core.Product', on_delete=models.CASCADE, related_name='cost_history')
    purchase = models.ForeignKey('core.WholesalePurchase', on_delete=models.CASCADE, 
                               related_name='cost_records', null=True, blank=True)
    date = models.DateTimeField()
    quantity = models.PositiveIntegerField()
    unit_cost = models.DecimalField(max_digits=10, decimal_places=2)
    total_cost = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-date']
        indexes = [
            models.Index(fields=['product', '-date']),  # For quick retrieval of latest costs
        ]
    
    def __str__(self):
        return f"{self.product.name} - {self.unit_cost} per {self.product.unit_type} on {self.date.date()}"
    
    def save(self, *args, **kwargs):
        # Auto-calculate total_cost if not provided
        if not self.total_cost:
            self.total_cost = Decimal(self.quantity) * Decimal(self.unit_cost)
        super().save(*args, **kwargs) 