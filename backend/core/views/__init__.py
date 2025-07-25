from .location_views import LocationViewSet
from .machine_views import MachineViewSet
from .product_views import ProductViewSet
from .machine_item_price_views import MachineItemPriceViewSet
from .supplier_views import SupplierViewSet
from .wholesale_purchase_views import WholesalePurchaseViewSet
from .visit_views import VisitViewSet
from .visit_machine_restock_views import VisitMachineRestockViewSet
from .restock_entry_views import RestockEntryViewSet
from .user_views import RegisterView, UserProfileView
from .product_cost_views import ProductCostViewSet
from .analytics_views import (
    StockLevelView, 
    DemandAnalysisView, 
    RevenueProfitView, 
    DashboardView,
    CurrentStockReportView,
    RestockSummaryView,
    StockCoverageEstimateView
) 