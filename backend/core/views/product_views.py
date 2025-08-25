from rest_framework import viewsets, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from core.models import Product, MachineItemPrice
from core.serializers import ProductSerializer
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend


class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all().order_by('name')
    serializer_class = ProductSerializer
    search_fields = ['name', 'unit_type']
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['product_type']
    
    def get_queryset(self):
        """
        Override get_queryset to handle custom filtering if needed
        """
        queryset = Product.objects.all().order_by('name')
        
        # Apply search filter
        search = self.request.query_params.get('search', None)
        if search:
            queryset = queryset.filter(name__icontains=search)
        
        # Apply product type filter
        product_type = self.request.query_params.get('product_type', None)
        if product_type:
            queryset = queryset.filter(product_type=product_type)
        
        return queryset
    
    def get_serializer_context(self):
        context = super().get_serializer_context()
        context.update({"request": self.request})
        return context
        
    @action(detail=False, methods=['get'])
    def by_machine_slot(self, request):
        """Get product by machine ID and slot number"""
        machine_id = request.query_params.get('machine')
        slot = request.query_params.get('slot')
        
        if not machine_id or not slot:
            return Response({"error": "Both machine and slot parameters are required"}, status=400)
            
        try:
            machine_item = get_object_or_404(MachineItemPrice, machine_id=machine_id, slot=slot)
            product = machine_item.product
            serializer = self.get_serializer(product)
            return Response(serializer.data)
        except Exception as e:
            return Response({"error": str(e)}, status=404)
    
    @action(detail=False, methods=['get'])
    def all(self, request):
        """Get all products without pagination for use in dropdowns and forms"""
        # Override pagination for this specific endpoint
        self.pagination_class = None
        
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data) 