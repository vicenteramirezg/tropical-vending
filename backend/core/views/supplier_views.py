from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Q
from core.models import Supplier
from core.serializers import SupplierSerializer, SupplierListSerializer


class SupplierViewSet(viewsets.ModelViewSet):
    queryset = Supplier.objects.all().order_by('name')
    serializer_class = SupplierSerializer
    search_fields = ['name', 'contact_person', 'email']
    filterset_fields = ['is_active']
    
    def get_serializer_class(self):
        """Use different serializers for different actions"""
        if self.action == 'list':
            return SupplierListSerializer
        return SupplierSerializer
    
    def get_queryset(self):
        """Filter queryset based on query parameters"""
        queryset = Supplier.objects.all()
        
        # Filter by active status
        is_active = self.request.query_params.get('is_active', None)
        if is_active is not None:
            if is_active.lower() in ['true', '1']:
                queryset = queryset.filter(is_active=True)
            elif is_active.lower() in ['false', '0']:
                queryset = queryset.filter(is_active=False)
        
        # Search functionality
        search = self.request.query_params.get('search', None)
        if search:
            queryset = queryset.filter(
                Q(name__icontains=search) |
                Q(contact_person__icontains=search) |
                Q(email__icontains=search)
            )
        
        return queryset.order_by('name')
    
    def destroy(self, request, *args, **kwargs):
        """Override destroy to handle suppliers with purchases"""
        supplier = self.get_object()
        
        # Check if supplier has any purchases
        if supplier.purchase_count > 0:
            return Response(
                {
                    "error": "Cannot delete supplier with existing purchases. "
                             "Consider deactivating the supplier instead."
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        
        return super().destroy(request, *args, **kwargs)
    
    @action(detail=True, methods=['post'])
    def toggle_active(self, request, pk=None):
        """Toggle the active status of a supplier"""
        supplier = self.get_object()
        supplier.is_active = not supplier.is_active
        supplier.save()
        
        serializer = self.get_serializer(supplier)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def active(self, request):
        """Get only active suppliers"""
        suppliers = self.get_queryset().filter(is_active=True)
        serializer = SupplierListSerializer(suppliers, many=True)
        return Response(serializer.data) 