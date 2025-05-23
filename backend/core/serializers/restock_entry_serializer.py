from rest_framework import serializers
from core.models import RestockEntry, MachineItemPrice


class RestockEntrySerializer(serializers.ModelSerializer):
    product_name = serializers.SerializerMethodField()
    machine_info = serializers.SerializerMethodField()
    visit_date = serializers.SerializerMethodField()
    slot = serializers.SerializerMethodField()
    
    class Meta:
        model = RestockEntry
        fields = ['id', 'visit_machine_restock', 'product', 'product_name', 
                 'machine_info', 'visit_date', 'slot', 'stock_before', 'discarded', 'restocked', 
                 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at', 'product_name', 'machine_info', 'visit_date', 'slot']
    
    def get_product_name(self, obj):
        return obj.product.name
    
    def get_machine_info(self, obj):
        machine = obj.visit_machine_restock.machine
        return f"{machine.machine_type} {machine.model} at {machine.location.name}"
    
    def get_visit_date(self, obj):
        return obj.visit_machine_restock.visit.visit_date
        
    def get_slot(self, obj):
        """Get the slot number for this product in the machine"""
        try:
            machine = obj.visit_machine_restock.machine
            machine_item = MachineItemPrice.objects.get(machine=machine, product=obj.product)
            return machine_item.slot
        except MachineItemPrice.DoesNotExist:
            return None 