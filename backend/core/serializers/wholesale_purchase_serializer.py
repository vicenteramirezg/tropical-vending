from rest_framework import serializers
from core.models import WholesalePurchase, Product, ProductCost, Supplier
from decimal import Decimal
from django.utils import timezone
from django.db import transaction


class WholesalePurchaseSerializer(serializers.ModelSerializer):
    product_name = serializers.SerializerMethodField()
    supplier_name = serializers.SerializerMethodField()
    unit_cost = serializers.SerializerMethodField()
    current_inventory = serializers.SerializerMethodField(read_only=True)
    
    # Fields to match frontend expectations
    purchase_date = serializers.DateTimeField(source='purchased_at', required=False, default=timezone.now)
    cost_per_unit = serializers.DecimalField(write_only=True, max_digits=10, decimal_places=2, required=False)
    notes = serializers.CharField(required=False, allow_blank=True, default='')
    
    class Meta:
        model = WholesalePurchase
        fields = ['id', 'product', 'product_name', 'supplier', 'supplier_name', 'quantity', 'total_cost', 
                 'unit_cost', 'purchased_at', 'created_at', 'updated_at',
                 'purchase_date', 'cost_per_unit', 'notes',
                 'current_inventory', 'inventory_updated']
        read_only_fields = ['created_at', 'updated_at', 'product_name', 'supplier_name',
                           'unit_cost', 'current_inventory', 'inventory_updated']
    
    def get_product_name(self, obj):
        return obj.product.name
    
    def get_supplier_name(self, obj):
        return obj.supplier.name if obj.supplier else ''
    
    def get_unit_cost(self, obj):
        return obj.unit_cost
    
    def get_current_inventory(self, obj):
        return obj.product.inventory_quantity
        
    def to_representation(self, instance):
        representation = super().to_representation(instance)
        # Map backend field names to frontend expectations
        representation['cost_per_unit'] = representation['unit_cost']
        representation['purchase_date'] = representation['purchased_at']
        # Ensure supplier field shows the ID for frontend compatibility
        if instance.supplier:
            representation['supplier'] = instance.supplier.id
        else:
            representation['supplier'] = None
        return representation
        
    def validate_supplier(self, value):
        """Validate that the supplier exists and is active"""
        # Handle empty string or None
        if value is None or value == '' or value == 'null':
            return None
            
        # Convert string ID to integer if needed
        if isinstance(value, str):
            try:
                value = int(value)
            except (ValueError, TypeError):
                raise serializers.ValidationError("Supplier ID must be a valid integer.")
        
        # Validate supplier exists and is active
        try:
            supplier = Supplier.objects.get(id=value, is_active=True)
            return value  # Return the ID, not the supplier instance
        except Supplier.DoesNotExist:
            raise serializers.ValidationError("Invalid supplier or supplier is not active.")
        
    @transaction.atomic
    def create(self, validated_data):
        # Handle cost_per_unit calculation
        cost_per_unit = validated_data.pop('cost_per_unit', None)
        
        # Calculate total_cost if cost_per_unit was provided
        if cost_per_unit is not None:
            quantity = validated_data.get('quantity', 1)
            validated_data['total_cost'] = Decimal(str(cost_per_unit)) * Decimal(quantity)
        
        # Create the wholesale purchase
        purchase = super().create(validated_data)
        
        # Update inventory and create cost history record
        # This is handled by the post_save signal in the model
        
        return purchase
        
    @transaction.atomic
    def update(self, instance, validated_data):
        # Track original values for inventory adjustment
        original_quantity = instance.quantity
        
        # Handle cost_per_unit calculation
        cost_per_unit = validated_data.pop('cost_per_unit', None)
        
        # Calculate total_cost if cost_per_unit was provided
        if cost_per_unit is not None:
            quantity = validated_data.get('quantity', instance.quantity)
            validated_data['total_cost'] = Decimal(str(cost_per_unit)) * Decimal(quantity)
        
        # Check if inventory has already been updated
        inventory_already_updated = instance.inventory_updated
        
        # If inventory was updated but quantity is changing, we need to adjust
        new_quantity = validated_data.get('quantity', original_quantity)
        quantity_change = new_quantity - original_quantity
        
        # Update the wholesale purchase
        purchase = super().update(instance, validated_data)
        
        # If inventory was already updated and quantity changed, adjust inventory
        if inventory_already_updated and quantity_change != 0:
            # Update product inventory
            purchase.product.update_inventory(quantity_change)
            
            # If cost changed, update or create a new cost record
            new_unit_cost = purchase.unit_cost
            
            # Update existing cost record or create new one
            cost_record = ProductCost.objects.filter(purchase=purchase).first()
            if cost_record:
                cost_record.quantity = new_quantity
                cost_record.unit_cost = new_unit_cost
                cost_record.total_cost = purchase.total_cost
                cost_record.save()
            else:
                ProductCost.objects.create(
                    product=purchase.product,
                    purchase=purchase,
                    date=purchase.purchased_at,
                    quantity=new_quantity,
                    unit_cost=new_unit_cost,
                    total_cost=purchase.total_cost
                )
        
        return purchase 