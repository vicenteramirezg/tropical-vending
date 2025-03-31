from rest_framework import viewsets, filters
from core.models import Visit
from core.serializers import VisitSerializer


class VisitViewSet(viewsets.ModelViewSet):
    queryset = Visit.objects.all().order_by('-visit_date')
    serializer_class = VisitSerializer
    filterset_fields = ['location', 'user'] 