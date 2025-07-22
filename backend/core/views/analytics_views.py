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