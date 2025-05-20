from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import permissions, status
from core.models import (
    RestockEntry, MachineItemPrice, Product, Machine, Location, ProductCost
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
        location_id = request.query_params.get('location')
        days = request.query_params.get('days', '30')
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')
        
        # Set the date range based on parameters
        if start_date and end_date:
            try:
                start_date = datetime.strptime(start_date, '%Y-%m-%d').replace(tzinfo=timezone.get_current_timezone())
                end_date = datetime.strptime(end_date, '%Y-%m-%d').replace(hour=23, minute=59, second=59, tzinfo=timezone.get_current_timezone())
            except ValueError:
                return Response({"error": "Invalid date format. Use YYYY-MM-DD."}, status=status.HTTP_400_BAD_REQUEST)
        else:
            end_date = timezone.now()
            days = int(days)
            start_date = end_date - timedelta(days=days)
        
        # Base query for restock entries within time period
        restocks = RestockEntry.objects.select_related(
            'product', 
            'visit_machine_restock__machine',
            'visit_machine_restock__machine__location',
            'visit_machine_restock__visit'
        ).filter(
            visit_machine_restock__visit__visit_date__gte=start_date,
            visit_machine_restock__visit__visit_date__lte=end_date
        ).order_by(
            'visit_machine_restock__machine__location',
            'visit_machine_restock__machine',
            'product',
            'visit_machine_restock__visit__visit_date'
        )
        
        # Filter by location if provided
        if location_id:
            restocks = restocks.filter(visit_machine_restock__machine__location_id=location_id)
            
        # Organize restock data by machine and product
        machine_product_restocks = {}
        
        for restock in restocks:
            machine = restock.visit_machine_restock.machine
            product = restock.product
            visit_date = restock.visit_machine_restock.visit.visit_date
            location = machine.location
            
            # Create a unique key for machine-product combination
            key = f"{machine.id}-{product.id}"
            
            if key not in machine_product_restocks:
                machine_product_restocks[key] = {
                    'machine_id': machine.id,
                    'machine_name': f"{machine.machine_type} {machine.model}",
                    'location_id': location.id,
                    'location_name': location.name,
                    'product_id': product.id,
                    'product_name': product.name,
                    'restocks': []
                }
                
            # Add restock info to the machine-product entry
            stock_after = restock.stock_before + restock.restocked
            machine_product_restocks[key]['restocks'].append({
                'date': visit_date,
                'stock_before': restock.stock_before,
                'restocked': restock.restocked,
                'stock_after': stock_after
            })
        
        # Calculate demand for each machine-product combination
        demand_data = {
            'unit_counts': [],
            'products': []
        }
        
        # Process demand calculations for each machine-product combo
        product_totals = {}  # To track totals by product for summary data
        
        for key, data in machine_product_restocks.items():
            restocks = data['restocks']
            
            # Initialize product tracking
            if data['product_id'] not in product_totals:
                product_totals[data['product_id']] = {
                    'product_id': data['product_id'],
                    'product_name': data['product_name'],
                    'units_sold': 0,
                    'revenue': 0,
                    'profit': 0,
                    'trend': 0
                }
            
            # Need at least 2 entries to calculate demand
            if len(restocks) >= 2:
                units_sold_total = 0
                days_total = 0
                daily_demand_avg = 0
                
                # Get the price of this product in this machine
                try:
                    machine_item = MachineItemPrice.objects.get(
                        machine_id=data['machine_id'],
                        product_id=data['product_id']
                    )
                    price = float(machine_item.price)
                except MachineItemPrice.DoesNotExist:
                    price = 0
                
                # For each consecutive pair of restocks
                for i in range(1, len(restocks)):
                    prev = restocks[i-1]
                    curr = restocks[i]
                    
                    # Calculate time difference in days
                    days_between = (curr['date'] - prev['date']).days
                    if days_between <= 0:
                        days_between = 1  # Minimum of 1 day
                    
                    # Calculate units sold (previous ending stock minus current starting stock)
                    units_sold = prev['stock_after'] - curr['stock_before']
                    
                    # Only include positive sales (avoids data errors)
                    if units_sold >= 0:
                        # Get the historical cost at the time of the second visit
                        historical_cost = self.get_historical_cost(data['product_id'], curr['date'])
                        
                        units_sold_total += units_sold
                        days_total += days_between
                        
                        # Record detailed demand info
                        demand_data['unit_counts'].append({
                            'machine_id': data['machine_id'],
                            'machine_name': data['machine_name'],
                            'location_id': data['location_id'],
                            'location_name': data['location_name'],
                            'product_id': data['product_id'],
                            'product_name': data['product_name'],
                            'start_date': prev['date'],
                            'end_date': curr['date'],
                            'days_between': days_between,
                            'units_sold': units_sold,
                            'daily_demand': units_sold / days_between,
                            'price': price,
                            'revenue': units_sold * price,
                            'profit_per_unit': price - historical_cost,
                            'profit': units_sold * (price - historical_cost)
                        })
                
                # Calculate overall statistics if we had valid data
                if days_total > 0:
                    daily_demand_avg = units_sold_total / days_total
                    
                    # Calculate trend (simplified)
                    trend = 0
                    if len(restocks) >= 3:
                        # Compare first half with second half
                        mid_point = len(restocks) // 2
                        first_half = sum(r['stock_after'] - restocks[i+1]['stock_before'] 
                                       for i, r in enumerate(restocks[:mid_point]) 
                                       if i+1 < mid_point and r['stock_after'] >= restocks[i+1]['stock_before'])
                        second_half = sum(r['stock_after'] - restocks[i+1]['stock_before']
                                        for i, r in enumerate(restocks[mid_point:-1])
                                        if r['stock_after'] >= restocks[i+1+mid_point]['stock_before'])
                        
                        if first_half > 0:
                            trend = ((second_half - first_half) / first_half) * 100
                    
                    # Get the historical cost for the last restock date for overall calculation
                    latest_historical_cost = self.get_historical_cost(data['product_id'], restocks[-1]['date'])
                    
                    # Update product totals
                    product_totals[data['product_id']]['units_sold'] += units_sold_total
                    product_totals[data['product_id']]['revenue'] += units_sold_total * price
                    product_totals[data['product_id']]['profit'] += units_sold_total * (price - latest_historical_cost)
                    product_totals[data['product_id']]['trend'] = trend  # Simplification
        
        # Prepare product summary data
        for product_id, data in product_totals.items():
            if data['units_sold'] > 0:
                demand_data['products'].append(data)
        
        # Sort products by units sold in descending order
        demand_data['products'].sort(key=lambda x: x['units_sold'], reverse=True)
        
        return Response(demand_data)
    
    def get_historical_cost(self, product_id, date):
        """
        Get the most recent cost of a product at a specific date
        """
        try:
            # Find the most recent cost record before or equal to the given date
            cost_record = ProductCost.objects.filter(
                product_id=product_id,
                date__lte=date
            ).order_by('-date').first()
            
            if cost_record:
                return float(cost_record.unit_cost)
            
            # Fallback to the product's average cost if no historical record exists
            product = Product.objects.get(id=product_id)
            return float(product.average_cost) if product.average_cost else 0
            
        except Exception as e:
            print(f"Error getting historical cost: {e}")
            return 0


class RevenueProfitView(APIView):
    """
    Calculate revenue and profit for products/machines based on estimated sales
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        location_id = request.query_params.get('location')
        days = request.query_params.get('days', '30')
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')
        
        # Set the date range based on parameters
        if start_date and end_date:
            try:
                start_date = datetime.strptime(start_date, '%Y-%m-%d').replace(tzinfo=timezone.get_current_timezone())
                end_date = datetime.strptime(end_date, '%Y-%m-%d').replace(hour=23, minute=59, second=59, tzinfo=timezone.get_current_timezone())
            except ValueError:
                return Response({"error": "Invalid date format. Use YYYY-MM-DD."}, status=status.HTTP_400_BAD_REQUEST)
        else:
            end_date = timezone.now()
            days = int(days)
            start_date = end_date - timedelta(days=days)
        
        # Calculate revenue based on restock entries
        restocks = RestockEntry.objects.select_related(
            'product', 
            'visit_machine_restock__machine',
            'visit_machine_restock__visit'
        ).filter(
            visit_machine_restock__visit__visit_date__gte=start_date,
            visit_machine_restock__visit__visit_date__lte=end_date
        )
        
        # Filter by location if provided
        if location_id:
            restocks = restocks.filter(visit_machine_restock__machine__location_id=location_id)
        
        # Calculate total revenue and profit
        total_revenue = 0
        total_profit = 0
        revenue_by_product = {}
        profit_by_product = {}
        revenue_by_machine = {}
        profit_by_machine = {}
        
        # Process each restock entry to calculate sales
        for entry in restocks:
            # When restocking, the units sold is the number of units restocked
            # This assumes we're restocking back to full capacity
            units_sold = max(0, entry.restocked)
            
            # Get the price for this product in this machine
            try:
                machine_item = MachineItemPrice.objects.get(
                    machine=entry.visit_machine_restock.machine,
                    product=entry.product
                )
                price = float(machine_item.price)
                
                # Get historical cost at the time of this restock
                historical_cost = self.get_historical_cost(entry.product.id, entry.visit_machine_restock.visit.visit_date)
            except MachineItemPrice.DoesNotExist:
                price = 0
                historical_cost = 0
            
            # Calculate revenue and profit for this entry
            entry_revenue = units_sold * price
            entry_profit = units_sold * (price - historical_cost)
            
            # Add to totals
            total_revenue += entry_revenue
            total_profit += entry_profit
            
            # Aggregate by product
            product_name = entry.product.name
            if product_name not in revenue_by_product:
                revenue_by_product[product_name] = 0
                profit_by_product[product_name] = 0
            revenue_by_product[product_name] += entry_revenue
            profit_by_product[product_name] += entry_profit
            
            # Aggregate by machine
            machine_name = f"{entry.visit_machine_restock.machine.machine_type} {entry.visit_machine_restock.machine.model}"
            if machine_name not in revenue_by_machine:
                revenue_by_machine[machine_name] = 0
                profit_by_machine[machine_name] = 0
            revenue_by_machine[machine_name] += entry_revenue
            profit_by_machine[machine_name] += entry_profit
        
        # Calculate profit margin
        profit_margin = 0
        if total_revenue > 0:
            profit_margin = (total_profit / total_revenue) * 100
        
        # Format the response data
        revenue_by_product_list = [{'product': p, 'revenue': r} for p, r in revenue_by_product.items()]
        profit_by_product_list = [{'product': p, 'profit': r} for p, r in profit_by_product.items()]
        revenue_by_machine_list = [{'machine': m, 'revenue': r} for m, r in revenue_by_machine.items()]
        profit_by_machine_list = [{'machine': m, 'profit': r} for m, r in profit_by_machine.items()]
        
        # Sort lists by revenue/profit
        revenue_by_product_list.sort(key=lambda x: x['revenue'], reverse=True)
        profit_by_product_list.sort(key=lambda x: x['profit'], reverse=True)
        revenue_by_machine_list.sort(key=lambda x: x['revenue'], reverse=True)
        profit_by_machine_list.sort(key=lambda x: x['profit'], reverse=True)
        
        # Calculate previous period for comparison
        previous_period_length = (end_date - start_date).days
        previous_start_date = start_date - timedelta(days=previous_period_length)
        previous_end_date = start_date - timedelta(seconds=1)  # Just before current start
        
        # Get previous period data
        previous_restocks = RestockEntry.objects.select_related(
            'product', 
            'visit_machine_restock__machine',
            'visit_machine_restock__visit'
        ).filter(
            visit_machine_restock__visit__visit_date__gte=previous_start_date,
            visit_machine_restock__visit__visit_date__lte=previous_end_date
        )
        
        if location_id:
            previous_restocks = previous_restocks.filter(visit_machine_restock__machine__location_id=location_id)
        
        # Calculate previous period totals
        previous_revenue = 0
        previous_profit = 0
        
        for entry in previous_restocks:
            # When restocking, the units sold is the number of units restocked
            # This assumes we're restocking back to full capacity
            units_sold = max(0, entry.restocked)
            
            try:
                machine_item = MachineItemPrice.objects.get(
                    machine=entry.visit_machine_restock.machine,
                    product=entry.product
                )
                price = float(machine_item.price)
                
                # Get historical cost at the time of this restock
                historical_cost = self.get_historical_cost(entry.product.id, entry.visit_machine_restock.visit.visit_date)
            except MachineItemPrice.DoesNotExist:
                price = 0
                historical_cost = 0
            
            previous_revenue += units_sold * price
            previous_profit += units_sold * (price - historical_cost)
        
        # Calculate change percentages
        revenue_change = 0
        profit_change = 0
        margin_change = 0
        
        if previous_revenue > 0:
            revenue_change = ((total_revenue - previous_revenue) / previous_revenue) * 100
            
        if previous_profit > 0:
            profit_change = ((total_profit - previous_profit) / previous_profit) * 100
            
        previous_margin = 0
        if previous_revenue > 0:
            previous_margin = (previous_profit / previous_revenue) * 100
            margin_change = profit_margin - previous_margin
        
        data = {
            'revenue': {
                'total': total_revenue,
                'change': revenue_change,
                'by_product': revenue_by_product_list,
                'by_machine': revenue_by_machine_list,
            },
            'profit': {
                'total': total_profit,
                'change': profit_change,
                'by_product': profit_by_product_list,
                'by_machine': profit_by_machine_list,
            },
            'margin': {
                'total': profit_margin,
                'change': margin_change
            }
        }
        
        return Response(data)
    
    def get_historical_cost(self, product_id, date):
        """
        Get the most recent cost of a product at a specific date
        """
        try:
            # Find the most recent cost record before or equal to the given date
            cost_record = ProductCost.objects.filter(
                product_id=product_id,
                date__lte=date
            ).order_by('-date').first()
            
            if cost_record:
                return float(cost_record.unit_cost)
            
            # Fallback to the product's average cost if no historical record exists
            product = Product.objects.get(id=product_id)
            return float(product.average_cost) if product.average_cost else 0
            
        except Exception as e:
            print(f"Error getting historical cost: {e}")
            return 0


class DashboardView(APIView):
    """
    Get key performance indicators for the dashboard
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        # Get filter parameters
        time_range = request.query_params.get('days', '30')
        location_id = request.query_params.get('location')
        machine_type = request.query_params.get('machine_type')
        
        # Parse time range
        end_date = timezone.now()
        
        if time_range == 'today':
            start_date = end_date.replace(hour=0, minute=0, second=0, microsecond=0)
        elif time_range == 'yesterday':
            yesterday = end_date - timedelta(days=1)
            start_date = yesterday.replace(hour=0, minute=0, second=0, microsecond=0)
            end_date = yesterday.replace(hour=23, minute=59, second=59, microsecond=999999)
        else:
            days = int(time_range)
            start_date = end_date - timedelta(days=days)
        
        # Get basic counts
        locations_query = Location.objects.all()
        machines_query = Machine.objects.all()
        
        # Apply location filter if specified
        if location_id:
            machines_query = machines_query.filter(location_id=location_id)
        
        # Apply machine type filter if specified
        if machine_type:
            machines_query = machines_query.filter(machine_type=machine_type)
        
        location_count = locations_query.count()
        machine_count = machines_query.count()
        product_count = Product.objects.count()
        
        # Get low stock items
        low_stock_threshold = 5  # Items with stock below this are considered low
        low_stock_items = MachineItemPrice.objects.filter(
            current_stock__lt=low_stock_threshold,
            current_stock__isnull=False
        ).select_related('machine', 'product', 'machine__location')
        
        # Apply filters to low stock items
        if location_id:
            low_stock_items = low_stock_items.filter(machine__location_id=location_id)
        
        if machine_type:
            low_stock_items = low_stock_items.filter(machine__machine_type=machine_type)
        
        low_stock_items = low_stock_items.order_by('current_stock')
        
        low_stock_data = []
        for item in low_stock_items:
            low_stock_data.append({
                'product': item.product.name,
                'machine': f"{item.machine.machine_type} {item.machine.model}",
                'location': item.machine.location.name,
                'current_stock': item.current_stock,
                'price': item.price
            })
        
        # Recent restocks
        restocks_query = RestockEntry.objects.filter(
            visit_machine_restock__visit__visit_date__gte=start_date,
            visit_machine_restock__visit__visit_date__lte=end_date
        )
        
        if location_id:
            restocks_query = restocks_query.filter(
                visit_machine_restock__machine__location_id=location_id
            )
            
        if machine_type:
            restocks_query = restocks_query.filter(
                visit_machine_restock__machine__machine_type=machine_type
            )
            
        recent_restocks = restocks_query.count()
        
        # Calculate revenue and profit data
        revenue_total = 0
        profit_total = 0
        
        for entry in restocks_query:
            # When restocking, the units sold is the number of units restocked
            # This assumes we're restocking back to full capacity
            units_sold = max(0, entry.restocked)
            
            try:
                machine_item = MachineItemPrice.objects.get(
                    machine=entry.visit_machine_restock.machine,
                    product=entry.product
                )
                price = float(machine_item.price)
                
                # Get historical cost at the time of this restock
                historical_cost = self.get_historical_cost(entry.product.id, entry.visit_machine_restock.visit.visit_date)
            except MachineItemPrice.DoesNotExist:
                price = 0
                historical_cost = 0
            
            entry_revenue = units_sold * price
            entry_profit = units_sold * (price - historical_cost)
            
            revenue_total += entry_revenue
            profit_total += entry_profit
        
        # Calculate profit margin
        profit_margin = 0
        if revenue_total > 0:
            profit_margin = (profit_total / revenue_total) * 100
        
        # Return dashboard data
        dashboard_data = {
            'locations': location_count,
            'machines': machine_count,
            'products': product_count,
            'low_stock_items': low_stock_data,
            'low_stock_count': len(low_stock_data),
            'recent_restocks': recent_restocks,
            'revenue_total': revenue_total,
            'profit_total': profit_total,
            'profit_margin': profit_margin,
        }
        
        return Response(dashboard_data)
    
    def get_historical_cost(self, product_id, date):
        """
        Get the most recent cost of a product at a specific date
        """
        try:
            # Find the most recent cost record before or equal to the given date
            cost_record = ProductCost.objects.filter(
                product_id=product_id,
                date__lte=date
            ).order_by('-date').first()
            
            if cost_record:
                return float(cost_record.unit_cost)
            
            # Fallback to the product's average cost if no historical record exists
            product = Product.objects.get(id=product_id)
            return float(product.average_cost) if product.average_cost else 0
            
        except Exception as e:
            print(f"Error getting historical cost: {e}")
            return 0 