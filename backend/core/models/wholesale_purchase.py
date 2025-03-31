from django.db import models


class WholesalePurchase(models.Model):
    product = models.ForeignKey('core.Product', on_delete=models.CASCADE, related_name='wholesale_purchases')
    quantity = models.IntegerField()
    total_cost = models.DecimalField(max_digits=10, decimal_places=2)
    purchased_at = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.quantity} {self.product.unit_type}(s) of {self.product.name} purchased on {self.purchased_at.date()}"
    
    @property
    def unit_cost(self):
        """Calculate cost per unit"""
        return self.total_cost / self.quantity if self.quantity > 0 else 0 