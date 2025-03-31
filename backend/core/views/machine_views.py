from rest_framework import viewsets, filters
from core.models import Machine
from core.serializers import MachineSerializer


class MachineViewSet(viewsets.ModelViewSet):
    queryset = Machine.objects.all().order_by('location__name', 'machine_type', 'model')
    serializer_class = MachineSerializer
    filterset_fields = ['location']
    search_fields = ['machine_type', 'model', 'location__name'] 