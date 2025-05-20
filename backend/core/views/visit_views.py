from rest_framework import viewsets, filters
from core.models import Visit, VisitMachineRestock, RestockEntry
from core.serializers import VisitSerializer


class VisitViewSet(viewsets.ModelViewSet):
    queryset = Visit.objects.all().order_by('-visit_date')
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
        # Find all machine restocks for this visit
        machine_restocks = VisitMachineRestock.objects.filter(visit=instance)
        
        # For each machine restock, revert the inventory changes
        for restock in machine_restocks:
            restock_entries = RestockEntry.objects.filter(visit_machine_restock=restock)
            
            for entry in restock_entries:
                # Revert the current stock in the machine
                try:
                    machine_item = restock.machine.item_prices.get(product=entry.product)
                    # Remove the net change: -discarded + restocked
                    machine_item.current_stock = machine_item.current_stock - (entry.restocked - entry.discarded)
                    machine_item.save(update_fields=['current_stock', 'updated_at'])
                except restock.machine.item_prices.model.DoesNotExist:
                    pass
                
                # Return the restocked items to inventory
                entry.product.update_inventory(entry.restocked)
        
        # Delete the visit (will cascade to delete machine restocks and entries)
        instance.delete() 