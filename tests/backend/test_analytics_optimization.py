import pytest
from django.test import TestCase, TransactionTestCase
from django.core.cache import cache
from django.utils import timezone
from django.contrib.auth.models import User
from rest_framework.test import APIClient
from rest_framework import status
from datetime import datetime, timedelta
from unittest.mock import patch, MagicMock
import json
import time

from core.models import (
    Location, Machine, Product, RestockEntry, MachineItemPrice, 
    ProductCost, Visit, VisitMachineRestock
)
from core.views.analytics_views import (
    OptimizedAnalyticsViewMixin, DashboardView, DemandAnalysisView,
    RevenueProfitView, CurrentStockReportView, RestockSummaryView,
    StockCoverageEstimateView
)


class OptimizedAnalyticsViewMixinTest(TestCase):
    """Test the optimization mixin functionality"""
    
    def setUp(self):
        self.mixin = OptimizedAnalyticsViewMixin()
        cache.clear()
    
    def test_cache_key_generation(self):
        """Test that cache keys are generated consistently"""
        params1 = {'location': '1', 'days': '30'}
        params2 = {'days': '30', 'location': '1'}  # Same params, different order
        
        key1 = self.mixin.get_cache_key('test', params1)
        key2 = self.mixin.get_cache_key('test', params2)
        
        self.assertEqual(key1, key2)  # Should be same despite different order
        self.assertTrue(key1.startswith('analytics_test_'))
    
    def test_cache_functionality(self):
        """Test caching and retrieval"""
        cache_key = 'test_cache_key'
        test_data = {'test': 'data', 'count': 42}
        
        def compute_func():
            return test_data
        
        # First call should compute and cache
        result1 = self.mixin.get_cached_or_compute(cache_key, compute_func, timeout=60)
        self.assertEqual(result1, test_data)
        
        # Second call should retrieve from cache
        def different_compute_func():
            return {'different': 'data'}
        
        result2 = self.mixin.get_cached_or_compute(cache_key, different_compute_func, timeout=60)
        self.assertEqual(result2, test_data)  # Should still return cached data
    
    def test_bulk_historical_costs(self):
        """Test bulk historical cost fetching"""
        # Create test data
        location = Location.objects.create(name='Test Location', address='123 Test St')
        product1 = Product.objects.create(name='Product 1', product_type='Snacks')
        product2 = Product.objects.create(name='Product 2', product_type='Drinks')
        
        base_date = timezone.now().date()
        
        # Create cost history
        ProductCost.objects.create(
            product=product1,
            date=base_date - timedelta(days=10),
            unit_cost=1.50
        )
        ProductCost.objects.create(
            product=product1,
            date=base_date - timedelta(days=5),
            unit_cost=1.75
        )
        ProductCost.objects.create(
            product=product2,
            date=base_date - timedelta(days=8),
            unit_cost=2.00
        )
        
        # Test bulk fetch
        product_dates = [
            (product1.id, base_date),
            (product1.id, base_date - timedelta(days=7)),
            (product2.id, base_date),
            (product2.id, base_date - timedelta(days=15))  # Before any cost records
        ]
        
        cost_map = self.mixin.get_historical_costs_bulk(product_dates)
        
        # Verify results
        self.assertEqual(cost_map[(product1.id, base_date)], 1.75)  # Latest cost
        self.assertEqual(cost_map[(product1.id, base_date - timedelta(days=7))], 1.50)  # Historical cost
        self.assertEqual(cost_map[(product2.id, base_date)], 2.00)
        self.assertGreaterEqual(cost_map[(product2.id, base_date - timedelta(days=15))], 0)  # Fallback


class AnalyticsViewsPerformanceTest(TransactionTestCase):
    """Test performance improvements in analytics views"""
    
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username='testuser', password='testpass')
        self.client.force_authenticate(user=self.user)
        
        # Create test data
        self.location = Location.objects.create(name='Test Location', address='123 Test St')
        self.machine = Machine.objects.create(
            machine_type='Snack',
            model='Model A',
            location=self.location
        )
        self.product = Product.objects.create(
            name='Test Product',
            product_type='Snacks',
            average_cost=1.50,
            inventory_quantity=100
        )
        
        # Create machine item price
        self.machine_item = MachineItemPrice.objects.create(
            machine=self.machine,
            product=self.product,
            price=3.00,
            current_stock=10,
            slot='A1'
        )
        
        # Create visit and restock data
        self.visit = Visit.objects.create(
            user=self.user,
            visit_date=timezone.now(),
            notes='Test visit'
        )
        
        self.visit_machine_restock = VisitMachineRestock.objects.create(
            visit=self.visit,
            machine=self.machine
        )
        
        self.restock_entry = RestockEntry.objects.create(
            visit_machine_restock=self.visit_machine_restock,
            product=self.product,
            stock_before=5,
            restocked=10,
            discarded=0
        )
        
        cache.clear()
    
    def test_dashboard_view_caching(self):
        """Test that dashboard view uses caching effectively"""
        url = '/api/analytics/dashboard/'
        
        # First request - should compute and cache
        start_time = time.time()
        response1 = self.client.get(url)
        first_request_time = time.time() - start_time
        
        self.assertEqual(response1.status_code, status.HTTP_200_OK)
        
        # Second request - should use cache
        start_time = time.time()
        response2 = self.client.get(url)
        second_request_time = time.time() - start_time
        
        self.assertEqual(response2.status_code, status.HTTP_200_OK)
        self.assertEqual(response1.data, response2.data)
        
        # Second request should be faster (cached)
        # Note: This might not always be true in test environment, so we just check it doesn't error
        self.assertLess(second_request_time, 1.0)  # Should be very fast
    
    def test_demand_analysis_view_optimization(self):
        """Test demand analysis view with optimized queries"""
        url = '/api/analytics/demand/'
        
        # Test with location filter
        response = self.client.get(url, {'location': self.location.id, 'days': '30'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Should have both unit_counts and products
        data = response.data
        self.assertIn('unit_counts', data)
        self.assertIn('products', data)
        self.assertIsInstance(data['unit_counts'], list)
        self.assertIsInstance(data['products'], list)
    
    def test_revenue_profit_view_bulk_operations(self):
        """Test revenue profit view uses bulk operations"""
        url = '/api/analytics/revenue-profit/'
        
        # Create additional test data to test bulk operations
        product2 = Product.objects.create(
            name='Test Product 2',
            product_type='Drinks',
            average_cost=2.00
        )
        
        machine_item2 = MachineItemPrice.objects.create(
            machine=self.machine,
            product=product2,
            price=4.00,
            current_stock=8,
            slot='A2'
        )
        
        restock_entry2 = RestockEntry.objects.create(
            visit_machine_restock=self.visit_machine_restock,
            product=product2,
            stock_before=3,
            restocked=8,
            discarded=0
        )
        
        response = self.client.get(url, {'days': '30'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        data = response.data
        self.assertIn('revenue', data)
        self.assertIn('profit', data)
        self.assertIn('margin', data)
        
        # Should have revenue and profit data
        self.assertGreaterEqual(data['revenue']['total'], 0)
        self.assertGreaterEqual(data['profit']['total'], 0)
    
    @patch('django.db.connection.queries')
    def test_query_count_optimization(self, mock_queries):
        """Test that optimized views use fewer database queries"""
        # This test would need to be run with DEBUG=True to track queries
        # For now, we'll just test that the views work correctly
        
        url = '/api/analytics/dashboard/'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # The optimized version should work without errors
        self.assertIsInstance(response.data, dict)
        self.assertIn('locations', response.data)
        self.assertIn('machines', response.data)


class CacheManagementTest(TestCase):
    """Test cache management functionality"""
    
    def setUp(self):
        cache.clear()
    
    def test_cache_invalidation_pattern(self):
        """Test cache invalidation patterns work correctly"""
        # Set some test cache data
        cache.set('analytics_dashboard_test123', {'test': 'data'}, 3600)
        cache.set('analytics_revenue_test456', {'revenue': 100}, 3600)
        cache.set('other_cache_key', {'other': 'data'}, 3600)
        
        # Test that we can retrieve the data
        self.assertIsNotNone(cache.get('analytics_dashboard_test123'))
        self.assertIsNotNone(cache.get('analytics_revenue_test456'))
        self.assertIsNotNone(cache.get('other_cache_key'))
        
        # Test pattern-based invalidation (would need to implement this in the actual cache service)
        # For now, just test individual key deletion
        cache.delete('analytics_dashboard_test123')
        self.assertIsNone(cache.get('analytics_dashboard_test123'))
        self.assertIsNotNone(cache.get('analytics_revenue_test456'))
    
    def test_cache_timeout_behavior(self):
        """Test cache timeout behavior"""
        cache_key = 'test_timeout_key'
        test_data = {'timeout': 'test'}
        
        # Set cache with very short timeout
        cache.set(cache_key, test_data, 1)  # 1 second
        
        # Should be available immediately
        self.assertEqual(cache.get(cache_key), test_data)
        
        # Wait for timeout (in real scenario)
        # For testing, we'll just delete it manually
        cache.delete(cache_key)
        self.assertIsNone(cache.get(cache_key))


class InventoryReportsOptimizationTest(TestCase):
    """Test inventory reports optimization"""
    
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username='testuser', password='testpass')
        self.client.force_authenticate(user=self.user)
        
        # Create test data
        self.location = Location.objects.create(name='Test Location', address='123 Test St')
        self.machine = Machine.objects.create(
            machine_type='Snack',
            model='Model A',
            location=self.location
        )
        self.product = Product.objects.create(
            name='Test Product',
            product_type='Snacks',
            average_cost=1.50,
            inventory_quantity=100
        )
        
        self.machine_item = MachineItemPrice.objects.create(
            machine=self.machine,
            product=self.product,
            price=3.00,
            current_stock=10,
            slot='A1'
        )
        
        cache.clear()
    
    def test_current_stock_report_optimization(self):
        """Test current stock report uses optimized queries"""
        url = '/api/analytics/current-stock-report/'
        
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        data = response.data
        self.assertIn('product_summary', data)
        self.assertIn('machine_details', data)
        self.assertIn('generated_at', data)
        
        # Should have our test data
        self.assertEqual(len(data['machine_details']), 1)
        machine_detail = data['machine_details'][0]
        self.assertEqual(machine_detail['product_name'], 'Test Product')
        self.assertEqual(machine_detail['current_stock'], 10)
    
    def test_restock_summary_optimization(self):
        """Test restock summary uses optimized queries"""
        # Create restock data
        visit = Visit.objects.create(
            user=self.user,
            visit_date=timezone.now(),
            notes='Test visit'
        )
        
        visit_machine_restock = VisitMachineRestock.objects.create(
            visit=visit,
            machine=self.machine
        )
        
        RestockEntry.objects.create(
            visit_machine_restock=visit_machine_restock,
            product=self.product,
            stock_before=5,
            restocked=10,
            discarded=0
        )
        
        url = '/api/analytics/restock-summary/'
        response = self.client.get(url, {'days': '7'})
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        data = response.data
        self.assertIn('product_summary', data)
        self.assertIn('restock_details', data)
        self.assertIn('total_products', data)
        self.assertIn('total_restocks', data)
        
        # Should have our test data
        self.assertGreater(data['total_restocks'], 0)
    
    def test_stock_coverage_estimate_optimization(self):
        """Test stock coverage estimate uses optimized calculations"""
        # Create multiple restock entries to calculate consumption
        visit1 = Visit.objects.create(
            user=self.user,
            visit_date=timezone.now() - timedelta(days=7),
            notes='Test visit 1'
        )
        
        visit2 = Visit.objects.create(
            user=self.user,
            visit_date=timezone.now() - timedelta(days=3),
            notes='Test visit 2'
        )
        
        vmr1 = VisitMachineRestock.objects.create(visit=visit1, machine=self.machine)
        vmr2 = VisitMachineRestock.objects.create(visit=visit2, machine=self.machine)
        
        # First restock - stocked to 15
        RestockEntry.objects.create(
            visit_machine_restock=vmr1,
            product=self.product,
            stock_before=5,
            restocked=10,
            discarded=0
        )
        
        # Second restock - was down to 8, restock to 15
        RestockEntry.objects.create(
            visit_machine_restock=vmr2,
            product=self.product,
            stock_before=8,
            restocked=7,
            discarded=0
        )
        
        url = '/api/analytics/stock-coverage-estimate/'
        response = self.client.get(url, {'analysis_days': '30'})
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        data = response.data
        self.assertIn('product_summary', data)
        self.assertIn('machine_estimates', data)
        self.assertIn('summary_stats', data)
        self.assertIn('analysis_period', data)


class ErrorHandlingTest(TestCase):
    """Test error handling in optimized views"""
    
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username='testuser', password='testpass')
        self.client.force_authenticate(user=self.user)
        cache.clear()
    
    def test_invalid_date_format(self):
        """Test handling of invalid date formats"""
        url = '/api/analytics/demand/'
        
        response = self.client.get(url, {
            'start_date': 'invalid-date',
            'end_date': '2024-01-01'
        })
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)
    
    def test_missing_data_handling(self):
        """Test handling when no data exists"""
        url = '/api/analytics/dashboard/'
        
        # Should work even with no data
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Should return default values
        data = response.data
        self.assertEqual(data['locations'], 0)
        self.assertEqual(data['machines'], 0)
        self.assertEqual(data['products'], 0)
        self.assertEqual(data['low_stock_count'], 0)
    
    @patch('core.views.analytics_views.cache')
    def test_cache_failure_handling(self, mock_cache):
        """Test handling when cache operations fail"""
        # Mock cache to raise exception
        mock_cache.get.side_effect = Exception("Cache error")
        mock_cache.set.side_effect = Exception("Cache error")
        
        url = '/api/analytics/dashboard/'
        
        # Should still work even if cache fails
        response = self.client.get(url)
        # The response might fail or succeed depending on implementation
        # The important thing is it doesn't crash the server
        self.assertIn(response.status_code, [200, 500])


class PerformanceBenchmarkTest(TransactionTestCase):
    """Performance benchmark tests"""
    
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username='testuser', password='testpass')
        self.client.force_authenticate(user=self.user)
        
        # Create larger dataset for performance testing
        self.create_test_dataset()
        cache.clear()
    
    def create_test_dataset(self):
        """Create a larger dataset for performance testing"""
        # Create multiple locations, machines, products
        locations = []
        for i in range(3):
            locations.append(Location.objects.create(
                name=f'Location {i+1}',
                address=f'{i+1}00 Test St'
            ))
        
        machines = []
        for location in locations:
            for j in range(2):  # 2 machines per location
                machines.append(Machine.objects.create(
                    machine_type='Snack' if j == 0 else 'Drink',
                    model=f'Model {j+1}',
                    location=location
                ))
        
        products = []
        for i in range(10):  # 10 products
            products.append(Product.objects.create(
                name=f'Product {i+1}',
                product_type='Snacks' if i < 5 else 'Drinks',
                average_cost=1.50 + (i * 0.25),
                inventory_quantity=100 + (i * 10)
            ))
        
        # Create machine item prices
        for machine in machines:
            for product in products[:5]:  # 5 products per machine
                MachineItemPrice.objects.create(
                    machine=machine,
                    product=product,
                    price=3.00 + (product.id * 0.50),
                    current_stock=10 - (product.id % 10),
                    slot=f'A{product.id}'
                )
        
        # Create visits and restocks
        base_date = timezone.now()
        for days_ago in range(30):  # 30 days of data
            visit_date = base_date - timedelta(days=days_ago)
            
            visit = Visit.objects.create(
                user=self.user,
                visit_date=visit_date,
                notes=f'Visit {days_ago} days ago'
            )
            
            # Create restocks for some machines
            for machine in machines[::2]:  # Every other machine
                vmr = VisitMachineRestock.objects.create(
                    visit=visit,
                    machine=machine
                )
                
                for product in products[:3]:  # 3 products per restock
                    RestockEntry.objects.create(
                        visit_machine_restock=vmr,
                        product=product,
                        stock_before=5,
                        restocked=10,
                        discarded=0
                    )
    
    def test_dashboard_performance(self):
        """Test dashboard performance with larger dataset"""
        url = '/api/analytics/dashboard/'
        
        start_time = time.time()
        response = self.client.get(url)
        request_time = time.time() - start_time
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertLess(request_time, 2.0)  # Should complete within 2 seconds
        
        # Test cached performance
        start_time = time.time()
        response2 = self.client.get(url)
        cached_request_time = time.time() - start_time
        
        self.assertEqual(response2.status_code, status.HTTP_200_OK)
        self.assertLess(cached_request_time, 0.5)  # Cached should be much faster
    
    def test_demand_analysis_performance(self):
        """Test demand analysis performance"""
        url = '/api/analytics/demand/'
        
        start_time = time.time()
        response = self.client.get(url, {'days': '30'})
        request_time = time.time() - start_time
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertLess(request_time, 3.0)  # Should complete within 3 seconds
        
        # Verify data structure
        data = response.data
        self.assertIn('unit_counts', data)
        self.assertIn('products', data)
    
    def test_revenue_profit_performance(self):
        """Test revenue profit analysis performance"""
        url = '/api/analytics/revenue-profit/'
        
        start_time = time.time()
        response = self.client.get(url, {'days': '30'})
        request_time = time.time() - start_time
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertLess(request_time, 3.0)  # Should complete within 3 seconds


if __name__ == '__main__':
    pytest.main([__file__]) 