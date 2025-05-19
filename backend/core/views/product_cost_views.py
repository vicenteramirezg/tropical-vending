from rest_framework import viewsets, permissions
from core.models import ProductCost, Product
from core.serializers import ProductCostSerializer
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Q


class ProductCostViewSet(viewsets.ModelViewSet):
    """
    API endpoint for managing product costs.
    """
    queryset = ProductCost.objects.all().order_by('-date')
    serializer_class = ProductCostSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """
        Filter costs based on query parameters.
        """
        queryset = ProductCost.objects.all().order_by('-date')
        product_id = self.request.query_params.get('product')
        
        if product_id:
            queryset = queryset.filter(product_id=product_id)
            
        return queryset
    
    @action(detail=False, methods=['get'])
    def latest_costs(self, request):
        """
        Get the latest cost for each product.
        """
        # Get all products
        products = Product.objects.all()
        
        # For each product, find the latest cost record
        result = []
        for product in products:
            latest_cost = ProductCost.objects.filter(product=product).order_by('-date').first()
            
            if latest_cost:
                result.append({
                    'product_id': product.id,
                    'product_name': product.name,
                    'date': latest_cost.date,
                    'unit_cost': latest_cost.unit_cost,
                    'inventory_quantity': product.inventory_quantity
                })
            else:
                # If no cost records, return zero cost
                result.append({
                    'product_id': product.id,
                    'product_name': product.name,
                    'date': None,
                    'unit_cost': 0,
                    'inventory_quantity': product.inventory_quantity
                })
        
        return Response(result) 