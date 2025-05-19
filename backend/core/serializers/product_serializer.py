from rest_framework import serializers
from core.models import Product, WholesalePurchase, ProductCost
from decimal import Decimal
from django.utils import timezone


class ProductSerializer(serializers.ModelSerializer):
    average_cost = serializers.SerializerMethodField()
    latest_cost = serializers.SerializerMethodField()
    cost_price = serializers.DecimalField(write_only=True, required=False, default=0, max_digits=10, decimal_places=2)
    
    class Meta:
        model = Product
        fields = [
            'id', 'name', 'product_type', 'unit_type', 'image_url', 
            'inventory_quantity', 'average_cost', 'latest_cost', 
            'cost_price', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at', 'average_cost', 'latest_cost']
        extra_kwargs = {
            'unit_type': {'required': False, 'default': 'unit'},
            'product_type': {'required': False, 'default': 'Soda'},
            'image_url': {'required': False}
        }
    
    def get_average_cost(self, obj):
        return obj.average_cost
    
    def get_latest_cost(self, obj):
        return obj.latest_unit_cost
    
    def to_representation(self, instance):
        representation = super().to_representation(instance)
        # Add cost_price to representation using latest cost if available, otherwise use average cost
        representation['cost_price'] = instance.latest_unit_cost or instance.average_cost
        return representation
        
    def create(self, validated_data):
        # Extract cost_price and initial quantity from validated data
        cost_price = validated_data.pop('cost_price', 0)
        initial_quantity = validated_data.get('inventory_quantity', 0)
        
        # Create the product
        product = Product.objects.create(**validated_data)
        
        # If cost_price was provided and is non-zero, create an initial wholesale purchase
        if cost_price and float(cost_price) > 0 and initial_quantity > 0:
            # Create wholesale purchase
            purchase = WholesalePurchase.objects.create(
                product=product,
                quantity=initial_quantity,
                total_cost=Decimal(str(cost_price)) * initial_quantity,
                purchased_at=timezone.now(),
                supplier='Initial',
                notes='Initial inventory setup',
                # Disable automatic inventory update since we're setting it directly
                inventory_updated=True
            )
            
            # Create cost history record
            ProductCost.objects.create(
                product=product,
                purchase=purchase,
                date=purchase.purchased_at,
                quantity=initial_quantity,
                unit_cost=Decimal(str(cost_price)),
                total_cost=Decimal(str(cost_price)) * initial_quantity
            )
        
        return product
        
    def update(self, instance, validated_data):
        # Extract cost_price from validated data
        cost_price = validated_data.pop('cost_price', None)
        
        # Track if inventory changed
        old_inventory = instance.inventory_quantity
        new_inventory = validated_data.get('inventory_quantity', old_inventory)
        inventory_change = new_inventory - old_inventory
        
        # Update the product without cost_price
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        
        # If inventory was manually adjusted, record it
        if inventory_change != 0:
            # Create wholesale purchase as an adjustment
            purchase = WholesalePurchase.objects.create(
                product=instance,
                quantity=inventory_change,
                total_cost=Decimal('0.00') if cost_price is None else Decimal(str(cost_price)) * abs(inventory_change),
                purchased_at=timezone.now(),
                supplier='Manual Adjustment',
                notes=f'Manual inventory adjustment: {inventory_change}',
                # Disable automatic inventory update since we already updated it
                inventory_updated=True
            )
            
            # If cost_price was provided, create cost history record
            if cost_price is not None and float(cost_price) > 0:
                ProductCost.objects.create(
                    product=instance,
                    purchase=purchase,
                    date=purchase.purchased_at,
                    quantity=abs(inventory_change),
                    unit_cost=Decimal(str(cost_price)),
                    total_cost=Decimal(str(cost_price)) * abs(inventory_change)
                )
                
        return instance 