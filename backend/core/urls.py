from django.urls import path, include
from rest_framework.routers import DefaultRouter
from core.views import (
    LocationViewSet, MachineViewSet, ProductViewSet, 
    MachineItemPriceViewSet, SupplierViewSet, WholesalePurchaseViewSet,
    VisitViewSet, VisitMachineRestockViewSet, RestockEntryViewSet,
    RegisterView, UserProfileView, ProductCostViewSet,
    StockLevelView, DemandAnalysisView, RevenueProfitView, DashboardView
)

# Set up the router for ViewSets
router = DefaultRouter()
router.register(r'locations', LocationViewSet)
router.register(r'machines', MachineViewSet)
router.register(r'products', ProductViewSet)
router.register(r'machine-items', MachineItemPriceViewSet)
router.register(r'suppliers', SupplierViewSet)
router.register(r'purchases', WholesalePurchaseViewSet)
router.register(r'visits', VisitViewSet)
router.register(r'restocks', VisitMachineRestockViewSet)
router.register(r'restock-entries', RestockEntryViewSet)
router.register(r'product-costs', ProductCostViewSet)

urlpatterns = [
    # Include router URLs
    path('', include(router.urls)),
    
    # User authentication endpoints
    path('register/', RegisterView.as_view(), name='register'),
    path('profile/', UserProfileView.as_view(), name='profile'),
    
    # Analytics endpoints
    path('analytics/stock-levels/', StockLevelView.as_view(), name='stock-levels'),
    path('analytics/demand/', DemandAnalysisView.as_view(), name='demand-analysis'),
    path('analytics/revenue-profit/', RevenueProfitView.as_view(), name='revenue-profit'),
    path('dashboard/', DashboardView.as_view(), name='dashboard'),
] 