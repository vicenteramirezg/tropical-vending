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


class CurrentStockReportView(APIView):
    """
    Get current stock levels for all products across all machines
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        product_id = request.query_params.get('product')
        location_id = request.query_params.get('location')
        machine_id = request.query_params.get('machine')
        
        # Base query for machine item prices (current stock levels)
        stock_query = MachineItemPrice.objects.select_related(
            'product', 'machine', 'machine__location'
        ).filter(current_stock__isnull=False)
        
        # Apply filters
        if product_id:
            stock_query = stock_query.filter(product_id=product_id)
        if location_id:
            stock_query = stock_query.filter(machine__location_id=location_id)
        if machine_id:
            stock_query = stock_query.filter(machine_id=machine_id)
        
        # Prepare stock data by product
        product_stock = {}
        machine_details = []
        
        for item in stock_query:
            product_name = item.product.name
            product_id = item.product.id
            
            # Initialize product data if not exists
            if product_id not in product_stock:
                product_stock[product_id] = {
                    'product_id': product_id,
                    'product_name': product_name,
                    'product_type': item.product.product_type,
                    'warehouse_quantity': item.product.inventory_quantity,
                    'total_machine_stock': 0,
                    'machine_count': 0,
                    'locations': set()
                }
            
            # Add machine stock to product total
            product_stock[product_id]['total_machine_stock'] += item.current_stock
            product_stock[product_id]['machine_count'] += 1
            product_stock[product_id]['locations'].add(item.machine.location.name)
            
            # Add machine detail
            machine_details.append({
                'product_id': product_id,
                'product_name': product_name,
                'machine_id': item.machine.id,
                'machine_name': f"{item.machine.machine_type} {item.machine.model}",
                'location_id': item.machine.location.id,
                'location_name': item.machine.location.name,
                'current_stock': item.current_stock,
                'price': float(item.price),
                'slot': item.slot
            })
        
        # Convert product stock data for response
        product_summary = []
        for product_id, data in product_stock.items():
            data['locations'] = list(data['locations'])  # Convert set to list
            data['total_stock'] = data['warehouse_quantity'] + data['total_machine_stock']
            product_summary.append(data)
        
        # Sort by product name
        product_summary.sort(key=lambda x: x['product_name'])
        machine_details.sort(key=lambda x: (x['location_name'], x['machine_name'], x['product_name']))
        
        return Response({
            'product_summary': product_summary,
            'machine_details': machine_details,
            'generated_at': timezone.now()
        })


class RestockSummaryView(APIView):
    """
    Get restock summary for a specified date range
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        # Get date range parameters
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')
        days = request.query_params.get('days', '7')  # Default to past week
        product_id = request.query_params.get('product')
        location_id = request.query_params.get('location')
        
        # Set date range
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
        )
        
        # Apply filters
        if product_id:
            restocks = restocks.filter(product_id=product_id)
        if location_id:
            restocks = restocks.filter(visit_machine_restock__machine__location_id=location_id)
        
        # Aggregate restock data by product
        product_restocks = {}
        restock_details = []
        
        for entry in restocks:
            product_id = entry.product.id
            product_name = entry.product.name
            
            # Initialize product data if not exists
            if product_id not in product_restocks:
                product_restocks[product_id] = {
                    'product_id': product_id,
                    'product_name': product_name,
                    'product_type': entry.product.product_type,
                    'total_restocked': 0,
                    'total_discarded': 0,
                    'restock_count': 0,
                    'machines_restocked': set(),
                    'locations': set()
                }
            
            # Add to product totals
            product_restocks[product_id]['total_restocked'] += entry.restocked
            product_restocks[product_id]['total_discarded'] += entry.discarded
            product_restocks[product_id]['restock_count'] += 1
            product_restocks[product_id]['machines_restocked'].add(entry.visit_machine_restock.machine.id)
            product_restocks[product_id]['locations'].add(entry.visit_machine_restock.machine.location.name)
            
            # Add detailed restock entry
            restock_details.append({
                'product_id': product_id,
                'product_name': product_name,
                'machine_id': entry.visit_machine_restock.machine.id,
                'machine_name': f"{entry.visit_machine_restock.machine.machine_type} {entry.visit_machine_restock.machine.model}",
                'location_id': entry.visit_machine_restock.machine.location.id,
                'location_name': entry.visit_machine_restock.machine.location.name,
                'visit_date': entry.visit_machine_restock.visit.visit_date,
                'stock_before': entry.stock_before,
                'restocked': entry.restocked,
                'discarded': entry.discarded,
                'stock_after': entry.stock_before + entry.restocked,
                'user': entry.visit_machine_restock.visit.user.username
            })
        
        # Convert product restock data for response
        product_summary = []
        for product_id, data in product_restocks.items():
            data['machines_restocked'] = len(data['machines_restocked'])
            data['locations'] = list(data['locations'])
            product_summary.append(data)
        
        # Sort by total restocked (descending)
        product_summary.sort(key=lambda x: x['total_restocked'], reverse=True)
        restock_details.sort(key=lambda x: x['visit_date'], reverse=True)
        
        return Response({
            'date_range': {
                'start_date': start_date,
                'end_date': end_date,
                'days': (end_date - start_date).days + 1
            },
            'product_summary': product_summary,
            'restock_details': restock_details,
            'total_products': len(product_summary),
            'total_restocks': sum(p['restock_count'] for p in product_summary),
            'total_units_restocked': sum(p['total_restocked'] for p in product_summary),
            'generated_at': timezone.now()
        })


class StockCoverageEstimateView(APIView):
    """
    Calculate stock coverage estimates based on consumption patterns
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        product_id = request.query_params.get('product')
        location_id = request.query_params.get('location')
        analysis_days = int(request.query_params.get('analysis_days', '30'))  # Days to analyze for consumption
        
        # Get current stock levels
        current_stock_query = MachineItemPrice.objects.select_related(
            'product', 'machine', 'machine__location'
        ).filter(current_stock__isnull=False)
        
        if product_id:
            current_stock_query = current_stock_query.filter(product_id=product_id)
        if location_id:
            current_stock_query = current_stock_query.filter(machine__location_id=location_id)
        
        # Calculate consumption patterns from restock data
        end_date = timezone.now()
        start_date = end_date - timedelta(days=analysis_days)
        
        restocks = RestockEntry.objects.select_related(
            'product', 
            'visit_machine_restock__machine',
            'visit_machine_restock__visit'
        ).filter(
            visit_machine_restock__visit__visit_date__gte=start_date,
            visit_machine_restock__visit__visit_date__lte=end_date
        ).order_by(
            'visit_machine_restock__machine',
            'product',
            'visit_machine_restock__visit__visit_date'
        )
        
        if product_id:
            restocks = restocks.filter(product_id=product_id)
        if location_id:
            restocks = restocks.filter(visit_machine_restock__machine__location_id=location_id)
        
        # Calculate consumption rates by machine-product combination
        machine_product_consumption = {}
        
        for entry in restocks:
            machine_id = entry.visit_machine_restock.machine.id
            product_id = entry.product.id
            key = f"{machine_id}-{product_id}"
            
            if key not in machine_product_consumption:
                machine_product_consumption[key] = {
                    'machine': entry.visit_machine_restock.machine,
                    'product': entry.product,
                    'restocks': []
                }
            
            machine_product_consumption[key]['restocks'].append({
                'date': entry.visit_machine_restock.visit.visit_date,
                'stock_before': entry.stock_before,
                'restocked': entry.restocked,
                'stock_after': entry.stock_before + entry.restocked
            })
        
        # Calculate coverage estimates
        coverage_estimates = []
        product_summaries = {}
        
        for key, data in machine_product_consumption.items():
            machine = data['machine']
            product = data['product']
            restocks = data['restocks']
            
            # Get current stock for this machine-product combination
            try:
                current_item = MachineItemPrice.objects.get(
                    machine=machine,
                    product=product
                )
                current_stock = current_item.current_stock or 0
            except MachineItemPrice.DoesNotExist:
                current_stock = 0
            
            # Calculate average weekly consumption
            weekly_consumption = 0
            total_consumption = 0
            consumption_periods = 0
            
            if len(restocks) >= 2:
                for i in range(1, len(restocks)):
                    prev = restocks[i-1]
                    curr = restocks[i]
                    
                    # Calculate consumption between restocks
                    days_between = (curr['date'] - prev['date']).days
                    if days_between > 0:
                        units_consumed = prev['stock_after'] - curr['stock_before']
                        if units_consumed >= 0:  # Valid consumption data
                            daily_consumption = units_consumed / days_between
                            total_consumption += daily_consumption
                            consumption_periods += 1
                
                if consumption_periods > 0:
                    avg_daily_consumption = total_consumption / consumption_periods
                    weekly_consumption = avg_daily_consumption * 7
            
            # Calculate coverage estimate
            weeks_remaining = 0
            if weekly_consumption > 0:
                weeks_remaining = current_stock / weekly_consumption
            
            # Determine status
            status = 'good'
            if weeks_remaining < 1:
                status = 'critical'
            elif weeks_remaining < 2:
                status = 'low'
            elif weeks_remaining < 4:
                status = 'moderate'
            
            coverage_estimate = {
                'machine_id': machine.id,
                'machine_name': f"{machine.machine_type} {machine.model}",
                'location_id': machine.location.id,
                'location_name': machine.location.name,
                'product_id': product.id,
                'product_name': product.name,
                'current_stock': current_stock,
                'weekly_consumption': round(weekly_consumption, 2),
                'weeks_remaining': round(weeks_remaining, 1),
                'status': status,
                'restock_recommended': weeks_remaining < 2,
                'analysis_periods': consumption_periods
            }
            
            coverage_estimates.append(coverage_estimate)
            
            # Aggregate by product for summary
            if product.id not in product_summaries:
                product_summaries[product.id] = {
                    'product_id': product.id,
                    'product_name': product.name,
                    'product_type': product.product_type,
                    'warehouse_quantity': product.inventory_quantity,
                    'total_machine_stock': 0,
                    'total_weekly_consumption': 0,
                    'machine_count': 0,
                    'avg_weeks_remaining': 0,
                    'min_weeks_remaining': float('inf'),
                    'max_weeks_remaining': 0,
                    'critical_machines': 0,
                    'low_machines': 0
                }
            
            summary = product_summaries[product.id]
            summary['total_machine_stock'] += current_stock
            summary['total_weekly_consumption'] += weekly_consumption
            summary['machine_count'] += 1
            
            if weeks_remaining > 0:
                summary['min_weeks_remaining'] = min(summary['min_weeks_remaining'], weeks_remaining)
                summary['max_weeks_remaining'] = max(summary['max_weeks_remaining'], weeks_remaining)
                
            if status == 'critical':
                summary['critical_machines'] += 1
            elif status == 'low':
                summary['low_machines'] += 1
        
        # Finalize product summaries
        for product_id, summary in product_summaries.items():
            if summary['machine_count'] > 0:
                if summary['total_weekly_consumption'] > 0:
                    summary['avg_weeks_remaining'] = round(
                        summary['total_machine_stock'] / summary['total_weekly_consumption'], 1
                    )
                if summary['min_weeks_remaining'] == float('inf'):
                    summary['min_weeks_remaining'] = 0
        
        # Sort coverage estimates by weeks remaining (ascending)
        coverage_estimates.sort(key=lambda x: x['weeks_remaining'])
        
        # Convert product summaries to list and sort
        product_summary = list(product_summaries.values())
        product_summary.sort(key=lambda x: x['avg_weeks_remaining'])
        
        return Response({
            'analysis_period': {
                'start_date': start_date,
                'end_date': end_date,
                'days': analysis_days
            },
            'product_summary': product_summary,
            'machine_estimates': coverage_estimates,
            'summary_stats': {
                'total_products': len(product_summary),
                'total_machines': len(coverage_estimates),
                'critical_count': sum(1 for x in coverage_estimates if x['status'] == 'critical'),
                'low_count': sum(1 for x in coverage_estimates if x['status'] == 'low'),
                'restock_recommended': sum(1 for x in coverage_estimates if x['restock_recommended'])
            },
            'generated_at': timezone.now()
        }) 