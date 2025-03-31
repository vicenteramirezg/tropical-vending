from rest_framework import viewsets, filters
from core.models import VisitMachineRestock
from core.serializers import VisitMachineRestockSerializer


class VisitMachineRestockViewSet(viewsets.ModelViewSet):
    queryset = VisitMachineRestock.objects.all().order_by('-visit__visit_date')
    serializer_class = VisitMachineRestockSerializer
    filterset_fields = ['visit', 'machine'] 