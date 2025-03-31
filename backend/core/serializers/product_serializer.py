from rest_framework import serializers
from core.models import Product, WholesalePurchase
from decimal import Decimal
from django.utils import timezone


class ProductSerializer(serializers.ModelSerializer):
    average_cost = serializers.SerializerMethodField()
    image_url = serializers.SerializerMethodField()
    cost_price = serializers.DecimalField(write_only=True, required=False, default=0, max_digits=10, decimal_places=2)
    
    class Meta:
        model = Product
        fields = ['id', 'name', 'product_type', 'unit_type', 'image_url', 'average_cost', 'cost_price', 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at', 'average_cost']
        extra_kwargs = {
            'unit_type': {'required': False, 'default': 'unit'},
            'product_type': {'required': False, 'default': 'Soda'}
        }
    
    def get_average_cost(self, obj):
        return obj.average_cost
    
    def get_image_url(self, obj):
        # Return the image_url directly since it's a field on the model now
        return obj.image_url
        
    def to_representation(self, instance):
        representation = super().to_representation(instance)
        # Add cost_price to representation using average_cost
        representation['cost_price'] = instance.average_cost
        return representation
        
    def create(self, validated_data):
        # Extract cost_price from validated data, default to 0 if not provided
        cost_price = validated_data.pop('cost_price', 0)
        
        # Create the product without cost_price (as it's not a model field)
        product = Product.objects.create(**validated_data)
        
        # If cost_price was provided and is non-zero, create an initial wholesale purchase
        if cost_price and float(cost_price) > 0:
            WholesalePurchase.objects.create(
                product=product,
                quantity=1,  # Initial reference quantity
                total_cost=Decimal(str(cost_price)),  # Convert to Decimal safely
                purchased_at=timezone.now()  # Use current time as purchase date
            )
        
        return product
        
    def update(self, instance, validated_data):
        # Extract cost_price from validated data
        cost_price = validated_data.pop('cost_price', None)
        
        # Update the product without cost_price
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        
        # If cost_price was provided and is non-zero, create a new wholesale purchase
        if cost_price is not None and float(cost_price) > 0:
            # Check if there are no existing wholesale purchases
            if not instance.wholesale_purchases.exists():
                WholesalePurchase.objects.create(
                    product=instance,
                    quantity=1,  # Initial reference quantity
                    total_cost=Decimal(str(cost_price)),  # Convert to Decimal safely
                    purchased_at=timezone.now()  # Use current time as purchase date
                )
                
        return instance 