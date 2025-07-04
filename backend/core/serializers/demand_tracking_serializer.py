from rest_framework import serializers
from core.models import DemandTracking


class DemandTrackingSerializer(serializers.ModelSerializer):
    machine_name = serializers.SerializerMethodField()
    product_name = serializers.SerializerMethodField()
    previous_visit_date = serializers.SerializerMethodField()
    current_visit_date = serializers.SerializerMethodField()
    
    class Meta:
        model = DemandTracking
        fields = [
            'id', 'machine', 'machine_name', 'product', 'product_name',
            'previous_visit', 'previous_visit_date', 'previous_stock_after_restock',
            'current_visit', 'current_visit_date', 'current_stock_before_restock',
            'days_between_visits', 'total_consumption', 'daily_demand',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']
    
    def get_machine_name(self, obj):
        return f"{obj.machine.name} - {obj.machine.machine_type} at {obj.machine.location.name}"
    
    def get_product_name(self, obj):
        return obj.product.name
    
    def get_previous_visit_date(self, obj):
        return obj.previous_visit.visit_date
    
    def get_current_visit_date(self, obj):
        return obj.current_visit.visit_date


class DemandSummarySerializer(serializers.Serializer):
    """Serializer for demand summary data"""
    machine_id = serializers.IntegerField()
    machine_name = serializers.CharField()
    product_id = serializers.IntegerField()
    product_name = serializers.CharField()
    average_daily_demand = serializers.DecimalField(max_digits=10, decimal_places=2)
    total_records = serializers.IntegerField()
    last_calculated = serializers.DateTimeField()
    
    def create(self, validated_data):
        # This is a read-only serializer
        raise NotImplementedError("DemandSummarySerializer is read-only")
    
    def update(self, instance, validated_data):
        # This is a read-only serializer
        raise NotImplementedError("DemandSummarySerializer is read-only")