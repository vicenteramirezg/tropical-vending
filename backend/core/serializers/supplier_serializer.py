from rest_framework import serializers
from core.models import Supplier


class SupplierSerializer(serializers.ModelSerializer):
    purchase_count = serializers.SerializerMethodField()
    total_spent = serializers.SerializerMethodField()
    
    class Meta:
        model = Supplier
        fields = [
            'id', 'name', 'contact_person', 'phone', 'email', 'address', 
            'notes', 'is_active', 'purchase_count', 'total_spent',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at', 'purchase_count', 'total_spent']
        extra_kwargs = {
            'contact_person': {'required': False},
            'phone': {'required': False},
            'email': {'required': False},
            'address': {'required': False},
            'notes': {'required': False},
            'is_active': {'required': False, 'default': True}
        }
    
    def get_purchase_count(self, obj):
        return obj.purchase_count
    
    def get_total_spent(self, obj):
        return obj.total_spent
    
    def validate_name(self, value):
        """Ensure supplier name is unique (case-insensitive)"""
        if not value or not value.strip():
            raise serializers.ValidationError("Supplier name cannot be empty.")
        
        # Check for uniqueness (case-insensitive), excluding current instance if updating
        queryset = Supplier.objects.filter(name__iexact=value.strip())
        if self.instance:
            queryset = queryset.exclude(pk=self.instance.pk)
        
        if queryset.exists():
            raise serializers.ValidationError("A supplier with this name already exists.")
        
        return value.strip()


class SupplierListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for listing suppliers"""
    purchase_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Supplier
        fields = ['id', 'name', 'is_active', 'purchase_count', 'created_at']
        read_only_fields = ['created_at', 'purchase_count']
    
    def get_purchase_count(self, obj):
        return obj.purchase_count 