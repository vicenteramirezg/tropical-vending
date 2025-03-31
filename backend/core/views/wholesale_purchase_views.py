from rest_framework import viewsets, filters
from core.models import WholesalePurchase
from core.serializers import WholesalePurchaseSerializer


class WholesalePurchaseViewSet(viewsets.ModelViewSet):
    queryset = WholesalePurchase.objects.all().order_by('-purchased_at')
    serializer_class = WholesalePurchaseSerializer
    filterset_fields = ['product'] 