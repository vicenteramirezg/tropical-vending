from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Q
from core.models import Location
from core.serializers import LocationSerializer


class LocationViewSet(viewsets.ModelViewSet):
    queryset = Location.objects.all().order_by('name')
    serializer_class = LocationSerializer
    
    def get_queryset(self):
        queryset = Location.objects.all().order_by('name')
        route = self.request.query_params.get('route', None)
        
        if route is not None:
            if route == 'unassigned':
                queryset = queryset.filter(Q(route__isnull=True) | Q(route=''))
            else:
                queryset = queryset.filter(route=route)
        
        return queryset
    
    @action(detail=False, methods=['get'])
    def routes(self, request):
        """Get list of available routes"""
        routes = Location.objects.exclude(
            Q(route__isnull=True) | Q(route='')
        ).values_list('route', flat=True).distinct().order_by('route')
        
        return Response({
            'routes': list(routes)
        }) 