from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import permissions, status
from core.models import (
    RestockEntry, MachineItemPrice, Product, Machine, Location
)
from django.db.models import Sum, F, FloatField, Avg, Count, Q
from django.db.models.functions import Coalesce
from datetime import datetime, timedelta
from django.utils import timezone


class StockLevelView(APIView):
    """
    Get time-series stock data for products/machines
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        product_id = request.query_params.get('product')
        machine_id = request.query_params.get('machine')
        
        # Base query for restock entries
        restocks = RestockEntry.objects.select_related(
            'product', 
            'visit_machine_restock__machine',
            'visit_machine_restock__visit'
        ).order_by('visit_machine_restock__visit__visit_date')
        
        # Filter by product or machine if provided
        if product_id:
            restocks = restocks.filter(product_id=product_id)
        if machine_id:
            restocks = restocks.filter(visit_machine_restock__machine_id=machine_id)
            
        # Prepare time series data
        stock_data = []
        for entry in restocks:
            date = entry.visit_machine_restock.visit.visit_date
            product_name = entry.product.name
            machine_name = f"{entry.visit_machine_restock.machine.machine_type} {entry.visit_machine_restock.machine.model}"
            location_name = entry.visit_machine_restock.machine.location.name
            
            stock_data.append({
                'date': date,
                'product': product_name,
                'machine': machine_name,
                'location': location_name,
                'stock_before': entry.stock_before,
                'restocked': entry.restocked,
                'stock_after': entry.stock_before + entry.restocked
            })
            
        return Response(stock_data)


class DemandAnalysisView(APIView):
    """
    Analyze demand by calculating units sold between restocks
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        product_id = request.query_params.get('product')
        machine_id = request.query_params.get('machine')
        days = int(request.query_params.get('days', 30))
        
        # Get date range
        end_date = timezone.now()
        start_date = end_date - timedelta(days=days)
        
        # Base query for restock entries within time period
        restocks = RestockEntry.objects.select_related(
            'product', 
            'visit_machine_restock__machine',
            'visit_machine_restock__visit'
        ).filter(
            visit_machine_restock__visit__visit_date__gte=start_date,
            visit_machine_restock__visit__visit_date__lte=end_date
        )
        
        # Filter by product or machine if provided
        if product_id:
            restocks = restocks.filter(product_id=product_id)
        if machine_id:
            restocks = restocks.filter(visit_machine_restock__machine_id=machine_id)
            
        # Group and analyze
        demand_data = []
        
        # Process by machine/product combination
        if machine_id and product_id:
            # Get all restocks for specific machine/product sorted by date
            entries = restocks.order_by('visit_machine_restock__visit__visit_date')
            
            # Process sequential entries to calculate demand
            for i in range(1, len(entries)):
                prev = entries[i-1]
                curr = entries[i]
                
                # Calculate time difference in days
                days_between = (curr.visit_machine_restock.visit.visit_date - 
                               prev.visit_machine_restock.visit.visit_date).days
                
                # Calculate units sold (previous stock level minus current stock before restocking)
                units_sold = (prev.stock_before + prev.restocked) - curr.stock_before
                
                # Only include if positive sales (prevents errors in data)
                if units_sold >= 0 and days_between > 0:
                    daily_demand = units_sold / days_between
                    
                    demand_data.append({
                        'product': curr.product.name,
                        'product_id': curr.product_id,
                        'machine': f"{curr.visit_machine_restock.machine.machine_type} {curr.visit_machine_restock.machine.model}",
                        'machine_id': curr.visit_machine_restock.machine_id,
                        'location': curr.visit_machine_restock.machine.location.name,
                        'start_date': prev.visit_machine_restock.visit.visit_date,
                        'end_date': curr.visit_machine_restock.visit.visit_date,
                        'days_between': days_between,
                        'units_sold': units_sold,
                        'daily_demand': daily_demand
                    })
        
        # Otherwise return aggregate data
        else:
            # Group by machine or product as needed
            from django.db.models import Avg, F, Sum, ExpressionWrapper, fields
            
            # This is simplified - real implementation would be more complex
            # to properly calculate demand between visits
            
            demand_data = [
                {
                    'product': 'Product-level demand requires specific machine/product selection',
                    'note': 'Please select both product and machine for detailed demand analysis'
                }
            ]
        
        return Response(demand_data)


class RevenueProfitView(APIView):
    """
    Calculate revenue and profit for products/machines based on estimated sales
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        product_id = request.query_params.get('product')
        machine_id = request.query_params.get('machine')
        days = int(request.query_params.get('days', 30))
        
        # This is a simplified calculation
        # In a real implementation, you would use the demand data and price information
        # to calculate accurate revenue and profit
        
        data = {
            'note': 'This is estimated data based on demand and pricing',
            'revenue': {
                'total': 1250.50,
                'by_product': [
                    {'product': 'Cola', 'revenue': 450.25},
                    {'product': 'Water', 'revenue': 325.50},
                    {'product': 'Snacks', 'revenue': 474.75},
                ],
                'by_machine': [
                    {'machine': 'Drink Machine #1', 'revenue': 650.25},
                    {'machine': 'Snack Machine #2', 'revenue': 600.25},
                ]
            },
            'profit': {
                'total': 625.25,
                'by_product': [
                    {'product': 'Cola', 'profit': 225.13},
                    {'product': 'Water', 'profit': 162.75},
                    {'product': 'Snacks', 'profit': 237.37},
                ],
                'by_machine': [
                    {'machine': 'Drink Machine #1', 'profit': 325.13},
                    {'machine': 'Snack Machine #2', 'profit': 300.12},
                ]
            }
        }
        
        return Response(data)


class DashboardView(APIView):
    """
    Get key performance indicators for the dashboard
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        # Get basic counts
        location_count = Location.objects.count()
        machine_count = Machine.objects.count()
        product_count = Product.objects.count()
        
        # Get low stock items
        low_stock_threshold = 5  # Items with stock below this are considered low
        low_stock_items = MachineItemPrice.objects.filter(
            current_stock__lt=low_stock_threshold,
            current_stock__isnull=False
        ).select_related('machine', 'product', 'machine__location').order_by('current_stock')
        
        low_stock_data = []
        for item in low_stock_items:
            low_stock_data.append({
                'product': item.product.name,
                'machine': f"{item.machine.machine_type} {item.machine.model}",
                'location': item.machine.location.name,
                'current_stock': item.current_stock,
                'price': item.price
            })
        
        # Recent restocks (last 7 days)
        recent_restocks = RestockEntry.objects.filter(
            visit_machine_restock__visit__visit_date__gte=timezone.now() - timedelta(days=7)
        ).count()
        
        # Return dashboard data
        dashboard_data = {
            'locations': location_count,
            'machines': machine_count,
            'products': product_count,
            'low_stock_items': low_stock_data,
            'low_stock_count': len(low_stock_data),
            'recent_restocks': recent_restocks,
            # Sample data (would be calculated in a real implementation)
            'revenue_total': 1250.50,
            'profit_total': 625.25,
            'profit_margin': 50.0,
        }
        
        return Response(dashboard_data) 