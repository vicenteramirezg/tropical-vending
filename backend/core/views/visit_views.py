from rest_framework import viewsets, filters
from django.db import models
from core.models import Visit, VisitMachineRestock, RestockEntry
from core.serializers import VisitSerializer


class VisitViewSet(viewsets.ModelViewSet):
    queryset = Visit.objects.select_related('location', 'user').order_by('-visit_date')
    serializer_class = VisitSerializer
    filterset_fields = ['location', 'user']
    
    def perform_create(self, serializer):
        # If user is not provided, use the current authenticated user
        user = self.request.data.get('user')
        if not user:
            serializer.save(user=self.request.user)
        else:
            serializer.save()
            
    def perform_destroy(self, instance):
        # Find all machine restocks for this visit with optimized queries
        machine_restocks = VisitMachineRestock.objects.filter(visit=instance).prefetch_related(
            'restock_entries__product',
            'machine__item_prices'
        )
        
        # Collect all changes to apply in bulk
        inventory_updates = {}  # product_id -> quantity_change
        machine_stock_updates = []
        
        # For each machine restock, collect the inventory changes
        for restock in machine_restocks:
            for entry in restock.restock_entries.all():
                # Collect inventory changes (return restocked items)
                product_id = entry.product.id
                if product_id not in inventory_updates:
                    inventory_updates[product_id] = 0
                inventory_updates[product_id] += entry.restocked
                
                # Collect machine stock changes
                try:
                    machine_item = restock.machine.item_prices.get(product=entry.product)
                    net_change = entry.restocked - entry.discarded
                    machine_stock_updates.append({
                        'machine_item_id': machine_item.id,
                        'change': -net_change  # Revert the change
                    })
                except restock.machine.item_prices.model.DoesNotExist:
                    pass
        
        # Apply inventory updates in bulk using F expressions
        for product_id, change in inventory_updates.items():
            if change != 0:
                models.Product.objects.filter(id=product_id).update(
                    inventory_quantity=models.F('inventory_quantity') + change
                )
        
        # Apply machine stock updates in bulk
        for update in machine_stock_updates:
            models.MachineItemPrice.objects.filter(id=update['machine_item_id']).update(
                current_stock=models.F('current_stock') + update['change']
            )
        
        # Delete the visit (will cascade to delete machine restocks and entries)
        instance.delete() 