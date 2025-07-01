from rest_framework import serializers
from core.models import Location


class LocationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Location
        fields = ['id', 'name', 'address', 'route', 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at'] 