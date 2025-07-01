from rest_framework import serializers
from core.models import Machine, Location


class MachineSerializer(serializers.ModelSerializer):
    location_name = serializers.SerializerMethodField()
    route = serializers.SerializerMethodField()
    route_name = serializers.SerializerMethodField()
    product_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Machine
        fields = ['id', 'name', 'location', 'location_name', 'route', 'route_name', 'machine_type', 'model', 'product_count', 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at', 'location_name', 'route', 'route_name', 'product_count']
    
    def get_location_name(self, obj):
        return obj.location.name
    
    def get_route(self, obj):
        return obj.location.route
    
    def get_route_name(self, obj):
        return obj.location.route or 'No Route Assigned'
        
    def get_product_count(self, obj):
        return obj.item_prices.count() 