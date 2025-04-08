from rest_framework import viewsets, filters
from core.models import MachineItemPrice
from core.serializers import MachineItemPriceSerializer


class MachineItemPriceViewSet(viewsets.ModelViewSet):
    queryset = MachineItemPrice.objects.all().order_by('machine__location__name', 'machine__machine_type', 'slot')
    serializer_class = MachineItemPriceSerializer
    filterset_fields = ['machine', 'product', 'slot'] 