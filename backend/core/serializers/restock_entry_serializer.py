from rest_framework import serializers
from core.models import RestockEntry, MachineItemPrice


class RestockEntrySerializer(serializers.ModelSerializer):
    product_name = serializers.SerializerMethodField()
    machine_name = serializers.SerializerMethodField()
    machine_type = serializers.SerializerMethodField()
    machine_model = serializers.SerializerMethodField()
    visit_date = serializers.SerializerMethodField()
    slot = serializers.SerializerMethodField()
    
    class Meta:
        model = RestockEntry
        fields = ['id', 'visit_machine_restock', 'product', 'product_name', 
                 'machine_name', 'machine_type', 'machine_model', 'visit_date', 'slot', 
                 'stock_before', 'discarded', 'restocked', 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at', 'product_name', 'machine_name', 
                           'machine_type', 'machine_model', 'visit_date', 'slot']
    
    def get_product_name(self, obj):
        return obj.product.name
    
    def get_machine_name(self, obj):
        return obj.visit_machine_restock.machine.name
    
    def get_machine_type(self, obj):
        return obj.visit_machine_restock.machine.machine_type
    
    def get_machine_model(self, obj):
        return obj.visit_machine_restock.machine.model or ''
    
    def get_visit_date(self, obj):
        return obj.visit_machine_restock.visit.visit_date
        
    def get_slot(self, obj):
        """Get the slot number for this product in the machine"""
        try:
            # Try to get from prefetched data first to avoid additional query
            machine = obj.visit_machine_restock.machine
            if hasattr(machine, '_prefetched_objects_cache') and 'item_prices' in machine._prefetched_objects_cache:
                # Use prefetched data if available
                for item in machine.item_prices.all():
                    if item.product_id == obj.product.id:
                        return item.slot
                return None
            else:
                # Fallback to direct query if not prefetched
                machine_item = MachineItemPrice.objects.get(machine=machine, product=obj.product)
                return machine_item.slot
        except MachineItemPrice.DoesNotExist:
            return None 