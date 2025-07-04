from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Avg, Max, Count
from core.models import DemandTracking, Machine, Product
from core.serializers import DemandTrackingSerializer, DemandSummarySerializer


class DemandTrackingViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for viewing demand tracking records.
    Provides read-only access to demand data.
    """
    queryset = DemandTracking.objects.all().order_by('-current_visit__visit_date')
    serializer_class = DemandTrackingSerializer
    filterset_fields = ['machine', 'product', 'current_visit', 'previous_visit']
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Filter by machine if specified
        machine_id = self.request.query_params.get('machine_id')
        if machine_id:
            queryset = queryset.filter(machine_id=machine_id)
        
        # Filter by product if specified
        product_id = self.request.query_params.get('product_id')
        if product_id:
            queryset = queryset.filter(product_id=product_id)
        
        # Filter by date range if specified
        start_date = self.request.query_params.get('start_date')
        end_date = self.request.query_params.get('end_date')
        if start_date:
            queryset = queryset.filter(current_visit__visit_date__gte=start_date)
        if end_date:
            queryset = queryset.filter(current_visit__visit_date__lte=end_date)
        
        return queryset
    
    @action(detail=False, methods=['get'])
    def summary(self, request):
        """
        Get demand summary data grouped by machine and product.
        """
        # Get query parameters
        machine_id = request.query_params.get('machine_id')
        product_id = request.query_params.get('product_id')
        days = int(request.query_params.get('days', 30))
        
        # Build base queryset
        queryset = DemandTracking.objects.all()
        
        if machine_id:
            queryset = queryset.filter(machine_id=machine_id)
        if product_id:
            queryset = queryset.filter(product_id=product_id)
        
        # Get demand summary data
        summary_data = queryset.values(
            'machine_id', 'machine__name', 'machine__machine_type', 
            'machine__location__name', 'product_id', 'product__name'
        ).annotate(
            average_daily_demand=Avg('daily_demand'),
            total_records=Count('id'),
            last_calculated=Max('current_visit__visit_date')
        ).order_by('-last_calculated')
        
        # Format the data
        formatted_data = []
        for item in summary_data:
            formatted_data.append({
                'machine_id': item['machine_id'],
                'machine_name': f"{item['machine__name']} - {item['machine__machine_type']} at {item['machine__location__name']}",
                'product_id': item['product_id'],
                'product_name': item['product__name'],
                'average_daily_demand': item['average_daily_demand'] or 0,
                'total_records': item['total_records'],
                'last_calculated': item['last_calculated']
            })
        
        serializer = DemandSummarySerializer(formatted_data, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def by_machine(self, request):
        """
        Get demand data grouped by machine.
        """
        machine_id = request.query_params.get('machine_id')
        if not machine_id:
            return Response(
                {'error': 'machine_id parameter is required'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            machine = Machine.objects.get(id=machine_id)
        except Machine.DoesNotExist:
            return Response(
                {'error': 'Machine not found'}, 
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Get demand records for this machine
        demand_records = DemandTracking.objects.filter(machine=machine).order_by('-current_visit__visit_date')
        
        # Group by product
        product_demands = {}
        for record in demand_records:
            product_id = record.product_id
            if product_id not in product_demands:
                product_demands[product_id] = {
                    'product_id': product_id,
                    'product_name': record.product.name,
                    'records': [],
                    'average_demand': 0,
                    'total_records': 0
                }
            
            product_demands[product_id]['records'].append({
                'visit_date': record.current_visit.visit_date,
                'daily_demand': record.daily_demand,
                'total_consumption': record.total_consumption,
                'days_between_visits': record.days_between_visits
            })
            product_demands[product_id]['total_records'] += 1
        
        # Calculate averages
        for product_id, data in product_demands.items():
            total_demand = sum(float(record['daily_demand']) for record in data['records'])
            data['average_demand'] = total_demand / len(data['records']) if data['records'] else 0
        
        return Response({
            'machine_id': machine.id,
            'machine_name': f"{machine.name} - {machine.machine_type} at {machine.location.name}",
            'product_demands': list(product_demands.values())
        })
    
    @action(detail=False, methods=['get'])
    def by_product(self, request):
        """
        Get demand data grouped by product across all machines.
        """
        product_id = request.query_params.get('product_id')
        if not product_id:
            return Response(
                {'error': 'product_id parameter is required'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            product = Product.objects.get(id=product_id)
        except Product.DoesNotExist:
            return Response(
                {'error': 'Product not found'}, 
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Get demand records for this product
        demand_records = DemandTracking.objects.filter(product=product).order_by('-current_visit__visit_date')
        
        # Group by machine
        machine_demands = {}
        for record in demand_records:
            machine_id = record.machine_id
            if machine_id not in machine_demands:
                machine_demands[machine_id] = {
                    'machine_id': machine_id,
                    'machine_name': f"{record.machine.name} - {record.machine.machine_type} at {record.machine.location.name}",
                    'records': [],
                    'average_demand': 0,
                    'total_records': 0
                }
            
            machine_demands[machine_id]['records'].append({
                'visit_date': record.current_visit.visit_date,
                'daily_demand': record.daily_demand,
                'total_consumption': record.total_consumption,
                'days_between_visits': record.days_between_visits
            })
            machine_demands[machine_id]['total_records'] += 1
        
        # Calculate averages
        for machine_id, data in machine_demands.items():
            total_demand = sum(float(record['daily_demand']) for record in data['records'])
            data['average_demand'] = total_demand / len(data['records']) if data['records'] else 0
        
        return Response({
            'product_id': product.id,
            'product_name': product.name,
            'machine_demands': list(machine_demands.values())
        })