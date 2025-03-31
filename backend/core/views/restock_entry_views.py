from rest_framework import viewsets, filters
from core.models import RestockEntry
from core.serializers import RestockEntrySerializer


class RestockEntryViewSet(viewsets.ModelViewSet):
    queryset = RestockEntry.objects.all().order_by('-visit_machine_restock__visit__visit_date')
    serializer_class = RestockEntrySerializer
    filterset_fields = ['visit_machine_restock', 'product'] 