from rest_framework import viewsets, filters
from core.models import RestockEntry
from core.serializers import RestockEntrySerializer


class RestockEntryViewSet(viewsets.ModelViewSet):
    queryset = RestockEntry.objects.all().order_by('-visit_machine_restock__visit__visit_date')
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
        
        if inventory_change != 0:
            # Update product inventory based on the change
            new_instance.product.update_inventory(inventory_change)
            
        # Update the machine item stock
        try:
            machine = new_instance.visit_machine_restock.machine
            machine_item = machine.item_prices.get(product=new_instance.product)
            
            # Calculate the net change to be applied to current stock:
            # Subtract old values and add new values
            stock_change = (new_instance.restocked - old_restocked) - (new_instance.discarded - old_discarded)
            
            machine_item.current_stock = machine_item.current_stock + stock_change
            machine_item.save(update_fields=['current_stock', 'updated_at'])
        except machine.item_prices.model.DoesNotExist:
            pass 