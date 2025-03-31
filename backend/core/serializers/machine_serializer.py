from rest_framework import serializers
from core.models import Machine, Location


class MachineSerializer(serializers.ModelSerializer):
    location_name = serializers.SerializerMethodField()
    
    class Meta:
        model = Machine
        fields = ['id', 'name', 'location', 'location_name', 'machine_type', 'model', 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at', 'location_name']
    
    def get_location_name(self, obj):
        return obj.location.name 