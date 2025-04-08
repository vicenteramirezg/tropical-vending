from rest_framework import serializers
from core.models import MachineItemPrice, Product, Machine


class MachineItemPriceSerializer(serializers.ModelSerializer):
    product_name = serializers.SerializerMethodField()
    machine_info = serializers.SerializerMethodField()
    profit_margin = serializers.SerializerMethodField()
    
    class Meta:
        model = MachineItemPrice
        fields = ['id', 'machine', 'machine_info', 'product', 'product_name', 
                 'price', 'slot', 'current_stock', 'profit_margin', 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at', 'product_name', 'machine_info', 'profit_margin']
    
    def get_product_name(self, obj):
        return obj.product.name
    
    def get_machine_info(self, obj):
        return f"{obj.machine.machine_type} {obj.machine.model} at {obj.machine.location.name}"
    
    def get_profit_margin(self, obj):
        return obj.profit_margin 