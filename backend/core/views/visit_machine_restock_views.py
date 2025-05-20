from rest_framework import viewsets, filters
from core.models import VisitMachineRestock, RestockEntry
from core.serializers import VisitMachineRestockSerializer


class VisitMachineRestockViewSet(viewsets.ModelViewSet):
    queryset = VisitMachineRestock.objects.all().order_by('-visit__visit_date')
    serializer_class = VisitMachineRestockSerializer
    filterset_fields = ['visit', 'machine']
    
    def perform_destroy(self, instance):
        # Before deleting, retrieve all restock entries to revert the changes
        restock_entries = RestockEntry.objects.filter(visit_machine_restock=instance)
        
        # For each restock entry, revert the machine item stock and product inventory
        for entry in restock_entries:
            # Get the machine item to update its current stock
            try:
                machine_item = instance.machine.item_prices.get(product=entry.product)
                # Revert by removing the net change: -discarded + restocked
                machine_item.current_stock = machine_item.current_stock - (entry.restocked - entry.discarded)
                machine_item.save(update_fields=['current_stock', 'updated_at'])
            except instance.machine.item_prices.model.DoesNotExist:
                pass
            
            # Return the restocked items to inventory
            entry.product.update_inventory(entry.restocked)
        
        # Now delete the instance which will cascade to delete related entries
        instance.delete() 