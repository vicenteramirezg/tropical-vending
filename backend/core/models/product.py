from django.db import models
from decimal import Decimal


class Product(models.Model):
    PRODUCT_TYPES = (
        ('Soda', 'Soda'),
        ('Snack', 'Snack'),
    )
    
    name = models.CharField(max_length=100, db_index=True)
    product_type = models.CharField(max_length=20, choices=PRODUCT_TYPES, default='Soda', db_index=True)
    unit_type = models.CharField(max_length=50, default='unit', blank=True)  # Made optional with default
    image_url = models.URLField(max_length=255, null=True, blank=True)
    inventory_quantity = models.PositiveIntegerField(default=0, help_text="Current quantity in inventory")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [
            models.Index(fields=['name', 'product_type']),  # Composite index for common queries
            models.Index(fields=['created_at']),  # For sorting by creation date
        ]

    def __str__(self):
        return self.name
    
    def update_inventory(self, quantity_change):
        """
        Update inventory by adding the specified quantity.
        Use negative values for reductions (e.g., when stocking machines).
        """
        # Prevent negative inventory (unless it's an adjustment)
        if self.inventory_quantity + quantity_change < 0:
            raise ValueError("Cannot reduce inventory below zero")
            
        self.inventory_quantity += quantity_change
        self.save(update_fields=['inventory_quantity', 'updated_at'])
        
        return self.inventory_quantity
    
    @property
    def average_cost(self):
        """Calculate average cost of this product based on wholesale purchases"""
        purchases = self.wholesale_purchases.all()
        if not purchases:
            return Decimal('0.00')
        
        total_quantity = sum(purchase.quantity for purchase in purchases)
        total_cost = sum(purchase.total_cost for purchase in purchases)
        
        return Decimal(total_cost / total_quantity) if total_quantity > 0 else Decimal('0.00')
    
    @property
    def latest_unit_cost(self):
        """Get the most recent unit cost based on ProductCost entries"""
        latest_cost = self.cost_history.order_by('-date').first()
        return latest_cost.unit_cost if latest_cost else Decimal('0.00') 