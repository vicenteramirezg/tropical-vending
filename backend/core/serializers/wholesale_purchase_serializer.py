from rest_framework import serializers
from core.models import WholesalePurchase, Product


class WholesalePurchaseSerializer(serializers.ModelSerializer):
    product_name = serializers.SerializerMethodField()
    unit_cost = serializers.SerializerMethodField()
    
    class Meta:
        model = WholesalePurchase
        fields = ['id', 'product', 'product_name', 'quantity', 'total_cost', 
                 'unit_cost', 'purchased_at', 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at', 'product_name', 'unit_cost']
    
    def get_product_name(self, obj):
        return obj.product.name
    
    def get_unit_cost(self, obj):
        return obj.unit_cost 