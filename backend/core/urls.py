from django.urls import path, include
from rest_framework.routers import DefaultRouter
from core.views import (
    LocationViewSet, MachineViewSet, ProductViewSet, 
    MachineItemPriceViewSet, SupplierViewSet, WholesalePurchaseViewSet,
    VisitViewSet, VisitMachineRestockViewSet, RestockEntryViewSet,
    RegisterView, UserProfileView, ProductCostViewSet,
    StockLevelView, DemandAnalysisView, RevenueProfitView, DashboardView,
    CurrentStockReportView, RestockSummaryView, StockCoverageEstimateView,
    BulkVisitSaveView
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
    # User authentication endpoints
    path('register/', RegisterView.as_view(), name='register'),
    path('profile/', UserProfileView.as_view(), name='profile'),
    
    # Bulk operations for performance optimization (MUST be before router URLs)
    path('visits/bulk-save/', BulkVisitSaveView.as_view(), name='bulk-visit-save'),
    path('visits/<int:visit_id>/bulk-update/', BulkVisitSaveView.as_view(), name='bulk-visit-update'),
    
    # Analytics endpoints
    path('analytics/stock-levels/', StockLevelView.as_view(), name='stock-levels'),
    path('analytics/demand/', DemandAnalysisView.as_view(), name='demand-analysis'),
    path('analytics/revenue-profit/', RevenueProfitView.as_view(), name='revenue-profit'),
    path('dashboard/', DashboardView.as_view(), name='dashboard'),
    
    # Inventory reporting endpoints
    path('inventory/current-stock/', CurrentStockReportView.as_view(), name='current-stock-report'),
    path('inventory/restock-summary/', RestockSummaryView.as_view(), name='restock-summary'),
    path('inventory/stock-coverage/', StockCoverageEstimateView.as_view(), name='stock-coverage-estimate'),
    
    # Include router URLs (MUST be last to avoid conflicts)
    path('', include(router.urls)),
] 