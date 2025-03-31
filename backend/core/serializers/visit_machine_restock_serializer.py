from rest_framework import serializers
from core.models import VisitMachineRestock


class VisitMachineRestockSerializer(serializers.ModelSerializer):
    machine_info = serializers.SerializerMethodField()
    visit_info = serializers.SerializerMethodField()
    
    class Meta:
        model = VisitMachineRestock
        fields = ['id', 'visit', 'visit_info', 'machine', 'machine_info', 
                 'notes', 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at', 'machine_info', 'visit_info']
    
    def get_machine_info(self, obj):
        return f"{obj.machine.machine_type} {obj.machine.model} at {obj.machine.location.name}"
    
    def get_visit_info(self, obj):
        return f"Visit to {obj.visit.location.name} on {obj.visit.visit_date.strftime('%Y-%m-%d %H:%M')}" 