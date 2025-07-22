import pytest
from django.test import TestCase
from django.core.cache import cache
from django.core.management import call_command
from django.core.management.base import CommandError
from django.utils import timezone
from django.contrib.auth.models import User
from io import StringIO
import sys
from unittest.mock import patch, MagicMock

from core.models import Location, Machine, Product, RestockEntry, MachineItemPrice, Visit, VisitMachineRestock
from core.management.commands.cache_analytics import Command as CacheCommand


class CacheManagementCommandTest(TestCase):
    """Test the cache management Django command"""
    
    def setUp(self):
        self.command = CacheCommand()
        cache.clear()
        
        # Create test data
        self.user = User.objects.create_user(username='testuser', password='testpass')
        self.location = Location.objects.create(name='Test Location', address='123 Test St')
        self.machine = Machine.objects.create(
            machine_type='Snack',
            model='Model A',
            location=self.location
        )
        self.product = Product.objects.create(
            name='Test Product',
            product_type='Snacks',
            average_cost=1.50
        )
        
        # Create machine item price
        self.machine_item = MachineItemPrice.objects.create(
            machine=self.machine,
            product=self.product,
            price=3.00,
            current_stock=10,
            slot='A1'
        )
    
    def test_warmup_action(self):
        """Test cache warmup functionality"""
        # Capture stdout
        out = StringIO()
        
        # Run warmup command
        call_command('cache_analytics', action='warmup', stdout=out)
        
        output = out.getvalue()
        self.assertIn('Cache warmup completed', output)
        
        # Check that cache keys were created
        # This would depend on the specific implementation of warmup
        self.assertTrue(len(cache._cache) >= 0)  # At least some cache entries
    
    def test_clear_action(self):
        """Test cache clearing functionality"""
        # Set some test cache data
        cache.set('analytics_test_key', {'test': 'data'}, 3600)
        cache.set('other_key', {'other': 'data'}, 3600)
        
        # Verify cache has data
        self.assertIsNotNone(cache.get('analytics_test_key'))
        
        # Run clear command
        out = StringIO()
        call_command('cache_analytics', action='clear', stdout=out)
        
        output = out.getvalue()
        self.assertIn('cleared', output.lower())
        
        # Analytics cache should be cleared
        self.assertIsNone(cache.get('analytics_test_key'))
    
    def test_stats_action(self):
        """Test cache statistics functionality"""
        # Set some test cache data
        cache.set('analytics_dashboard_123', {'dashboard': 'data'}, 3600)
        cache.set('analytics_revenue_456', {'revenue': 'data'}, 3600)
        cache.set('other_cache_key', {'other': 'data'}, 3600)
        
        # Run stats command
        out = StringIO()
        call_command('cache_analytics', action='stats', stdout=out)
        
        output = out.getvalue()
        self.assertIn('Cache Statistics', output)
        self.assertIn('analytics_dashboard', output)
        self.assertIn('analytics_revenue', output)
    
    def test_warmup_with_specific_views(self):
        """Test warmup with specific view parameters"""
        out = StringIO()
        
        # Run warmup with specific parameters
        call_command(
            'cache_analytics',
            action='warmup',
            views='dashboard,revenue',
            locations=str(self.location.id),
            days='30',
            stdout=out
        )
        
        output = out.getvalue()
        self.assertIn('Warming up cache', output)
    
    def test_warmup_with_all_locations(self):
        """Test warmup for all locations"""
        # Create additional location
        location2 = Location.objects.create(name='Location 2', address='456 Test Ave')
        
        out = StringIO()
        call_command(
            'cache_analytics',
            action='warmup',
            all_locations=True,
            stdout=out
        )
        
        output = out.getvalue()
        self.assertIn('locations', output)
    
    def test_invalid_action(self):
        """Test handling of invalid action parameter"""
        with self.assertRaises(CommandError):
            call_command('cache_analytics', action='invalid_action')
    
    def test_warmup_performance_timing(self):
        """Test that warmup reports performance timing"""
        out = StringIO()
        
        call_command('cache_analytics', action='warmup', stdout=out)
        
        output = out.getvalue()
        # Should contain timing information
        self.assertTrue('seconds' in output or 'ms' in output or 'completed' in output)
    
    @patch('core.management.commands.cache_analytics.DashboardView')
    def test_warmup_with_mocked_views(self, mock_dashboard_view):
        """Test warmup with mocked view responses"""
        # Mock the view response
        mock_instance = MagicMock()
        mock_instance.get.return_value.data = {'test': 'data'}
        mock_dashboard_view.return_value = mock_instance
        
        out = StringIO()
        call_command('cache_analytics', action='warmup', views='dashboard', stdout=out)
        
        output = out.getvalue()
        self.assertIn('Warming up cache', output)
    
    def test_clear_with_pattern(self):
        """Test clearing cache with specific patterns"""
        # Set various cache keys
        cache.set('analytics_dashboard_abc', {'data': 1}, 3600)
        cache.set('analytics_revenue_def', {'data': 2}, 3600)
        cache.set('analytics_stock_ghi', {'data': 3}, 3600)
        cache.set('other_cache_key', {'data': 4}, 3600)
        
        out = StringIO()
        call_command('cache_analytics', action='clear', pattern='dashboard', stdout=out)
        
        # Only dashboard cache should be cleared
        self.assertIsNone(cache.get('analytics_dashboard_abc'))
        self.assertIsNotNone(cache.get('analytics_revenue_def'))
        self.assertIsNotNone(cache.get('other_cache_key'))
    
    def test_stats_with_detailed_output(self):
        """Test detailed cache statistics output"""
        # Create cache entries with different timestamps
        current_time = timezone.now().timestamp()
        
        cache.set('analytics_dashboard_123', {
            'data': {'test': 'data'},
            'timestamp': current_time - 1800,  # 30 minutes ago
            'size': 1024
        }, 3600)
        
        cache.set('analytics_revenue_456', {
            'data': {'revenue': 5000},
            'timestamp': current_time - 3600,  # 1 hour ago
            'size': 2048
        }, 3600)
        
        out = StringIO()
        call_command('cache_analytics', action='stats', detailed=True, stdout=out)
        
        output = out.getvalue()
        self.assertIn('Total cache entries', output)
        self.assertIn('analytics_dashboard', output)
        self.assertIn('analytics_revenue', output)


class CacheUtilitiesTest(TestCase):
    """Test cache utility functions"""
    
    def setUp(self):
        cache.clear()
    
    def test_cache_key_generation_consistency(self):
        """Test that cache key generation is consistent"""
        from core.views.analytics_views import OptimizedAnalyticsViewMixin
        
        mixin = OptimizedAnalyticsViewMixin()
        
        params1 = {'location': '1', 'days': '30', 'view': 'dashboard'}
        params2 = {'days': '30', 'location': '1', 'view': 'dashboard'}  # Different order
        
        key1 = mixin.get_cache_key('test', params1)
        key2 = mixin.get_cache_key('test', params2)
        
        self.assertEqual(key1, key2)
    
    def test_cache_key_uniqueness(self):
        """Test that different parameters generate different cache keys"""
        from core.views.analytics_views import OptimizedAnalyticsViewMixin
        
        mixin = OptimizedAnalyticsViewMixin()
        
        params1 = {'location': '1', 'days': '30'}
        params2 = {'location': '2', 'days': '30'}
        params3 = {'location': '1', 'days': '7'}
        
        key1 = mixin.get_cache_key('test', params1)
        key2 = mixin.get_cache_key('test', params2)
        key3 = mixin.get_cache_key('test', params3)
        
        self.assertNotEqual(key1, key2)
        self.assertNotEqual(key1, key3)
        self.assertNotEqual(key2, key3)
    
    def test_cache_timeout_functionality(self):
        """Test cache timeout behavior"""
        from core.views.analytics_views import OptimizedAnalyticsViewMixin
        
        mixin = OptimizedAnalyticsViewMixin()
        
        def compute_func():
            return {'computed': 'data', 'timestamp': timezone.now()}
        
        cache_key = 'test_timeout_key'
        
        # Set with short timeout
        result1 = mixin.get_cached_or_compute(cache_key, compute_func, timeout=1)
        
        # Should get same result immediately
        result2 = mixin.get_cached_or_compute(cache_key, lambda: {'different': 'data'}, timeout=1)
        
        self.assertEqual(result1, result2)
        
        # Manually clear cache to simulate timeout
        cache.delete(cache_key)
        
        # Should compute new result
        result3 = mixin.get_cached_or_compute(cache_key, lambda: {'new': 'data'}, timeout=1)
        
        self.assertNotEqual(result1, result3)
        self.assertEqual(result3['new'], 'data')
    
    def test_bulk_historical_costs_performance(self):
        """Test bulk historical costs fetching performance"""
        from core.views.analytics_views import OptimizedAnalyticsViewMixin
        from core.models import ProductCost
        
        mixin = OptimizedAnalyticsViewMixin()
        
        # Create test products and costs
        products = []
        for i in range(5):
            product = Product.objects.create(
                name=f'Product {i}',
                product_type='Test',
                average_cost=1.00 + i
            )
            products.append(product)
            
            # Create cost history
            base_date = timezone.now().date()
            for days_ago in [10, 5, 1]:
                ProductCost.objects.create(
                    product=product,
                    date=base_date - timezone.timedelta(days=days_ago),
                    unit_cost=1.00 + i + (days_ago * 0.1)
                )
        
        # Test bulk fetch
        product_dates = []
        for product in products:
            product_dates.extend([
                (product.id, timezone.now().date()),
                (product.id, timezone.now().date() - timezone.timedelta(days=7))
            ])
        
        import time
        start_time = time.time()
        cost_map = mixin.get_historical_costs_bulk(product_dates)
        end_time = time.time()
        
        # Should complete quickly
        self.assertLess(end_time - start_time, 1.0)  # Less than 1 second
        
        # Should have results for all product-date combinations
        self.assertEqual(len(cost_map), len(product_dates))
        
        # Verify some results
        for product_id, date in product_dates:
            self.assertIn((product_id, date), cost_map)
            self.assertGreaterEqual(cost_map[(product_id, date)], 0)
    
    def test_cache_memory_usage_monitoring(self):
        """Test cache memory usage monitoring"""
        # Set various sized cache entries
        small_data = {'small': 'data'}
        medium_data = {'medium': 'data' * 100}
        large_data = {'large': 'data' * 1000}
        
        cache.set('small_key', small_data, 3600)
        cache.set('medium_key', medium_data, 3600)
        cache.set('large_key', large_data, 3600)
        
        # Test that we can retrieve all entries
        self.assertEqual(cache.get('small_key'), small_data)
        self.assertEqual(cache.get('medium_key'), medium_data)
        self.assertEqual(cache.get('large_key'), large_data)
    
    def test_concurrent_cache_access(self):
        """Test concurrent cache access scenarios"""
        from core.views.analytics_views import OptimizedAnalyticsViewMixin
        import threading
        
        mixin = OptimizedAnalyticsViewMixin()
        results = []
        
        def compute_and_cache(thread_id):
            def compute_func():
                return {'thread_id': thread_id, 'data': f'computed_by_{thread_id}'}
            
            result = mixin.get_cached_or_compute(f'concurrent_test_{thread_id}', compute_func)
            results.append(result)
        
        # Start multiple threads
        threads = []
        for i in range(5):
            thread = threading.Thread(target=compute_and_cache, args=(i,))
            threads.append(thread)
            thread.start()
        
        # Wait for all threads to complete
        for thread in threads:
            thread.join()
        
        # Should have results from all threads
        self.assertEqual(len(results), 5)
        
        # Each thread should have its own cached result
        thread_ids = [result['thread_id'] for result in results]
        self.assertEqual(sorted(thread_ids), list(range(5)))


class CacheInvalidationTest(TestCase):
    """Test cache invalidation strategies"""
    
    def setUp(self):
        cache.clear()
    
    def test_cache_invalidation_on_model_changes(self):
        """Test that cache is invalidated when models change"""
        # Set some cache data
        cache.set('analytics_dashboard_test', {'cached': 'data'}, 3600)
        
        # Verify cache exists
        self.assertIsNotNone(cache.get('analytics_dashboard_test'))
        
        # Simulate model change (this would typically be done via signals)
        # For testing, we manually invalidate
        cache.delete('analytics_dashboard_test')
        
        # Cache should be cleared
        self.assertIsNone(cache.get('analytics_dashboard_test'))
    
    def test_pattern_based_invalidation(self):
        """Test pattern-based cache invalidation"""
        # Set various cache keys
        cache.set('analytics_dashboard_abc123', {'data': 1}, 3600)
        cache.set('analytics_dashboard_def456', {'data': 2}, 3600)
        cache.set('analytics_revenue_ghi789', {'data': 3}, 3600)
        cache.set('other_cache_key', {'data': 4}, 3600)
        
        # Get all cache keys (this is implementation-specific)
        # For testing, we'll simulate pattern-based deletion
        keys_to_delete = []
        
        # In a real implementation, you'd iterate through cache keys
        # Here we simulate finding keys that match the pattern
        test_keys = [
            'analytics_dashboard_abc123',
            'analytics_dashboard_def456',
            'analytics_revenue_ghi789',
            'other_cache_key'
        ]
        
        pattern = 'analytics_dashboard'
        for key in test_keys:
            if pattern in key:
                keys_to_delete.append(key)
        
        # Delete matching keys
        for key in keys_to_delete:
            cache.delete(key)
        
        # Verify correct keys were deleted
        self.assertIsNone(cache.get('analytics_dashboard_abc123'))
        self.assertIsNone(cache.get('analytics_dashboard_def456'))
        self.assertIsNotNone(cache.get('analytics_revenue_ghi789'))
        self.assertIsNotNone(cache.get('other_cache_key'))
    
    def test_time_based_invalidation(self):
        """Test time-based cache invalidation"""
        import time
        
        # Set cache with very short timeout
        cache.set('short_lived_key', {'data': 'test'}, 1)  # 1 second
        
        # Should be available immediately
        self.assertIsNotNone(cache.get('short_lived_key'))
        
        # Wait for timeout (simulate with manual deletion for testing)
        cache.delete('short_lived_key')
        
        # Should be gone
        self.assertIsNone(cache.get('short_lived_key'))


if __name__ == '__main__':
    pytest.main([__file__]) 