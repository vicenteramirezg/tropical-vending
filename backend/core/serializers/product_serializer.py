from rest_framework import serializers
from core.models import Product


class ProductSerializer(serializers.ModelSerializer):
    average_cost = serializers.SerializerMethodField()
    image_url = serializers.SerializerMethodField()
    
    class Meta:
        model = Product
        fields = ['id', 'name', 'sku', 'unit_type', 'image', 'image_url', 'average_cost', 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at', 'average_cost', 'image_url']
    
    def get_average_cost(self, obj):
        return obj.average_cost
    
    def get_image_url(self, obj):
        if obj.image:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.image.url)
        return None 