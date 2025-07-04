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
    
    def get_demand_for_machine(self, machine, days=30):
        """Get average daily demand for this product in a specific machine"""
        from .demand_tracking import DemandTracking
        return DemandTracking.get_average_demand(machine, self, days)
    
    def get_total_demand_across_machines(self, days=30):
        """Get total average daily demand across all machines"""
        from .demand_tracking import DemandTracking
        from django.utils import timezone
        from datetime import timedelta
        
        cutoff_date = timezone.now() - timedelta(days=days)
        
        recent_demands = DemandTracking.objects.filter(
            product=self,
            current_visit__visit_date__gte=cutoff_date
        )
        
        if not recent_demands.exists():
            return Decimal('0.00')
        
        # Group by machine and get the latest demand for each
        machine_demands = {}
        for demand in recent_demands:
            machine_id = demand.machine_id
            if machine_id not in machine_demands:
                machine_demands[machine_id] = demand.daily_demand
            else:
                # Keep the most recent demand for this machine
                if demand.current_visit.visit_date > machine_demands[machine_id].current_visit.visit_date:
                    machine_demands[machine_id] = demand.daily_demand
        
        # Sum up all machine demands
        total_demand = sum(machine_demands.values())
        return total_demand
    
    def get_recommended_stock_level(self, machine, days_ahead=7):
        """Get recommended stock level based on demand patterns"""
        daily_demand = self.get_demand_for_machine(machine, days=30)
        
        # Add a 20% buffer for safety stock
        recommended_level = int(float(daily_demand) * days_ahead * 1.2)
        
        # Get machine capacity (max stock level)
        try:
            machine_item = machine.item_prices.get(product=self)
            # If we don't have a max capacity, use a reasonable default
            max_capacity = getattr(machine_item, 'max_stock', 50)  # Default to 50 if not set
            
            # Don't exceed machine capacity
            recommended_level = min(recommended_level, max_capacity)
        except:
            # If product isn't in machine, return 0
            recommended_level = 0
        
        return max(recommended_level, 0) 