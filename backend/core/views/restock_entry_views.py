from rest_framework import viewsets, filters
from django.db import models
from core.models import RestockEntry
from core.serializers import RestockEntrySerializer


class RestockEntryViewSet(viewsets.ModelViewSet):
    queryset = RestockEntry.objects.select_related(
        'visit_machine_restock__visit__location',
        'visit_machine_restock__machine',
        'product'
    ).order_by('-visit_machine_restock__visit__visit_date')
    serializer_class = RestockEntrySerializer
    filterset_fields = ['visit_machine_restock', 'product']
    
    def perform_update(self, serializer):
        # Get the old instance to calculate inventory changes
        old_instance = self.get_object()
        old_restocked = old_instance.restocked
        old_discarded = old_instance.discarded
        
        # Save the new instance
        new_instance = serializer.save()
        
        # Calculate the net change in inventory
        inventory_change = old_restocked - new_instance.restocked
        
        # Use bulk update with F expressions for atomic operations
        if inventory_change != 0:
            # Update product inventory using F expression for atomic update
            models.Product.objects.filter(id=new_instance.product.id).update(
                inventory_quantity=models.F('inventory_quantity') + inventory_change
            )
            
        # Update the machine item stock using bulk operations
        try:
            machine = new_instance.visit_machine_restock.machine
            
            # Calculate the net change to be applied to current stock:
            # Subtract old values and add new values
            stock_change = (new_instance.restocked - old_restocked) - (new_instance.discarded - old_discarded)
            
            if stock_change != 0:
                # Use F expression for atomic update
                models.MachineItemPrice.objects.filter(
                    machine=machine,
                    product=new_instance.product
                ).update(
                    current_stock=models.F('current_stock') + stock_change
                )
        except Exception:
            pass  # If machine item doesn't exist, skip update 