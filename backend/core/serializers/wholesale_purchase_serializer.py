from rest_framework import serializers
from core.models import WholesalePurchase, Product
from decimal import Decimal
from django.utils import timezone


class WholesalePurchaseSerializer(serializers.ModelSerializer):
    product_name = serializers.SerializerMethodField()
    unit_cost = serializers.SerializerMethodField()
    
    # Fields to match frontend expectations
    supplier = serializers.CharField(required=False, allow_blank=True, default='')
    purchase_date = serializers.DateTimeField(source='purchased_at', required=False, default=timezone.now)
    cost_per_unit = serializers.DecimalField(write_only=True, max_digits=10, decimal_places=2, required=False)
    notes = serializers.CharField(required=False, allow_blank=True, default='')
    
    class Meta:
        model = WholesalePurchase
        fields = ['id', 'product', 'product_name', 'quantity', 'total_cost', 
                 'unit_cost', 'purchased_at', 'created_at', 'updated_at',
                 'supplier', 'purchase_date', 'cost_per_unit', 'notes']
        read_only_fields = ['created_at', 'updated_at', 'product_name', 'unit_cost']
    
    def get_product_name(self, obj):
        return obj.product.name
    
    def get_unit_cost(self, obj):
        return obj.unit_cost
        
    def to_representation(self, instance):
        representation = super().to_representation(instance)
        # Map backend field names to frontend expectations
        representation['cost_per_unit'] = representation['unit_cost']
        representation['purchase_date'] = representation['purchased_at']
        # Add supplier and notes if they don't exist
        if 'supplier' not in representation:
            representation['supplier'] = ''
        if 'notes' not in representation:
            representation['notes'] = ''
        return representation
        
    def create(self, validated_data):
        # Handle cost_per_unit calculation
        cost_per_unit = validated_data.pop('cost_per_unit', None)
        
        # Calculate total_cost if cost_per_unit was provided
        if cost_per_unit is not None:
            quantity = validated_data.get('quantity', 1)
            validated_data['total_cost'] = Decimal(str(cost_per_unit)) * Decimal(quantity)
            
        return super().create(validated_data)
        
    def update(self, instance, validated_data):
        # Handle cost_per_unit calculation
        cost_per_unit = validated_data.pop('cost_per_unit', None)
        
        # Calculate total_cost if cost_per_unit was provided
        if cost_per_unit is not None:
            quantity = validated_data.get('quantity', instance.quantity)
            validated_data['total_cost'] = Decimal(str(cost_per_unit)) * Decimal(quantity)
            
        return super().update(instance, validated_data) 