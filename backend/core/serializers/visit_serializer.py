from rest_framework import serializers
from core.models import Visit
from django.contrib.auth.models import User


class VisitSerializer(serializers.ModelSerializer):
    location_name = serializers.SerializerMethodField()
    user_name = serializers.SerializerMethodField()
    
    class Meta:
        model = Visit
        fields = ['id', 'location', 'location_name', 'user', 'user_name', 
                 'visit_date', 'notes', 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at', 'location_name', 'user_name']
    
    def get_location_name(self, obj):
        return obj.location.name
    
    def get_user_name(self, obj):
        return f"{obj.user.first_name} {obj.user.last_name}" if obj.user.first_name else obj.user.username
        
    def create(self, validated_data):
        # If user is not provided, use the current authenticated user
        request = self.context.get('request')
        if 'user' not in validated_data and request and request.user.is_authenticated:
            validated_data['user'] = request.user
        return super().create(validated_data) 