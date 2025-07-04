from django.db import models
from decimal import Decimal


class DemandTracking(models.Model):
    """
    Tracks demand per product per machine based on restock data.
    Each record represents the calculated demand between two consecutive visits.
    """
    machine = models.ForeignKey('core.Machine', on_delete=models.CASCADE, related_name='demand_records')
    product = models.ForeignKey('core.Product', on_delete=models.CASCADE, related_name='demand_records')
    
    # Previous visit data
    previous_visit = models.ForeignKey('core.Visit', on_delete=models.CASCADE, related_name='demand_records_previous')
    previous_stock_after_restock = models.IntegerField(help_text="Stock level after previous restock")
    
    # Current visit data
    current_visit = models.ForeignKey('core.Visit', on_delete=models.CASCADE, related_name='demand_records_current')
    current_stock_before_restock = models.IntegerField(help_text="Stock level before current restock")
    
    # Calculated values
    days_between_visits = models.IntegerField(help_text="Number of days between visits")
    total_consumption = models.IntegerField(help_text="Total units consumed between visits")
    daily_demand = models.DecimalField(max_digits=10, decimal_places=2, help_text="Average daily demand")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        unique_together = ('machine', 'product', 'current_visit')
        indexes = [
            models.Index(fields=['machine', 'product']),
            models.Index(fields=['current_visit']),
        ]
    
    def __str__(self):
        return f"Demand: {self.product.name} in {self.machine.name} - {self.daily_demand}/day"
    
    @classmethod
    def calculate_demand(cls, machine, product, current_visit, current_stock_before, current_stock_after):
        """
        Calculate demand between the previous visit and current visit.
        
        Args:
            machine: Machine object
            product: Product object
            current_visit: Current Visit object
            current_stock_before: Stock level before current restock
            current_stock_after: Stock level after current restock (stock_before - discarded + restocked)
        
        Returns:
            DemandTracking object or None if no previous visit found
        """
        # Find the previous visit for this machine
        previous_visits = cls.objects.filter(
            machine=machine,
            product=product,
            current_visit__visit_date__lt=current_visit.visit_date
        ).order_by('-current_visit__visit_date')
        
        if not previous_visits.exists():
            # Try to find any previous restock entry for this machine/product
            from .restock_entry import RestockEntry
            previous_entries = RestockEntry.objects.filter(
                visit_machine_restock__machine=machine,
                product=product,
                visit_machine_restock__visit__visit_date__lt=current_visit.visit_date
            ).order_by('-visit_machine_restock__visit__visit_date')
            
            if not previous_entries.exists():
                return None
            
            previous_entry = previous_entries.first()
            previous_visit = previous_entry.visit_machine_restock.visit
            previous_stock_after = previous_entry.stock_before - previous_entry.discarded + previous_entry.restocked
        else:
            # Use the most recent demand record
            previous_demand = previous_visits.first()
            previous_visit = previous_demand.current_visit
            previous_stock_after = previous_demand.current_stock_before - previous_demand.total_consumption + \
                                 (previous_demand.current_stock_before - previous_demand.previous_stock_after_restock)
        
        # Calculate days between visits
        days_between = (current_visit.visit_date.date() - previous_visit.visit_date.date()).days
        
        if days_between <= 0:
            return None
        
        # Calculate consumption
        total_consumption = previous_stock_after - current_stock_before
        
        # Ensure consumption is not negative (could happen due to data inconsistencies)
        if total_consumption < 0:
            total_consumption = 0
        
        # Calculate daily demand
        daily_demand = Decimal(total_consumption) / Decimal(days_between)
        
        # Create or update the demand record
        demand_record, created = cls.objects.update_or_create(
            machine=machine,
            product=product,
            current_visit=current_visit,
            defaults={
                'previous_visit': previous_visit,
                'previous_stock_after_restock': previous_stock_after,
                'current_stock_before_restock': current_stock_before,
                'days_between_visits': days_between,
                'total_consumption': total_consumption,
                'daily_demand': daily_demand,
            }
        )
        
        return demand_record
    
    @classmethod
    def get_average_demand(cls, machine, product, days=30):
        """
        Get average daily demand for a product in a machine over the last N days.
        
        Args:
            machine: Machine object
            product: Product object
            days: Number of days to look back (default: 30)
        
        Returns:
            Average daily demand as Decimal
        """
        from django.utils import timezone
        from datetime import timedelta
        
        cutoff_date = timezone.now() - timedelta(days=days)
        
        recent_demands = cls.objects.filter(
            machine=machine,
            product=product,
            current_visit__visit_date__gte=cutoff_date
        )
        
        if not recent_demands.exists():
            return Decimal('0.00')
        
        total_demand = sum(demand.daily_demand for demand in recent_demands)
        return total_demand / len(recent_demands)