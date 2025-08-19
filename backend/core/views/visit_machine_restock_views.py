from rest_framework import viewsets, filters
from django.db import models
from core.models import VisitMachineRestock, RestockEntry
from core.serializers import VisitMachineRestockSerializer


class VisitMachineRestockViewSet(viewsets.ModelViewSet):
    queryset = VisitMachineRestock.objects.select_related(
        'visit__location',
        'machine__location'
    ).prefetch_related(
        'restock_entries__product'
    ).order_by('-visit__visit_date')
    serializer_class = VisitMachineRestockSerializer
    filterset_fields = ['visit', 'machine']
    
    def perform_destroy(self, instance):
        # Before deleting, retrieve all restock entries with optimized queries
        restock_entries = RestockEntry.objects.filter(
            visit_machine_restock=instance
        ).select_related('product')
        
        # Collect all changes to apply in bulk
        inventory_updates = {}  # product_id -> quantity_change
        machine_stock_updates = []
        
        # For each restock entry, collect the changes
        for entry in restock_entries:
            # Collect inventory changes (return restocked items)
            product_id = entry.product.id
            if product_id not in inventory_updates:
                inventory_updates[product_id] = 0
            inventory_updates[product_id] += entry.restocked
            
            # Collect machine stock changes
            try:
                net_change = entry.restocked - entry.discarded
                machine_stock_updates.append({
                    'machine_id': instance.machine.id,
                    'product_id': product_id,
                    'change': -net_change  # Revert the change
                })
            except Exception:
                pass
        
        # Apply inventory updates in bulk using F expressions
        for product_id, change in inventory_updates.items():
            if change != 0:
                models.Product.objects.filter(id=product_id).update(
                    inventory_quantity=models.F('inventory_quantity') + change
                )
        
        # Apply machine stock updates in bulk
        for update in machine_stock_updates:
            models.MachineItemPrice.objects.filter(
                machine_id=update['machine_id'],
                product_id=update['product_id']
            ).update(
                current_stock=models.F('current_stock') + update['change']
            )
        
        # Now delete the instance which will cascade to delete related entries
        instance.delete() 