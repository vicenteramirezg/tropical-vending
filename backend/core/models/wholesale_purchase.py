from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from decimal import Decimal


class WholesalePurchase(models.Model):
    product = models.ForeignKey('core.Product', on_delete=models.CASCADE, related_name='wholesale_purchases')
    quantity = models.IntegerField()
    total_cost = models.DecimalField(max_digits=10, decimal_places=2)
    purchased_at = models.DateTimeField()
    supplier = models.CharField(max_length=100, blank=True, default='')
    notes = models.TextField(blank=True, default='')
    inventory_updated = models.BooleanField(default=False, help_text="Flag to track if inventory has been updated")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.quantity} {self.product.unit_type}(s) of {self.product.name} purchased on {self.purchased_at.date()}"
    
    @property
    def unit_cost(self):
        """Calculate cost per unit"""
        return self.total_cost / self.quantity if self.quantity > 0 else Decimal('0.00')
    
    def update_inventory(self):
        """Update the product's inventory and create a cost history record"""
        if not self.inventory_updated:
            # Update product inventory
            self.product.update_inventory(self.quantity)
            
            # Create cost history record
            from core.models.product_cost import ProductCost
            
            ProductCost.objects.create(
                product=self.product,
                purchase=self,
                date=self.purchased_at,
                quantity=self.quantity,
                unit_cost=self.unit_cost,
                total_cost=self.total_cost
            )
            
            # Mark as updated to prevent duplicate updates
            self.inventory_updated = True
            self.save(update_fields=['inventory_updated', 'updated_at'])
            
            return True
        return False


@receiver(post_save, sender=WholesalePurchase)
def handle_purchase_save(sender, instance, created, **kwargs):
    """Handle inventory updates when a wholesale purchase is saved"""
    # Only update on creation to avoid duplicate updates
    if created:
        instance.update_inventory() 