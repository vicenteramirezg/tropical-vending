from rest_framework import viewsets, filters
from django.db.models import Q
from core.models import Machine
from core.serializers import MachineSerializer


class MachineViewSet(viewsets.ModelViewSet):
    queryset = Machine.objects.all().order_by('location__name', 'machine_type', 'model')
    serializer_class = MachineSerializer
    filterset_fields = ['location', 'machine_type']
    search_fields = ['machine_type', 'model', 'location__name', 'location__route']
    
    def get_queryset(self):
        queryset = Machine.objects.all().order_by('location__name', 'machine_type', 'model')
        route = self.request.query_params.get('route', None)
        
        if route is not None:
            if route == 'unassigned':
                queryset = queryset.filter(Q(location__route__isnull=True) | Q(location__route=''))
            else:
                queryset = queryset.filter(location__route=route)
        
        return queryset 