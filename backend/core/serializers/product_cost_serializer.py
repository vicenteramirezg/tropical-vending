from rest_framework import serializers
from core.models import ProductCost


class ProductCostSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source='product.name', read_only=True)
    unit_type = serializers.CharField(source='product.unit_type', read_only=True)
    supplier = serializers.CharField(source='purchase.supplier', read_only=True, default='N/A')
    purchase_notes = serializers.CharField(source='purchase.notes', read_only=True, default='')
    
    class Meta:
        model = ProductCost
        fields = [
            'id', 'product', 'product_name', 'unit_type', 
            'date', 'quantity', 'unit_cost', 'total_cost', 
            'purchase', 'supplier', 'purchase_notes', 'created_at'
        ]
        read_only_fields = ['id', 'created_at'] 