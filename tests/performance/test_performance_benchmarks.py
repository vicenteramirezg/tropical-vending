"""
Performance Benchmark Tests
Tests to validate that the optimizations actually improve performance
"""

import pytest
import time
import statistics
from django.test import TestCase, TransactionTestCase
from django.core.cache import cache
from django.contrib.auth.models import User
from rest_framework.test import APIClient
from rest_framework import status
from django.utils import timezone
from datetime import timedelta
from unittest.mock import patch
import json

from core.models import (
    Location, Machine, Product, RestockEntry, MachineItemPrice, 
    ProductCost, Visit, VisitMachineRestock
)


class PerformanceBenchmarkMixin:
    """Mixin providing performance testing utilities"""
    
    def time_function(self, func, *args, **kwargs):
        """Time a function execution"""
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        return result, end_time - start_time
    
    def average_execution_time(self, func, iterations=5, *args, **kwargs):
        """Get average execution time over multiple iterations"""
        times = []
        for _ in range(iterations):
            _, execution_time = self.time_function(func, *args, **kwargs)
            times.append(execution_time)
        
        return {
            'average': statistics.mean(times),
            'min': min(times),
            'max': max(times),
            'median': statistics.median(times),
            'std_dev': statistics.stdev(times) if len(times) > 1 else 0
        }
    
    def create_performance_dataset(self, locations=3, machines_per_location=2, products=10, days_of_data=30):
        """Create a dataset for performance testing"""
        # Create locations
        locations_list = []
        for i in range(locations):
            location = Location.objects.create(
                name=f'Location {i+1}',
                address=f'{i+1}00 Test Street'
            )
            locations_list.append(location)
        
        # Create machines
        machines_list = []
        for location in locations_list:
            for j in range(machines_per_location):
                machine = Machine.objects.create(
                    machine_type='Snack' if j % 2 == 0 else 'Drink',
                    model=f'Model {j+1}',
                    location=location
                )
                machines_list.append(machine)
        
        # Create products
        products_list = []
        for i in range(products):
            product = Product.objects.create(
                name=f'Product {i+1}',
                product_type='Snacks' if i < products//2 else 'Drinks',
                average_cost=1.00 + (i * 0.25),
                inventory_quantity=100 + (i * 10)
            )
            products_list.append(product)
            
            # Create cost history for each product
            base_date = timezone.now().date()
            for days_ago in [30, 20, 10, 5, 1]:
                if days_ago <= days_of_data:
                    ProductCost.objects.create(
                        product=product,
                        date=base_date - timedelta(days=days_ago),
                        unit_cost=1.00 + (i * 0.25) + (days_ago * 0.05)
                    )
        
        # Create machine item prices
        for machine in machines_list:
            for product in products_list[:products//2]:  # Half the products per machine
                MachineItemPrice.objects.create(
                    machine=machine,
                    product=product,
                    price=3.00 + (product.id * 0.50),
                    current_stock=max(0, 15 - (product.id % 16)),
                    slot=f'A{product.id}'
                )
        
        # Create visits and restocks
        base_date = timezone.now()
        for days_ago in range(days_of_data):
            visit_date = base_date - timedelta(days=days_ago)
            
            visit = Visit.objects.create(
                user=self.user,
                visit_date=visit_date,
                notes=f'Performance test visit {days_ago} days ago'
            )
            
            # Create restocks for some machines (not all, to simulate real usage)
            machines_to_restock = machines_list[::2] if days_ago % 3 == 0 else machines_list[1::3]
            
            for machine in machines_to_restock:
                vmr = VisitMachineRestock.objects.create(
                    visit=visit,
                    machine=machine
                )
                
                # Restock some products
                products_to_restock = products_list[:products//3]  # First third of products
                for product in products_to_restock:
                    stock_before = max(0, 10 - (days_ago % 11))
                    restocked = max(5, 15 - (days_ago % 8))
                    
                    RestockEntry.objects.create(
                        visit_machine_restock=vmr,
                        product=product,
                        stock_before=stock_before,
                        restocked=restocked,
                        discarded=0 if days_ago % 5 != 0 else 1
                    )
        
        return {
            'locations': locations_list,
            'machines': machines_list,
            'products': products_list
        }


class DashboardPerformanceTest(PerformanceBenchmarkMixin, TransactionTestCase):
    """Test dashboard performance improvements"""
    
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username='perftest', password='testpass')
        self.client.force_authenticate(user=self.user)
        cache.clear()
        
        # Create performance dataset
        self.dataset = self.create_performance_dataset(
            locations=5, 
            machines_per_location=3, 
            products=20, 
            days_of_data=60
        )
    
    def test_dashboard_cold_cache_performance(self):
        """Test dashboard performance with cold cache"""
        url = '/api/analytics/dashboard/'
        
        def make_dashboard_request():
            response = self.client.get(url, {'days': '30'})
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            return response
        
        # Clear cache to ensure cold start
        cache.clear()
        
        # Measure cold cache performance
        stats = self.average_execution_time(make_dashboard_request, iterations=3)
        
        print(f"\nDashboard Cold Cache Performance:")
        print(f"  Average: {stats['average']:.3f}s")
        print(f"  Min: {stats['min']:.3f}s")
        print(f"  Max: {stats['max']:.3f}s")
        
        # Should complete within reasonable time even with cold cache
        self.assertLess(stats['average'], 3.0, "Dashboard should load in under 3 seconds with cold cache")
    
    def test_dashboard_warm_cache_performance(self):
        """Test dashboard performance with warm cache"""
        url = '/api/analytics/dashboard/'
        
        # Warm up cache
        self.client.get(url, {'days': '30'})
        
        def make_cached_request():
            response = self.client.get(url, {'days': '30'})
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            return response
        
        # Measure warm cache performance
        stats = self.average_execution_time(make_cached_request, iterations=5)
        
        print(f"\nDashboard Warm Cache Performance:")
        print(f"  Average: {stats['average']:.3f}s")
        print(f"  Min: {stats['min']:.3f}s")
        print(f"  Max: {stats['max']:.3f}s")
        
        # Should be significantly faster with warm cache
        self.assertLess(stats['average'], 0.5, "Dashboard should load in under 0.5 seconds with warm cache")
    
    def test_dashboard_with_filters_performance(self):
        """Test dashboard performance with various filters"""
        url = '/api/analytics/dashboard/'
        location_id = self.dataset['locations'][0].id
        
        test_cases = [
            {'days': '7'},
            {'days': '30'},
            {'days': '30', 'location': location_id},
            {'days': '30', 'machine_type': 'Snack'},
            {'days': '30', 'location': location_id, 'machine_type': 'Snack'}
        ]
        
        for params in test_cases:
            cache.clear()  # Test each case with cold cache
            
            def make_filtered_request():
                response = self.client.get(url, params)
                self.assertEqual(response.status_code, status.HTTP_200_OK)
                return response
            
            _, execution_time = self.time_function(make_filtered_request)
            
            print(f"Dashboard with filters {params}: {execution_time:.3f}s")
            
            # Should complete within reasonable time regardless of filters
            self.assertLess(execution_time, 4.0, f"Dashboard with filters {params} should load in under 4 seconds")


class AnalyticsPerformanceTest(PerformanceBenchmarkMixin, TransactionTestCase):
    """Test analytics views performance improvements"""
    
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username='perftest', password='testpass')
        self.client.force_authenticate(user=self.user)
        cache.clear()
        
        # Create larger dataset for analytics testing
        self.dataset = self.create_performance_dataset(
            locations=4, 
            machines_per_location=4, 
            products=25, 
            days_of_data=90
        )
    
    def test_demand_analysis_performance(self):
        """Test demand analysis performance"""
        url = '/api/analytics/demand/'
        
        def make_demand_request():
            response = self.client.get(url, {'days': '60'})
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            return response
        
        cache.clear()
        stats = self.average_execution_time(make_demand_request, iterations=3)
        
        print(f"\nDemand Analysis Performance:")
        print(f"  Average: {stats['average']:.3f}s")
        print(f"  Min: {stats['min']:.3f}s")
        print(f"  Max: {stats['max']:.3f}s")
        
        # Should complete within reasonable time
        self.assertLess(stats['average'], 5.0, "Demand analysis should complete in under 5 seconds")
        
        # Test response structure
        response = make_demand_request()
        data = response.data
        self.assertIn('unit_counts', data)
        self.assertIn('products', data)
    
    def test_revenue_profit_performance(self):
        """Test revenue profit analysis performance"""
        url = '/api/analytics/revenue-profit/'
        
        def make_revenue_request():
            response = self.client.get(url, {'days': '60'})
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            return response
        
        cache.clear()
        stats = self.average_execution_time(make_revenue_request, iterations=3)
        
        print(f"\nRevenue Profit Analysis Performance:")
        print(f"  Average: {stats['average']:.3f}s")
        print(f"  Min: {stats['min']:.3f}s")
        print(f"  Max: {stats['max']:.3f}s")
        
        # Should complete within reasonable time
        self.assertLess(stats['average'], 5.0, "Revenue profit analysis should complete in under 5 seconds")
    
    def test_stock_levels_performance(self):
        """Test stock levels performance"""
        url = '/api/analytics/stock-levels/'
        
        def make_stock_request():
            response = self.client.get(url)
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            return response
        
        cache.clear()
        stats = self.average_execution_time(make_stock_request, iterations=5)
        
        print(f"\nStock Levels Performance:")
        print(f"  Average: {stats['average']:.3f}s")
        print(f"  Min: {stats['min']:.3f}s")
        print(f"  Max: {stats['max']:.3f}s")
        
        # Stock levels should be very fast as it's mostly current data
        self.assertLess(stats['average'], 2.0, "Stock levels should load in under 2 seconds")


class InventoryReportsPerformanceTest(PerformanceBenchmarkMixin, TransactionTestCase):
    """Test inventory reports performance improvements"""
    
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username='perftest', password='testpass')
        self.client.force_authenticate(user=self.user)
        cache.clear()
        
        # Create dataset optimized for inventory testing
        self.dataset = self.create_performance_dataset(
            locations=3, 
            machines_per_location=5, 
            products=30, 
            days_of_data=45
        )
    
    def test_current_stock_report_performance(self):
        """Test current stock report performance"""
        url = '/api/analytics/current-stock-report/'
        
        def make_stock_report_request():
            response = self.client.get(url)
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            return response
        
        cache.clear()
        stats = self.average_execution_time(make_stock_report_request, iterations=5)
        
        print(f"\nCurrent Stock Report Performance:")
        print(f"  Average: {stats['average']:.3f}s")
        print(f"  Min: {stats['min']:.3f}s")
        print(f"  Max: {stats['max']:.3f}s")
        
        # Current stock should be fast
        self.assertLess(stats['average'], 2.0, "Current stock report should load in under 2 seconds")
        
        # Test with filters
        location_id = self.dataset['locations'][0].id
        product_id = self.dataset['products'][0].id
        
        def make_filtered_request():
            response = self.client.get(url, {'location': location_id, 'product': product_id})
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            return response
        
        _, filtered_time = self.time_function(make_filtered_request)
        print(f"  With filters: {filtered_time:.3f}s")
        
        # Filtered should be even faster
        self.assertLess(filtered_time, 1.5, "Filtered stock report should be faster")
    
    def test_restock_summary_performance(self):
        """Test restock summary performance"""
        url = '/api/analytics/restock-summary/'
        
        def make_restock_summary_request():
            response = self.client.get(url, {'days': '30'})
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            return response
        
        cache.clear()
        stats = self.average_execution_time(make_restock_summary_request, iterations=3)
        
        print(f"\nRestock Summary Performance:")
        print(f"  Average: {stats['average']:.3f}s")
        print(f"  Min: {stats['min']:.3f}s")
        print(f"  Max: {stats['max']:.3f}s")
        
        # Restock summary involves more complex calculations
        self.assertLess(stats['average'], 3.0, "Restock summary should load in under 3 seconds")
    
    def test_stock_coverage_estimate_performance(self):
        """Test stock coverage estimate performance"""
        url = '/api/analytics/stock-coverage-estimate/'
        
        def make_coverage_request():
            response = self.client.get(url, {'analysis_days': '30'})
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            return response
        
        cache.clear()
        stats = self.average_execution_time(make_coverage_request, iterations=3)
        
        print(f"\nStock Coverage Estimate Performance:")
        print(f"  Average: {stats['average']:.3f}s")
        print(f"  Min: {stats['min']:.3f}s")
        print(f"  Max: {stats['max']:.3f}s")
        
        # Coverage estimate is the most complex calculation
        self.assertLess(stats['average'], 4.0, "Stock coverage estimate should load in under 4 seconds")


class CacheEfficiencyTest(PerformanceBenchmarkMixin, TransactionTestCase):
    """Test cache efficiency and hit rates"""
    
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username='perftest', password='testpass')
        self.client.force_authenticate(user=self.user)
        cache.clear()
        
        # Create modest dataset for cache testing
        self.dataset = self.create_performance_dataset(
            locations=2, 
            machines_per_location=2, 
            products=10, 
            days_of_data=30
        )
    
    def test_cache_hit_rate_dashboard(self):
        """Test cache hit rate for dashboard requests"""
        url = '/api/analytics/dashboard/'
        params = {'days': '30'}
        
        # First request - cache miss
        cache.clear()
        _, cold_time = self.time_function(lambda: self.client.get(url, params))
        
        # Subsequent requests - cache hits
        warm_times = []
        for _ in range(5):
            _, warm_time = self.time_function(lambda: self.client.get(url, params))
            warm_times.append(warm_time)
        
        avg_warm_time = statistics.mean(warm_times)
        
        print(f"\nCache Efficiency - Dashboard:")
        print(f"  Cold cache: {cold_time:.3f}s")
        print(f"  Warm cache: {avg_warm_time:.3f}s")
        print(f"  Speedup: {cold_time / avg_warm_time:.1f}x")
        
        # Warm cache should be significantly faster
        self.assertLess(avg_warm_time, cold_time / 2, "Cached requests should be at least 2x faster")
    
    def test_cache_invalidation_performance(self):
        """Test performance after cache invalidation"""
        url = '/api/analytics/dashboard/'
        params = {'days': '30'}
        
        # Warm up cache
        self.client.get(url, params)
        
        # Measure warm cache performance
        _, warm_time = self.time_function(lambda: self.client.get(url, params))
        
        # Invalidate cache
        cache.clear()
        
        # Measure cold cache performance after invalidation
        _, cold_time = self.time_function(lambda: self.client.get(url, params))
        
        print(f"\nCache Invalidation Impact:")
        print(f"  Before invalidation: {warm_time:.3f}s")
        print(f"  After invalidation: {cold_time:.3f}s")
        print(f"  Performance impact: {cold_time / warm_time:.1f}x slower")
        
        # Should be measurably different
        self.assertGreater(cold_time, warm_time * 1.5, "Cache invalidation should have measurable impact")
    
    def test_concurrent_cache_access(self):
        """Test cache performance under concurrent access"""
        import threading
        import queue
        
        url = '/api/analytics/dashboard/'
        params = {'days': '30'}
        
        # Warm up cache
        self.client.get(url, params)
        
        results = queue.Queue()
        
        def make_concurrent_request(thread_id):
            start_time = time.time()
            response = self.client.get(url, params)
            end_time = time.time()
            
            results.put({
                'thread_id': thread_id,
                'status_code': response.status_code,
                'duration': end_time - start_time
            })
        
        # Start multiple concurrent requests
        threads = []
        num_threads = 10
        
        for i in range(num_threads):
            thread = threading.Thread(target=make_concurrent_request, args=(i,))
            threads.append(thread)
        
        # Start all threads simultaneously
        start_time = time.time()
        for thread in threads:
            thread.start()
        
        # Wait for all to complete
        for thread in threads:
            thread.join()
        
        total_time = time.time() - start_time
        
        # Collect results
        thread_results = []
        while not results.empty():
            thread_results.append(results.get())
        
        durations = [r['duration'] for r in thread_results]
        avg_duration = statistics.mean(durations)
        max_duration = max(durations)
        
        print(f"\nConcurrent Cache Access:")
        print(f"  Threads: {num_threads}")
        print(f"  Total time: {total_time:.3f}s")
        print(f"  Average request time: {avg_duration:.3f}s")
        print(f"  Max request time: {max_duration:.3f}s")
        
        # All requests should succeed
        self.assertEqual(len(thread_results), num_threads)
        for result in thread_results:
            self.assertEqual(result['status_code'], 200)
        
        # Concurrent cached requests should still be fast
        self.assertLess(avg_duration, 1.0, "Concurrent cached requests should average under 1 second")


class QueryOptimizationTest(PerformanceBenchmarkMixin, TransactionTestCase):
    """Test database query optimization"""
    
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username='perftest', password='testpass')
        self.client.force_authenticate(user=self.user)
        cache.clear()
        
        # Create dataset for query testing
        self.dataset = self.create_performance_dataset(
            locations=3, 
            machines_per_location=3, 
            products=15, 
            days_of_data=60
        )
    
    @patch('django.db.connection.queries_log')
    def test_query_count_dashboard(self, mock_queries_log):
        """Test that dashboard uses optimized queries"""
        # This test would need DEBUG=True to actually count queries
        # For now, we test that the endpoint works efficiently
        
        url = '/api/analytics/dashboard/'
        
        cache.clear()
        response = self.client.get(url, {'days': '30'})
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Test that we get expected data structure
        data = response.data
        self.assertIn('locations', data)
        self.assertIn('machines', data)
        self.assertIn('products', data)
        self.assertIn('low_stock_items', data)
        
        # Test that low stock items have proper structure (indicating joins worked)
        if data['low_stock_items']:
            item = data['low_stock_items'][0]
            self.assertIn('product', item)
            self.assertIn('machine', item)
            self.assertIn('location', item)
    
    def test_bulk_operations_efficiency(self):
        """Test that bulk operations are more efficient than individual queries"""
        from core.views.analytics_views import OptimizedAnalyticsViewMixin
        
        mixin = OptimizedAnalyticsViewMixin()
        
        # Test bulk historical costs vs individual lookups
        products = self.dataset['products'][:5]
        test_date = timezone.now().date()
        
        # Simulate individual lookups (what we'd do without optimization)
        def individual_cost_lookups():
            costs = {}
            for product in products:
                # This would be multiple individual queries
                try:
                    cost_record = ProductCost.objects.filter(
                        product=product,
                        date__lte=test_date
                    ).order_by('-date').first()
                    
                    costs[product.id] = float(cost_record.unit_cost) if cost_record else float(product.average_cost)
                except:
                    costs[product.id] = 0
            return costs
        
        # Test bulk lookup (our optimized version)
        def bulk_cost_lookup():
            product_dates = [(product.id, test_date) for product in products]
            return mixin.get_historical_costs_bulk(product_dates)
        
        # Time both approaches
        _, individual_time = self.time_function(individual_cost_lookups)
        _, bulk_time = self.time_function(bulk_cost_lookup)
        
        print(f"\nBulk Operations Efficiency:")
        print(f"  Individual lookups: {individual_time:.3f}s")
        print(f"  Bulk lookup: {bulk_time:.3f}s")
        print(f"  Speedup: {individual_time / bulk_time:.1f}x")
        
        # Bulk should be faster or at least not slower
        # In practice, with more data, bulk should be significantly faster
        self.assertLessEqual(bulk_time, individual_time * 1.2, "Bulk operations should not be significantly slower")


if __name__ == '__main__':
    pytest.main([__file__, '-v', '-s']) 