from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import permissions, status
from core.models import (
    RestockEntry, MachineItemPrice, Product, Machine, Location, ProductCost
)
from django.db.models import Sum, F, FloatField, Avg, Count, Q, Prefetch
from django.db.models.functions import Coalesce
from datetime import datetime, timedelta
from django.utils import timezone
from django.core.cache import cache
from django.db import connection
import hashlib
import json


class OptimizedAnalyticsViewMixin:
    """Mixin class providing common optimization utilities for analytics views"""
    
    def get_cache_key(self, prefix, params):
        """Generate a cache key based on view prefix and parameters"""
        param_str = json.dumps(params, sort_keys=True, default=str)
        hash_str = hashlib.md5(param_str.encode()).hexdigest()
        return f"analytics_{prefix}_{hash_str}"
    
    def get_cached_or_compute(self, cache_key, compute_func, timeout=7200):  # 2 hours
        """Get data from cache or compute and cache it"""
        cached_data = cache.get(cache_key)
        if cached_data is not None:
            return cached_data
        
        data = compute_func()
        cache.set(cache_key, data, timeout)
        return data
    
    def get_historical_costs_bulk(self, product_dates):
        """
        Bulk fetch historical costs for multiple products and dates
        Returns a dictionary: {(product_id, date): cost}
        """
        if not product_dates:
            return {}
        
        # Group dates by product for efficient querying
        product_date_map = {}
        for product_id, date in product_dates:
            if product_id not in product_date_map:
                product_date_map[product_id] = []
            product_date_map[product_id].append(date)
        
        cost_map = {}
        
        # Fetch costs for each product
        for product_id, dates in product_date_map.items():
            # Get all cost records for this product up to the latest date
            max_date = max(dates)
            cost_records = ProductCost.objects.filter(
                product_id=product_id,
                date__lte=max_date
            ).order_by('product_id', 'date')
            
            # Create a sorted list of costs for this product
            product_costs = [(record.date, float(record.unit_cost)) for record in cost_records]
            
            # For each date, find the most recent cost
            for date in dates:
                cost = 0
                for cost_date, unit_cost in reversed(product_costs):
                    if cost_date <= date:
                        cost = unit_cost
                        break
                
                # Fallback to product average cost if no historical cost found
                if cost == 0:
                    try:
                        product = Product.objects.get(id=product_id)
                        cost = float(product.average_cost) if product.average_cost else 0
                    except Product.DoesNotExist:
                        cost = 0
                
                cost_map[(product_id, date)] = cost
        
        return cost_map


class StockLevelView(OptimizedAnalyticsViewMixin, APIView):
    """
    Get time-series stock data for products/machines
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        product_id = request.query_params.get('product')
        machine_id = request.query_params.get('machine')
        
        # Create cache key
        cache_params = {
            'product': product_id,
            'machine': machine_id,
            'view': 'stock_levels'
        }
        cache_key = self.get_cache_key('stock_levels', cache_params)
        
        def compute_stock_data():
            # Optimized query with proper select_related
            restocks = RestockEntry.objects.select_related(
                'product', 
                'visit_machine_restock__machine__location',
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
                visit = entry.visit_machine_restock.visit
                machine = entry.visit_machine_restock.machine
                
                stock_data.append({
                    'date': visit.visit_date,
                    'product': entry.product.name,
                    'machine': f"{machine.machine_type} {machine.model}",
                    'location': machine.location.name,
                    'stock_before': entry.stock_before,
                    'restocked': entry.restocked,
                    'stock_after': entry.stock_before + entry.restocked
                })
            
            return stock_data
        
        stock_data = self.get_cached_or_compute(cache_key, compute_stock_data)
        return Response(stock_data)


class DemandAnalysisView(OptimizedAnalyticsViewMixin, APIView):
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
        
        # Create cache key
        cache_params = {
            'location': location_id,
            'start_date': start_date,
            'end_date': end_date,
            'view': 'demand_analysis'
        }
        cache_key = self.get_cache_key('demand_analysis', cache_params)
        
        def compute_demand_data():
            # Optimized query with all necessary joins
            restocks = RestockEntry.objects.select_related(
                'product', 
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
            
            # Prefetch machine item prices to avoid N+1 queries
            machine_product_combinations = set()
            for restock in restocks:
                machine_product_combinations.add((restock.visit_machine_restock.machine.id, restock.product.id))
            
            # Bulk fetch machine item prices
            machine_prices = {}
            if machine_product_combinations:
                machine_items = MachineItemPrice.objects.filter(
                    machine_id__in=[combo[0] for combo in machine_product_combinations],
                    product_id__in=[combo[1] for combo in machine_product_combinations]
                ).select_related('machine', 'product')
                
                for item in machine_items:
                    machine_prices[(item.machine_id, item.product_id)] = float(item.price)
            
            # Organize restock data by machine and product
            machine_product_restocks = {}
            product_dates = []  # For bulk historical cost lookup
            
            for restock in restocks:
                machine = restock.visit_machine_restock.machine
                product = restock.product
                visit_date = restock.visit_machine_restock.visit.visit_date
                location = machine.location
                
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
                
                stock_after = restock.stock_before + restock.restocked
                machine_product_restocks[key]['restocks'].append({
                    'date': visit_date,
                    'stock_before': restock.stock_before,
                    'restocked': restock.restocked,
                    'stock_after': stock_after
                })
                
                # Collect product-date combinations for bulk historical cost lookup
                product_dates.append((product.id, visit_date))
            
            # Bulk fetch historical costs
            historical_costs = self.get_historical_costs_bulk(product_dates)
            
            # Calculate demand for each machine-product combination
            demand_data = {
                'unit_counts': [],
                'products': []
            }
            
            product_totals = {}
            
            for key, data in machine_product_restocks.items():
                restocks = data['restocks']
                
                if data['product_id'] not in product_totals:
                    product_totals[data['product_id']] = {
                        'product_id': data['product_id'],
                        'product_name': data['product_name'],
                        'units_sold': 0,
                        'revenue': 0,
                        'profit': 0,
                        'trend': 0
                    }
                
                if len(restocks) >= 2:
                    units_sold_total = 0
                    days_total = 0
                    
                    # Get price from bulk-loaded data
                    price = machine_prices.get((data['machine_id'], data['product_id']), 0)
                    
                    for i in range(1, len(restocks)):
                        prev = restocks[i-1]
                        curr = restocks[i]
                        
                        days_between = (curr['date'] - prev['date']).days
                        if days_between <= 0:
                            days_between = 1
                        
                        units_sold = prev['stock_after'] - curr['stock_before']
                        
                        if units_sold >= 0:
                            # Get historical cost from bulk-loaded data
                            historical_cost = historical_costs.get((data['product_id'], curr['date']), 0)
                            
                            units_sold_total += units_sold
                            days_total += days_between
                            
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
                    
                    if days_total > 0:
                        # Calculate trend
                        trend = 0
                        if len(restocks) >= 3:
                            mid_point = len(restocks) // 2
                            first_half = sum(r['stock_after'] - restocks[i+1]['stock_before'] 
                                           for i, r in enumerate(restocks[:mid_point]) 
                                           if i+1 < mid_point and r['stock_after'] >= restocks[i+1]['stock_before'])
                            second_half = sum(r['stock_after'] - restocks[i+1]['stock_before']
                                            for i, r in enumerate(restocks[mid_point:-1])
                                            if r['stock_after'] >= restocks[i+1+mid_point]['stock_before'])
                            
                            if first_half > 0:
                                trend = ((second_half - first_half) / first_half) * 100
                        
                        # Get latest historical cost
                        latest_historical_cost = historical_costs.get((data['product_id'], restocks[-1]['date']), 0)
                        
                        # Update product totals
                        product_totals[data['product_id']]['units_sold'] += units_sold_total
                        product_totals[data['product_id']]['revenue'] += units_sold_total * price
                        product_totals[data['product_id']]['profit'] += units_sold_total * (price - latest_historical_cost)
                        product_totals[data['product_id']]['trend'] = trend
            
            # Prepare product summary data
            for product_id, data in product_totals.items():
                if data['units_sold'] > 0:
                    demand_data['products'].append(data)
            
            # Sort products by units sold
            demand_data['products'].sort(key=lambda x: x['units_sold'], reverse=True)
            
            return demand_data
        
        demand_data = self.get_cached_or_compute(cache_key, compute_demand_data)
        return Response(demand_data)


class RevenueProfitView(OptimizedAnalyticsViewMixin, APIView):
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
        
        # Create cache key
        cache_params = {
            'location': location_id,
            'start_date': start_date,
            'end_date': end_date,
            'view': 'revenue_profit'
        }
        cache_key = self.get_cache_key('revenue_profit', cache_params)
        
        def compute_revenue_profit_data():
            # Optimized query with proper joins
            restocks = RestockEntry.objects.select_related(
                'product', 
                'visit_machine_restock__machine',
                'visit_machine_restock__visit'
            ).filter(
                visit_machine_restock__visit__visit_date__gte=start_date,
                visit_machine_restock__visit__visit_date__lte=end_date
            )
            
            if location_id:
                restocks = restocks.filter(visit_machine_restock__machine__location_id=location_id)
            
            # Bulk fetch machine item prices
            machine_product_combinations = set()
            product_dates = []
            
            for entry in restocks:
                machine_id = entry.visit_machine_restock.machine.id
                product_id = entry.product.id
                visit_date = entry.visit_machine_restock.visit.visit_date
                
                machine_product_combinations.add((machine_id, product_id))
                product_dates.append((product_id, visit_date))
            
            # Bulk fetch prices
            machine_prices = {}
            if machine_product_combinations:
                machine_items = MachineItemPrice.objects.filter(
                    machine_id__in=[combo[0] for combo in machine_product_combinations],
                    product_id__in=[combo[1] for combo in machine_product_combinations]
                )
                
                for item in machine_items:
                    machine_prices[(item.machine_id, item.product_id)] = float(item.price)
            
            # Bulk fetch historical costs
            historical_costs = self.get_historical_costs_bulk(product_dates)
            
            # Calculate totals
            total_revenue = 0
            total_profit = 0
            revenue_by_product = {}
            profit_by_product = {}
            revenue_by_machine = {}
            profit_by_machine = {}
            
            for entry in restocks:
                units_sold = max(0, entry.restocked)
                machine_id = entry.visit_machine_restock.machine.id
                product_id = entry.product.id
                visit_date = entry.visit_machine_restock.visit.visit_date
                
                # Get price and cost from bulk-loaded data
                price = machine_prices.get((machine_id, product_id), 0)
                historical_cost = historical_costs.get((product_id, visit_date), 0)
                
                entry_revenue = units_sold * price
                entry_profit = units_sold * (price - historical_cost)
                
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
                machine = entry.visit_machine_restock.machine
                machine_name = f"{machine.machine_type} {machine.model}"
                if machine_name not in revenue_by_machine:
                    revenue_by_machine[machine_name] = 0
                    profit_by_machine[machine_name] = 0
                revenue_by_machine[machine_name] += entry_revenue
                profit_by_machine[machine_name] += entry_profit
            
            # Calculate profit margin
            profit_margin = (total_profit / total_revenue * 100) if total_revenue > 0 else 0
            
            # Format response data
            revenue_by_product_list = [{'product': p, 'revenue': r} for p, r in revenue_by_product.items()]
            profit_by_product_list = [{'product': p, 'profit': r} for p, r in profit_by_product.items()]
            revenue_by_machine_list = [{'machine': m, 'revenue': r} for m, r in revenue_by_machine.items()]
            profit_by_machine_list = [{'machine': m, 'profit': r} for m, r in profit_by_machine.items()]
            
            # Sort lists
            revenue_by_product_list.sort(key=lambda x: x['revenue'], reverse=True)
            profit_by_product_list.sort(key=lambda x: x['profit'], reverse=True)
            revenue_by_machine_list.sort(key=lambda x: x['revenue'], reverse=True)
            profit_by_machine_list.sort(key=lambda x: x['profit'], reverse=True)
            
            # Calculate previous period comparison
            previous_period_length = (end_date - start_date).days
            previous_start_date = start_date - timedelta(days=previous_period_length)
            previous_end_date = start_date - timedelta(seconds=1)
            
            # Get previous period data with same optimization
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
            
            # Calculate previous period totals (simplified for performance)
            previous_revenue = 0
            previous_profit = 0
            
            # Bulk fetch for previous period
            prev_product_dates = [(entry.product.id, entry.visit_machine_restock.visit.visit_date) 
                                 for entry in previous_restocks]
            prev_historical_costs = self.get_historical_costs_bulk(prev_product_dates)
            
            for entry in previous_restocks:
                units_sold = max(0, entry.restocked)
                machine_id = entry.visit_machine_restock.machine.id
                product_id = entry.product.id
                visit_date = entry.visit_machine_restock.visit.visit_date
                
                price = machine_prices.get((machine_id, product_id), 0)
                historical_cost = prev_historical_costs.get((product_id, visit_date), 0)
                
                previous_revenue += units_sold * price
                previous_profit += units_sold * (price - historical_cost)
            
            # Calculate change percentages
            revenue_change = ((total_revenue - previous_revenue) / previous_revenue * 100) if previous_revenue > 0 else 0
            profit_change = ((total_profit - previous_profit) / previous_profit * 100) if previous_profit > 0 else 0
            
            previous_margin = (previous_profit / previous_revenue * 100) if previous_revenue > 0 else 0
            margin_change = profit_margin - previous_margin
            
            return {
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
        
        data = self.get_cached_or_compute(cache_key, compute_revenue_profit_data)
        return Response(data)


class DashboardView(OptimizedAnalyticsViewMixin, APIView):
    """
    Get key performance indicators for the dashboard
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        time_range = request.query_params.get('days', '30')
        location_id = request.query_params.get('location')
        machine_type = request.query_params.get('machine_type')
        
        # Create cache key
        cache_params = {
            'time_range': time_range,
            'location': location_id,
            'machine_type': machine_type,
            'view': 'dashboard'
        }
        cache_key = self.get_cache_key('dashboard', cache_params)
        
        def compute_dashboard_data():
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
            
            # Optimized queries with proper filtering
            locations_query = Location.objects.all()
            machines_query = Machine.objects.select_related('location')
            
            if location_id:
                machines_query = machines_query.filter(location_id=location_id)
            
            if machine_type:
                machines_query = machines_query.filter(machine_type=machine_type)
            
            location_count = locations_query.count()
            machine_count = machines_query.count()
            product_count = Product.objects.count()
            
            # Optimized low stock items query
            low_stock_threshold = 5
            low_stock_query = MachineItemPrice.objects.filter(
                current_stock__lt=low_stock_threshold,
                current_stock__isnull=False
            ).select_related('machine__location', 'product')
            
            if location_id:
                low_stock_query = low_stock_query.filter(machine__location_id=location_id)
            
            if machine_type:
                low_stock_query = low_stock_query.filter(machine__machine_type=machine_type)
            
            low_stock_items = low_stock_query.order_by('current_stock')
            
            low_stock_data = []
            for item in low_stock_items:
                low_stock_data.append({
                    'product': item.product.name,
                    'machine': f"{item.machine.machine_type} {item.machine.model}",
                    'location': item.machine.location.name,
                    'current_stock': item.current_stock,
                    'price': item.price
                })
            
            # Optimized restocks query
            restocks_query = RestockEntry.objects.select_related(
                'product',
                'visit_machine_restock__machine',
                'visit_machine_restock__visit'
            ).filter(
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
            
            # Calculate revenue and profit with bulk optimization
            revenue_total = 0
            profit_total = 0
            
            # Bulk fetch machine prices and historical costs
            machine_product_combinations = set()
            product_dates = []
            
            restocks_list = list(restocks_query)
            for entry in restocks_list:
                machine_id = entry.visit_machine_restock.machine.id
                product_id = entry.product.id
                visit_date = entry.visit_machine_restock.visit.visit_date
                
                machine_product_combinations.add((machine_id, product_id))
                product_dates.append((product_id, visit_date))
            
            # Bulk fetch prices
            machine_prices = {}
            if machine_product_combinations:
                machine_items = MachineItemPrice.objects.filter(
                    machine_id__in=[combo[0] for combo in machine_product_combinations],
                    product_id__in=[combo[1] for combo in machine_product_combinations]
                )
                
                for item in machine_items:
                    machine_prices[(item.machine_id, item.product_id)] = float(item.price)
            
            # Bulk fetch historical costs
            historical_costs = self.get_historical_costs_bulk(product_dates)
            
            # Calculate totals
            for entry in restocks_list:
                units_sold = max(0, entry.restocked)
                machine_id = entry.visit_machine_restock.machine.id
                product_id = entry.product.id
                visit_date = entry.visit_machine_restock.visit.visit_date
                
                price = machine_prices.get((machine_id, product_id), 0)
                historical_cost = historical_costs.get((product_id, visit_date), 0)
                
                entry_revenue = units_sold * price
                entry_profit = units_sold * (price - historical_cost)
                
                revenue_total += entry_revenue
                profit_total += entry_profit
            
            # Calculate profit margin
            profit_margin = (profit_total / revenue_total * 100) if revenue_total > 0 else 0
            
            return {
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
        
        dashboard_data = self.get_cached_or_compute(cache_key, compute_dashboard_data)
        return Response(dashboard_data)


class CurrentStockReportView(OptimizedAnalyticsViewMixin, APIView):
    """
    Get current stock levels for all products across all machines
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        product_id = request.query_params.get('product')
        location_id = request.query_params.get('location')
        machine_id = request.query_params.get('machine')
        
        # Create cache key
        cache_params = {
            'product': product_id,
            'location': location_id,
            'machine': machine_id,
            'view': 'current_stock'
        }
        cache_key = self.get_cache_key('current_stock', cache_params)
        
        def compute_stock_data():
            # Optimized query with proper joins
            stock_query = MachineItemPrice.objects.select_related(
                'product', 'machine__location'
            ).filter(current_stock__isnull=False)
            
            # Apply filters
            if product_id:
                stock_query = stock_query.filter(product_id=product_id)
            if location_id:
                stock_query = stock_query.filter(machine__location_id=location_id)
            if machine_id:
                stock_query = stock_query.filter(machine_id=machine_id)
            
            # Process data
            product_stock = {}
            machine_details = []
            
            for item in stock_query:
                product_name = item.product.name
                product_id_key = item.product.id
                
                if product_id_key not in product_stock:
                    product_stock[product_id_key] = {
                        'product_id': product_id_key,
                        'product_name': product_name,
                        'product_type': item.product.product_type,
                        'warehouse_quantity': item.product.inventory_quantity,
                        'total_machine_stock': 0,
                        'machine_count': 0,
                        'locations': set()
                    }
                
                product_stock[product_id_key]['total_machine_stock'] += item.current_stock
                product_stock[product_id_key]['machine_count'] += 1
                product_stock[product_id_key]['locations'].add(item.machine.location.name)
                
                machine_details.append({
                    'product_id': product_id_key,
                    'product_name': product_name,
                    'machine_id': item.machine.id,
                    'machine_name': f"{item.machine.machine_type} {item.machine.model}",
                    'location_id': item.machine.location.id,
                    'location_name': item.machine.location.name,
                    'current_stock': item.current_stock,
                    'price': float(item.price),
                    'slot': item.slot
                })
            
            # Convert product stock data
            product_summary = []
            for product_id_key, data in product_stock.items():
                data['locations'] = list(data['locations'])
                data['total_stock'] = data['warehouse_quantity'] + data['total_machine_stock']
                product_summary.append(data)
            
            # Sort data
            product_summary.sort(key=lambda x: x['product_name'])
            machine_details.sort(key=lambda x: (x['location_name'], x['machine_name'], x['product_name']))
            
            return {
                'product_summary': product_summary,
                'machine_details': machine_details,
                'generated_at': timezone.now()
            }
        
        data = self.get_cached_or_compute(cache_key, compute_stock_data)
        return Response(data)


class RestockSummaryView(OptimizedAnalyticsViewMixin, APIView):
    """
    Get restock summary for a specified date range
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')
        days = request.query_params.get('days', '7')
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
        
        # Create cache key
        cache_params = {
            'start_date': start_date,
            'end_date': end_date,
            'product': product_id,
            'location': location_id,
            'view': 'restock_summary'
        }
        cache_key = self.get_cache_key('restock_summary', cache_params)
        
        def compute_restock_summary():
            # Optimized query
            restocks = RestockEntry.objects.select_related(
                'product', 
                'visit_machine_restock__machine__location',
                'visit_machine_restock__visit__user'
            ).filter(
                visit_machine_restock__visit__visit_date__gte=start_date,
                visit_machine_restock__visit__visit_date__lte=end_date
            )
            
            # Apply filters
            if product_id:
                restocks = restocks.filter(product_id=product_id)
            if location_id:
                restocks = restocks.filter(visit_machine_restock__machine__location_id=location_id)
            
            # Process data
            product_restocks = {}
            restock_details = []
            
            for entry in restocks:
                product_id_key = entry.product.id
                product_name = entry.product.name
                
                if product_id_key not in product_restocks:
                    product_restocks[product_id_key] = {
                        'product_id': product_id_key,
                        'product_name': product_name,
                        'product_type': entry.product.product_type,
                        'total_restocked': 0,
                        'total_discarded': 0,
                        'restock_count': 0,
                        'machines_restocked': set(),
                        'locations': set()
                    }
                
                # Update totals
                product_restocks[product_id_key]['total_restocked'] += entry.restocked
                product_restocks[product_id_key]['total_discarded'] += entry.discarded
                product_restocks[product_id_key]['restock_count'] += 1
                product_restocks[product_id_key]['machines_restocked'].add(entry.visit_machine_restock.machine.id)
                product_restocks[product_id_key]['locations'].add(entry.visit_machine_restock.machine.location.name)
                
                # Add detailed entry
                machine = entry.visit_machine_restock.machine
                restock_details.append({
                    'product_id': product_id_key,
                    'product_name': product_name,
                    'machine_id': machine.id,
                    'machine_name': f"{machine.machine_type} {machine.model}",
                    'location_id': machine.location.id,
                    'location_name': machine.location.name,
                    'visit_date': entry.visit_machine_restock.visit.visit_date,
                    'stock_before': entry.stock_before,
                    'restocked': entry.restocked,
                    'discarded': entry.discarded,
                    'stock_after': entry.stock_before + entry.restocked,
                    'user': entry.visit_machine_restock.visit.user.username
                })
            
            # Convert product restock data
            product_summary = []
            for product_id_key, data in product_restocks.items():
                data['machines_restocked'] = len(data['machines_restocked'])
                data['locations'] = list(data['locations'])
                product_summary.append(data)
            
            # Sort data
            product_summary.sort(key=lambda x: x['total_restocked'], reverse=True)
            restock_details.sort(key=lambda x: x['visit_date'], reverse=True)
            
            return {
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
            }
        
        data = self.get_cached_or_compute(cache_key, compute_restock_summary)
        return Response(data)


class StockCoverageEstimateView(OptimizedAnalyticsViewMixin, APIView):
    """
    Calculate stock coverage estimates based on consumption patterns
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        product_id = request.query_params.get('product')
        location_id = request.query_params.get('location')
        analysis_days = int(request.query_params.get('analysis_days', '30'))
        
        # Create cache key
        cache_params = {
            'product': product_id,
            'location': location_id,
            'analysis_days': analysis_days,
            'view': 'stock_coverage'
        }
        cache_key = self.get_cache_key('stock_coverage', cache_params)
        
        def compute_stock_coverage():
            # Get current stock levels with optimized query
            current_stock_query = MachineItemPrice.objects.select_related(
                'product', 'machine__location'
            ).filter(current_stock__isnull=False)
            
            if product_id:
                current_stock_query = current_stock_query.filter(product_id=product_id)
            if location_id:
                current_stock_query = current_stock_query.filter(machine__location_id=location_id)
            
            # Calculate consumption patterns
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
            
            # Calculate consumption rates
            machine_product_consumption = {}
            
            for entry in restocks:
                machine = entry.visit_machine_restock.machine
                product = entry.product
                key = f"{machine.id}-{product.id}"
                
                if key not in machine_product_consumption:
                    machine_product_consumption[key] = {
                        'machine': machine,
                        'product': product,
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
            
            # Create a lookup for current stock
            current_stock_lookup = {}
            for item in current_stock_query:
                key = f"{item.machine.id}-{item.product.id}"
                current_stock_lookup[key] = {
                    'current_stock': item.current_stock or 0,
                    'machine': item.machine,
                    'product': item.product
                }
            
            for key, data in machine_product_consumption.items():
                machine = data['machine']
                product = data['product']
                restocks = data['restocks']
                
                # Get current stock
                current_stock = current_stock_lookup.get(key, {}).get('current_stock', 0)
                
                # Calculate consumption
                weekly_consumption = 0
                total_consumption = 0
                consumption_periods = 0
                
                if len(restocks) >= 2:
                    for i in range(1, len(restocks)):
                        prev = restocks[i-1]
                        curr = restocks[i]
                        
                        days_between = (curr['date'] - prev['date']).days
                        if days_between > 0:
                            units_consumed = prev['stock_after'] - curr['stock_before']
                            if units_consumed >= 0:
                                daily_consumption = units_consumed / days_between
                                total_consumption += daily_consumption
                                consumption_periods += 1
                    
                    if consumption_periods > 0:
                        avg_daily_consumption = total_consumption / consumption_periods
                        weekly_consumption = avg_daily_consumption * 7
                
                # Calculate coverage
                weeks_remaining = current_stock / weekly_consumption if weekly_consumption > 0 else 0
                
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
                
                # Aggregate by product
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
            for product_id_key, summary in product_summaries.items():
                if summary['machine_count'] > 0:
                    if summary['total_weekly_consumption'] > 0:
                        summary['avg_weeks_remaining'] = round(
                            summary['total_machine_stock'] / summary['total_weekly_consumption'], 1
                        )
                    if summary['min_weeks_remaining'] == float('inf'):
                        summary['min_weeks_remaining'] = 0
            
            # Sort data
            coverage_estimates.sort(key=lambda x: x['weeks_remaining'])
            product_summary = list(product_summaries.values())
            product_summary.sort(key=lambda x: x['avg_weeks_remaining'])
            
            return {
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
            }
        
        data = self.get_cached_or_compute(cache_key, compute_stock_coverage)
        return Response(data)


class AdvancedDemandAnalyticsView(OptimizedAnalyticsViewMixin, APIView):
    """
    Advanced demand analytics using sophisticated SQL query to analyze product performance,
    demand patterns, inventory turnover, and profitability insights
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        # Get filter parameters
        location_id = request.query_params.get('location')
        machine_id = request.query_params.get('machine')
        product_id = request.query_params.get('product')
        days = request.query_params.get('days', '30')
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')
        format_type = request.query_params.get('format', 'json')  # json or csv
        
        # Set the date range
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
        
        # Create cache key
        cache_params = {
            'location': location_id,
            'machine': machine_id,
            'product': product_id,
            'start_date': start_date,
            'end_date': end_date,
            'view': 'advanced_demand_analytics'
        }
        cache_key = self.get_cache_key('advanced_demand_analytics', cache_params)
        
        def compute_advanced_analytics():
            # Build the sophisticated SQL query with proper filtering
            base_query = """
            SELECT
                -- Current visit data
                a.stock_before,
                a.restocked,
                a.discarded,
                f.name AS product_name,
                f.id AS product_id,
                g.price AS product_unit_price,
                h.unit_cost AS product_unit_cost,
                d.name AS machine_name,
                d.id AS machine_id,
                d.machine_type,
                d.model AS machine_model,
                e.name AS location_name,
                e.id AS location_id,
                c.visit_date,
                h.date AS product_cost_date,
                
                -- Previous visit data for same machine × product × location
                prev.c_prev_visit_date,
                prev.prev_stock_before,
                prev.prev_restocked,
                prev.prev_discarded,
                
                -- Days between visits
                CASE
                    WHEN prev.c_prev_visit_date IS NOT NULL
                    THEN DATE_PART('day', c.visit_date::timestamp - prev.c_prev_visit_date::timestamp)
                END AS days_since_prev_visit,
                
                -- Estimated demand calculation
                GREATEST(
                    COALESCE(prev.prev_stock_before, 0)
                    + COALESCE(prev.prev_restocked, 0)
                    - COALESCE(prev.prev_discarded, 0)
                    - COALESCE(a.stock_before, 0),
                    0
                ) AS est_demand_units,
                
                -- Daily demand rate
                ROUND((
                    GREATEST(
                        COALESCE(prev.prev_stock_before, 0)
                        + COALESCE(prev.prev_restocked, 0)
                        - COALESCE(prev.prev_discarded, 0)
                        - COALESCE(a.stock_before, 0),
                        0
                    )
                    / NULLIF(
                        DATE_PART('day', c.visit_date::timestamp - prev.c_prev_visit_date::timestamp)
                        , 0)
                )::numeric, 2) AS est_demand_units_per_day
                
            FROM core_restockentry a
            LEFT JOIN core_visitmachinerestock b ON a.visit_machine_restock_id = b.id
            LEFT JOIN core_visit c ON b.visit_id = c.id
            LEFT JOIN core_machine d ON b.machine_id = d.id
            LEFT JOIN core_location e ON c.location_id = e.id
            LEFT JOIN core_product f ON a.product_id = f.id
            LEFT JOIN core_machineitemprice g ON (b.machine_id = g.machine_id AND a.product_id = g.product_id)
            LEFT JOIN LATERAL (
                SELECT unit_cost, date
                FROM core_productcost
                WHERE product_id = a.product_id
                AND date <= c.visit_date
                ORDER BY date DESC NULLS LAST
                LIMIT 1
            ) h ON TRUE
            
            -- Previous visit subquery
            LEFT JOIN LATERAL (
                SELECT
                    c2.visit_date AS c_prev_visit_date,
                    a2.stock_before AS prev_stock_before,
                    a2.restocked AS prev_restocked,
                    a2.discarded AS prev_discarded
                FROM core_visitmachinerestock b2
                JOIN core_visit c2 ON b2.visit_id = c2.id
                JOIN core_restockentry a2 ON (a2.visit_machine_restock_id = b2.id AND a2.product_id = a.product_id)
                WHERE b2.machine_id = b.machine_id
                AND c2.location_id = c.location_id
                AND c2.visit_date < c.visit_date
                ORDER BY c2.visit_date DESC
                LIMIT 1
            ) prev ON TRUE
            
            WHERE c.visit_date >= %s AND c.visit_date <= %s
            """
            
            # Add filters
            params = [start_date, end_date]
            
            if location_id:
                base_query += " AND c.location_id = %s"
                params.append(location_id)
                
            if machine_id:
                base_query += " AND b.machine_id = %s"
                params.append(machine_id)
                
            if product_id:
                base_query += " AND a.product_id = %s"
                params.append(product_id)
                
            base_query += " ORDER BY c.visit_date DESC"
            
            # Execute the query
            with connection.cursor() as cursor:
                cursor.execute(base_query, params)
                columns = [col[0] for col in cursor.description]
                raw_results = [dict(zip(columns, row)) for row in cursor.fetchall()]
            
            # Transform raw results into meaningful analytics
            return self._process_advanced_analytics_data(raw_results, start_date, end_date)
        
        data = self.get_cached_or_compute(cache_key, compute_advanced_analytics)
        
        # Handle CSV export
        if format_type.lower() == 'csv':
            try:
                return self._export_csv(data, 'advanced_demand_analytics')
            except Exception as e:
                print(f"CSV export error: {e}")
                import traceback
                traceback.print_exc()
                return Response({'error': f'CSV export failed: {str(e)}'}, status=500)
        
        return Response(data)
    
    def _process_advanced_analytics_data(self, raw_results, start_date, end_date):
        """Transform raw SQL results into meaningful analytics insights"""
        
        # Initialize aggregations
        products_performance = {}
        machines_performance = {}
        locations_performance = {}
        time_series_data = []
        
        total_demand = 0
        total_revenue = 0
        total_profit = 0
        total_restocks = 0
        
        # Process each row
        for row in raw_results:
            # Skip rows without valid demand data
            if row['est_demand_units'] is None or row['est_demand_units'] <= 0:
                continue
                
            # Extract key metrics
            demand_units = float(row['est_demand_units'] or 0)
            daily_demand = float(row['est_demand_units_per_day'] or 0)
            price = float(row['product_unit_price'] or 0)
            cost = float(row['product_unit_cost'] or 0)
            revenue = demand_units * price
            profit = demand_units * (price - cost)
            days_between = float(row['days_since_prev_visit'] or 0)
            
            # Aggregate totals
            total_demand += demand_units
            total_revenue += revenue
            total_profit += profit
            total_restocks += 1
            
            # Product performance aggregation
            product_key = row['product_id']
            if product_key not in products_performance:
                products_performance[product_key] = {
                    'product_id': product_key,
                    'product_name': row['product_name'],
                    'total_demand': 0,
                    'total_revenue': 0,
                    'total_profit': 0,
                    'avg_daily_demand': 0,
                    'avg_price': 0,
                    'avg_cost': 0,
                    'profit_margin': 0,
                    'restock_count': 0,
                    'machines_count': set(),
                    'locations_count': set(),
                    'demand_periods': [],
                    'velocity_score': 0,
                    'performance_trend': 'stable'
                }
            
            product_data = products_performance[product_key]
            product_data['total_demand'] += demand_units
            product_data['total_revenue'] += revenue
            product_data['total_profit'] += profit
            product_data['restock_count'] += 1
            product_data['machines_count'].add(row['machine_id'])
            product_data['locations_count'].add(row['location_id'])
            product_data['demand_periods'].append({
                'date': row['visit_date'],
                'demand': demand_units,
                'daily_demand': daily_demand,
                'days_between': days_between
            })
            
            # Machine performance aggregation
            machine_key = row['machine_id']
            if machine_key not in machines_performance:
                machines_performance[machine_key] = {
                    'machine_id': machine_key,
                    'machine_name': row['machine_name'],
                    'machine_type': row['machine_type'],
                    'machine_model': row['machine_model'],
                    'location_id': row['location_id'],
                    'location_name': row['location_name'],
                    'total_demand': 0,
                    'total_revenue': 0,
                    'total_profit': 0,
                    'avg_daily_demand': 0,
                    'product_count': set(),
                    'restock_count': 0,
                    'efficiency_score': 0
                }
            
            machine_data = machines_performance[machine_key]
            machine_data['total_demand'] += demand_units
            machine_data['total_revenue'] += revenue
            machine_data['total_profit'] += profit
            machine_data['restock_count'] += 1
            machine_data['product_count'].add(row['product_id'])
            
            # Location performance aggregation
            location_key = row['location_id']
            if location_key not in locations_performance:
                locations_performance[location_key] = {
                    'location_id': location_key,
                    'location_name': row['location_name'],
                    'total_demand': 0,
                    'total_revenue': 0,
                    'total_profit': 0,
                    'machine_count': set(),
                    'product_count': set(),
                    'avg_daily_demand': 0,
                    'restock_count': 0
                }
            
            location_data = locations_performance[location_key]
            location_data['total_demand'] += demand_units
            location_data['total_revenue'] += revenue
            location_data['total_profit'] += profit
            location_data['restock_count'] += 1
            location_data['machine_count'].add(row['machine_id'])
            location_data['product_count'].add(row['product_id'])
            
            # Time series data for trend analysis
            time_series_data.append({
                'date': row['visit_date'],
                'demand': demand_units,
                'revenue': revenue,
                'profit': profit,
                'daily_demand': daily_demand,
                'product_name': row['product_name'],
                'machine_name': row['machine_name'],
                'location_name': row['location_name']
            })
        
        # Post-process aggregated data
        self._finalize_product_analytics(products_performance)
        self._finalize_machine_analytics(machines_performance)
        self._finalize_location_analytics(locations_performance)
        
        # Calculate overall KPIs
        analysis_days = (end_date - start_date).days
        avg_daily_demand = total_demand / analysis_days if analysis_days > 0 else 0
        overall_profit_margin = (total_profit / total_revenue * 100) if total_revenue > 0 else 0
        
        # Sort results by performance
        top_products = sorted(products_performance.values(), key=lambda x: x['total_demand'], reverse=True)
        top_machines = sorted(machines_performance.values(), key=lambda x: x['total_demand'], reverse=True)
        top_locations = sorted(locations_performance.values(), key=lambda x: x['total_demand'], reverse=True)
        
        return {
            'summary': {
                'analysis_period': {
                    'start_date': start_date,
                    'end_date': end_date,
                    'days': analysis_days
                },
                'total_demand_units': total_demand,
                'total_revenue': round(total_revenue, 2),
                'total_profit': round(total_profit, 2),
                'avg_daily_demand': round(avg_daily_demand, 2),
                'overall_profit_margin': round(overall_profit_margin, 2),
                'total_restocks': total_restocks,
                'unique_products': len(products_performance),
                'unique_machines': len(machines_performance),
                'unique_locations': len(locations_performance)
            },
            'products': {
                'top_performers': top_products[:10],
                'all': top_products
            },
            'machines': {
                'top_performers': top_machines[:10],
                'all': top_machines
            },
            'locations': {
                'performance': top_locations
            },
            'trends': {
                'time_series': sorted(time_series_data, key=lambda x: x['date']),
                'daily_summary': self._generate_daily_summary(time_series_data)
            },
            'insights': self._generate_insights(products_performance, machines_performance, locations_performance),
            'generated_at': timezone.now()
        }
    
    def _finalize_product_analytics(self, products_performance):
        """Calculate final metrics for products"""
        for product_data in products_performance.values():
            # Convert sets to counts
            product_data['machines_count'] = len(product_data['machines_count'])
            product_data['locations_count'] = len(product_data['locations_count'])
            
            # Calculate averages and derived metrics
            if product_data['restock_count'] > 0:
                product_data['avg_revenue_per_restock'] = product_data['total_revenue'] / product_data['restock_count']
                product_data['avg_demand_per_restock'] = product_data['total_demand'] / product_data['restock_count']
            
            if product_data['total_revenue'] > 0:
                product_data['profit_margin'] = (product_data['total_profit'] / product_data['total_revenue']) * 100
            
            # Calculate velocity score (demand per day per machine)
            total_days = sum(period['days_between'] for period in product_data['demand_periods'] if period['days_between'] > 0)
            if total_days > 0 and product_data['machines_count'] > 0:
                product_data['velocity_score'] = product_data['total_demand'] / (total_days / len(product_data['demand_periods'])) / product_data['machines_count']
            
            # Calculate performance trend
            if len(product_data['demand_periods']) >= 3:
                recent_periods = sorted(product_data['demand_periods'], key=lambda x: x['date'])[-3:]
                earlier_periods = sorted(product_data['demand_periods'], key=lambda x: x['date'])[:-3][-3:] if len(product_data['demand_periods']) > 3 else []
                
                if earlier_periods:
                    recent_avg = sum(p['daily_demand'] for p in recent_periods) / len(recent_periods)
                    earlier_avg = sum(p['daily_demand'] for p in earlier_periods) / len(earlier_periods)
                    
                    if recent_avg > earlier_avg * 1.1:
                        product_data['performance_trend'] = 'improving'
                    elif recent_avg < earlier_avg * 0.9:
                        product_data['performance_trend'] = 'declining'
            
            # Clean up temporary data
            del product_data['demand_periods']
    
    def _finalize_machine_analytics(self, machines_performance):
        """Calculate final metrics for machines"""
        for machine_data in machines_performance.values():
            # Convert sets to counts
            machine_data['product_count'] = len(machine_data['product_count'])
            
            # Calculate efficiency score (revenue per restock)
            if machine_data['restock_count'] > 0:
                machine_data['efficiency_score'] = machine_data['total_revenue'] / machine_data['restock_count']
                machine_data['avg_demand_per_restock'] = machine_data['total_demand'] / machine_data['restock_count']
    
    def _finalize_location_analytics(self, locations_performance):
        """Calculate final metrics for locations"""
        for location_data in locations_performance.values():
            # Convert sets to counts
            location_data['machine_count'] = len(location_data['machine_count'])
            location_data['product_count'] = len(location_data['product_count'])
            
            # Calculate averages
            if location_data['machine_count'] > 0:
                location_data['avg_revenue_per_machine'] = location_data['total_revenue'] / location_data['machine_count']
                location_data['avg_demand_per_machine'] = location_data['total_demand'] / location_data['machine_count']
    
    def _generate_daily_summary(self, time_series_data):
        """Generate daily aggregated summary from time series data"""
        daily_data = {}
        for entry in time_series_data:
            date_key = entry['date'].date()
            if date_key not in daily_data:
                daily_data[date_key] = {
                    'date': date_key,
                    'total_demand': 0,
                    'total_revenue': 0,
                    'total_profit': 0,
                    'restock_count': 0
                }
            
            daily_data[date_key]['total_demand'] += entry['demand']
            daily_data[date_key]['total_revenue'] += entry['revenue']
            daily_data[date_key]['total_profit'] += entry['profit']
            daily_data[date_key]['restock_count'] += 1
        
        return sorted(daily_data.values(), key=lambda x: x['date'])
    
    def _generate_insights(self, products_performance, machines_performance, locations_performance):
        """Generate automated insights from the analytics data"""
        insights = []
        
        if products_performance:
            # Top performing product
            top_product = max(products_performance.values(), key=lambda x: x['total_demand'])
            insights.append({
                'type': 'top_product',
                'title': f"Top Performing Product",
                'description': f"{top_product['product_name']} leads with {top_product['total_demand']:.0f} units sold across {top_product['machines_count']} machines",
                'metric': top_product['total_demand'],
                'priority': 'high'
            })
            
            # High margin products
            high_margin_products = [p for p in products_performance.values() if p['profit_margin'] > 50]
            if high_margin_products:
                avg_margin = sum(p['profit_margin'] for p in high_margin_products) / len(high_margin_products)
                insights.append({
                    'type': 'high_margin',
                    'title': f"High Margin Opportunities",
                    'description': f"{len(high_margin_products)} products have >50% profit margins (avg: {avg_margin:.1f}%)",
                    'metric': len(high_margin_products),
                    'priority': 'medium'
                })
        
        if machines_performance:
            # Most efficient machine
            top_machine = max(machines_performance.values(), key=lambda x: x['efficiency_score'])
            insights.append({
                'type': 'top_machine',
                'title': f"Most Efficient Machine",
                'description': f"{top_machine['machine_name']} at {top_machine['location_name']} generates ${top_machine['efficiency_score']:.0f} per restock",
                'metric': top_machine['efficiency_score'],
                'priority': 'medium'
            })
        
        return insights
    
    def _export_csv(self, data, filename_prefix):
        """Export analytics data as CSV with robust error handling"""
        import csv
        from django.http import HttpResponse
        
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename="{filename_prefix}_{timezone.now().strftime("%Y%m%d_%H%M%S")}.csv"'
        
        writer = csv.writer(response)
        
        # Write products data with safe field access
        if data.get('products', {}).get('all'):
            writer.writerow(['=== PRODUCTS PERFORMANCE ==='])
            writer.writerow(['Product Name', 'Total Demand', 'Total Revenue', 'Total Profit', 'Profit Margin %', 'Machines Count', 'Locations Count', 'Velocity Score', 'Trend'])
            
            for product in data['products']['all']:
                try:
                    writer.writerow([
                        product.get('product_name', 'N/A'),
                        product.get('total_demand', 0),
                        round(product.get('total_revenue', 0), 2),
                        round(product.get('total_profit', 0), 2),
                        round(product.get('profit_margin', 0), 2),
                        product.get('machines_count', 0),
                        product.get('locations_count', 0),
                        round(product.get('velocity_score', 0), 3),
                        product.get('performance_trend', 'stable')
                    ])
                except Exception as e:
                    print(f"Error writing product row: {e}, Product data: {product}")
                    # Write a placeholder row to indicate error
                    writer.writerow([
                        product.get('product_name', 'ERROR'),
                        'ERROR', 'ERROR', 'ERROR', 'ERROR', 'ERROR', 'ERROR', 'ERROR', 'ERROR'
                    ])
            
            writer.writerow([])  # Empty row
        
        # Write machines data with safe field access
        if data.get('machines', {}).get('all'):
            writer.writerow(['=== MACHINES PERFORMANCE ==='])
            writer.writerow(['Machine Name', 'Location', 'Total Demand', 'Total Revenue', 'Total Profit', 'Product Count', 'Efficiency Score'])
            
            for machine in data['machines']['all']:
                try:
                    writer.writerow([
                        machine.get('machine_name', 'N/A'),
                        machine.get('location_name', 'N/A'),
                        machine.get('total_demand', 0),
                        round(machine.get('total_revenue', 0), 2),
                        round(machine.get('total_profit', 0), 2),
                        machine.get('product_count', 0),
                        round(machine.get('efficiency_score', 0), 2)
                    ])
                except Exception as e:
                    print(f"Error writing machine row: {e}, Machine data: {machine}")
                    # Write a placeholder row to indicate error
                    writer.writerow([
                        machine.get('machine_name', 'ERROR'),
                        'ERROR', 'ERROR', 'ERROR', 'ERROR', 'ERROR', 'ERROR'
                    ])
        
        return response 


class AdvancedDemandAnalyticsCSVView(AdvancedDemandAnalyticsView):
    """
    Dedicated CSV export endpoint to avoid issues with format query negotiation.
    Returns CSV regardless of query params, honoring same filters as JSON view.
    Reuses parent class logic to avoid duplication and ensure consistency.
    """
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        # Get filter parameters
        location_id = request.query_params.get('location')
        machine_id = request.query_params.get('machine')
        product_id = request.query_params.get('product')
        days = request.query_params.get('days', '30')
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')

        # Set the date range
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

        # Create cache key (separate from JSON cache)
        cache_params = {
            'location': location_id,
            'machine': machine_id,
            'product': product_id,
            'start_date': start_date,
            'end_date': end_date,
            'view': 'advanced_demand_analytics_csv'
        }
        cache_key = self.get_cache_key('advanced_demand_analytics_csv', cache_params)

        # Reuse parent class's compute logic
        def compute_advanced_analytics():
            # Build the sophisticated SQL query with proper filtering
            base_query = """
            SELECT
                -- Current visit data
                a.stock_before,
                a.restocked,
                a.discarded,
                f.name AS product_name,
                f.id AS product_id,
                g.price AS product_unit_price,
                h.unit_cost AS product_unit_cost,
                d.name AS machine_name,
                d.id AS machine_id,
                d.machine_type,
                d.model AS machine_model,
                e.name AS location_name,
                e.id AS location_id,
                c.visit_date,
                h.date AS product_cost_date,
                
                -- Previous visit data for same machine × product × location
                prev.c_prev_visit_date,
                prev.prev_stock_before,
                prev.prev_restocked,
                prev.prev_discarded,
                
                -- Days between visits
                CASE
                    WHEN prev.c_prev_visit_date IS NOT NULL
                    THEN DATE_PART('day', c.visit_date::timestamp - prev.c_prev_visit_date::timestamp)
                END AS days_since_prev_visit,
                
                -- Estimated demand calculation
                GREATEST(
                    COALESCE(prev.prev_stock_before, 0)
                    + COALESCE(prev.prev_restocked, 0)
                    - COALESCE(prev.prev_discarded, 0)
                    - COALESCE(a.stock_before, 0),
                    0
                ) AS est_demand_units,
                
                -- Daily demand rate
                ROUND((
                    GREATEST(
                        COALESCE(prev.prev_stock_before, 0)
                        + COALESCE(prev.prev_restocked, 0)
                        - COALESCE(prev.prev_discarded, 0)
                        - COALESCE(a.stock_before, 0),
                        0
                    )
                    / NULLIF(
                        DATE_PART('day', c.visit_date::timestamp - prev.c_prev_visit_date::timestamp)
                        , 0)
                )::numeric, 2) AS est_demand_units_per_day
                
            FROM core_restockentry a
            LEFT JOIN core_visitmachinerestock b ON a.visit_machine_restock_id = b.id
            LEFT JOIN core_visit c ON b.visit_id = c.id
            LEFT JOIN core_machine d ON b.machine_id = d.id
            LEFT JOIN core_location e ON c.location_id = e.id
            LEFT JOIN core_product f ON a.product_id = f.id
            LEFT JOIN core_machineitemprice g ON (b.machine_id = g.machine_id AND a.product_id = g.product_id)
            LEFT JOIN LATERAL (
                SELECT unit_cost, date
                FROM core_productcost
                WHERE product_id = a.product_id
                AND date <= c.visit_date
                ORDER BY date DESC NULLS LAST
                LIMIT 1
            ) h ON TRUE
            
            -- Previous visit subquery
            LEFT JOIN LATERAL (
                SELECT
                    c2.visit_date AS c_prev_visit_date,
                    a2.stock_before AS prev_stock_before,
                    a2.restocked AS prev_restocked,
                    a2.discarded AS prev_discarded
                FROM core_visitmachinerestock b2
                JOIN core_visit c2 ON b2.visit_id = c2.id
                JOIN core_restockentry a2 ON (a2.visit_machine_restock_id = b2.id AND a2.product_id = a.product_id)
                WHERE b2.machine_id = b.machine_id
                AND c2.location_id = c.location_id
                AND c2.visit_date < c.visit_date
                ORDER BY c2.visit_date DESC
                LIMIT 1
            ) prev ON TRUE
            
            WHERE c.visit_date >= %s AND c.visit_date <= %s
            """
            
            # Add filters
            params = [start_date, end_date]
            
            if location_id:
                base_query += " AND c.location_id = %s"
                params.append(location_id)
                
            if machine_id:
                base_query += " AND b.machine_id = %s"
                params.append(machine_id)
                
            if product_id:
                base_query += " AND a.product_id = %s"
                params.append(product_id)
                
            base_query += " ORDER BY c.visit_date DESC"
            
            # Execute the query
            with connection.cursor() as cursor:
                cursor.execute(base_query, params)
                columns = [col[0] for col in cursor.description]
                raw_results = [dict(zip(columns, row)) for row in cursor.fetchall()]
            
            # Transform raw results into meaningful analytics
            return self._process_advanced_analytics_data(raw_results, start_date, end_date)

        # Get or compute data using same logic as parent
        try:
            data = self.get_cached_or_compute(cache_key, compute_advanced_analytics)
            return self._export_csv(data, 'advanced_demand_analytics')
        except Exception as e:
            # Detailed error logging for debugging
            import traceback
            error_trace = traceback.format_exc()
            print(f"CSV export error: {e}")
            print(f"Full traceback:\n{error_trace}")
            
            # Return a more informative error response
            return Response({
                'error': 'CSV export failed',
                'message': str(e),
                'type': type(e).__name__
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
