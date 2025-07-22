from django.core.management.base import BaseCommand
from django.core.cache import cache
from django.utils import timezone
from datetime import timedelta
from core.views.analytics_views import (
    DashboardView, DemandAnalysisView, RevenueProfitView, 
    CurrentStockReportView, RestockSummaryView, StockCoverageEstimateView
)
from core.models import Location, Machine
import time


class Command(BaseCommand):
    help = 'Manage analytics cache - warm up, clear, or show stats'

    def add_arguments(self, parser):
        parser.add_argument(
            '--action',
            type=str,
            choices=['warmup', 'clear', 'stats'],
            default='warmup',
            help='Action to perform on the cache'
        )
        
        parser.add_argument(
            '--locations',
            type=str,
            help='Comma-separated list of location IDs to cache (default: all)'
        )
        
        parser.add_argument(
            '--days',
            type=str,
            default='7,30,90',
            help='Comma-separated list of day ranges to cache (default: 7,30,90)'
        )

    def handle(self, *args, **options):
        action = options['action']
        
        if action == 'warmup':
            self.warmup_cache(options)
        elif action == 'clear':
            self.clear_cache()
        elif action == 'stats':
            self.show_cache_stats()

    def warmup_cache(self, options):
        """Warm up the analytics cache with common queries"""
        self.stdout.write("Starting analytics cache warmup...")
        
        # Get locations to cache
        if options['locations']:
            location_ids = [int(id.strip()) for id in options['locations'].split(',')]
            locations = Location.objects.filter(id__in=location_ids)
        else:
            locations = Location.objects.all()
        
        # Get day ranges to cache
        day_ranges = [int(d.strip()) for d in options['days'].split(',')]
        
        # Add None for all locations query
        location_list = [None] + list(locations)
        
        total_operations = 0
        successful_operations = 0
        
        start_time = time.time()
        
        for location in location_list:
            location_id = location.id if location else None
            location_name = location.name if location else "All Locations"
            
            self.stdout.write(f"Caching data for: {location_name}")
            
            for days in day_ranges:
                self.stdout.write(f"  - {days} day range...")
                
                # Common parameters
                params = {'days': str(days)}
                if location_id:
                    params['location'] = str(location_id)
                
                # Cache dashboard data
                try:
                    view = DashboardView()
                    view.request = type('Request', (), {
                        'query_params': params
                    })()
                    view.get(view.request)
                    successful_operations += 1
                except Exception as e:
                    self.stdout.write(f"    Error caching dashboard: {e}")
                total_operations += 1
                
                # Cache demand analysis
                try:
                    view = DemandAnalysisView()
                    view.request = type('Request', (), {
                        'query_params': params
                    })()
                    view.get(view.request)
                    successful_operations += 1
                except Exception as e:
                    self.stdout.write(f"    Error caching demand analysis: {e}")
                total_operations += 1
                
                # Cache revenue/profit data
                try:
                    view = RevenueProfitView()
                    view.request = type('Request', (), {
                        'query_params': params
                    })()
                    view.get(view.request)
                    successful_operations += 1
                except Exception as e:
                    self.stdout.write(f"    Error caching revenue/profit: {e}")
                total_operations += 1
                
                # Cache current stock (doesn't use days parameter)
                if days == day_ranges[0]:  # Only cache once per location
                    try:
                        stock_params = {}
                        if location_id:
                            stock_params['location'] = str(location_id)
                        
                        view = CurrentStockReportView()
                        view.request = type('Request', (), {
                            'query_params': stock_params
                        })()
                        view.get(view.request)
                        successful_operations += 1
                    except Exception as e:
                        self.stdout.write(f"    Error caching current stock: {e}")
                    total_operations += 1
                
                # Cache restock summary
                try:
                    view = RestockSummaryView()
                    view.request = type('Request', (), {
                        'query_params': params
                    })()
                    view.get(view.request)
                    successful_operations += 1
                except Exception as e:
                    self.stdout.write(f"    Error caching restock summary: {e}")
                total_operations += 1
                
                # Cache stock coverage (uses analysis_days parameter)
                try:
                    coverage_params = {'analysis_days': str(days)}
                    if location_id:
                        coverage_params['location'] = str(location_id)
                    
                    view = StockCoverageEstimateView()
                    view.request = type('Request', (), {
                        'query_params': coverage_params
                    })()
                    view.get(view.request)
                    successful_operations += 1
                except Exception as e:
                    self.stdout.write(f"    Error caching stock coverage: {e}")
                total_operations += 1
        
        end_time = time.time()
        duration = end_time - start_time
        
        self.stdout.write(
            self.style.SUCCESS(
                f"Cache warmup completed in {duration:.2f} seconds\n"
                f"Successful operations: {successful_operations}/{total_operations}"
            )
        )

    def clear_cache(self):
        """Clear all analytics cache entries"""
        self.stdout.write("Clearing analytics cache...")
        
        # Get all cache keys that start with 'analytics_'
        # Note: This is a simplified approach. In production, you might want
        # to use a more sophisticated cache key pattern matching
        try:
            # Clear all cache (simple approach)
            cache.clear()
            self.stdout.write(
                self.style.SUCCESS("Analytics cache cleared successfully")
            )
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f"Error clearing cache: {e}")
            )

    def show_cache_stats(self):
        """Show cache statistics"""
        self.stdout.write("Analytics Cache Statistics")
        self.stdout.write("=" * 50)
        
        # Test cache connectivity
        test_key = "cache_test"
        test_value = "test_value"
        
        try:
            cache.set(test_key, test_value, 10)
            retrieved_value = cache.get(test_key)
            
            if retrieved_value == test_value:
                self.stdout.write(
                    self.style.SUCCESS("✓ Cache is working correctly")
                )
                cache.delete(test_key)
            else:
                self.stdout.write(
                    self.style.ERROR("✗ Cache is not working correctly")
                )
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f"✗ Cache error: {e}")
            )
        
        # Show cache backend info
        cache_info = cache.__class__.__name__
        self.stdout.write(f"Cache Backend: {cache_info}")
        
        # Show locations and machines count for context
        locations_count = Location.objects.count()
        machines_count = Machine.objects.count()
        
        self.stdout.write(f"Locations in system: {locations_count}")
        self.stdout.write(f"Machines in system: {machines_count}")
        
        # Estimate cache entries that could be created
        day_ranges = 3  # 7, 30, 90 days
        views_per_location = 6  # dashboard, demand, revenue, stock, restock, coverage
        
        estimated_entries = (locations_count + 1) * day_ranges * views_per_location
        self.stdout.write(f"Estimated max cache entries: {estimated_entries}")
        
        self.stdout.write("\nTo warm up the cache, run:")
        self.stdout.write("  python manage.py cache_analytics --action=warmup")
        self.stdout.write("\nTo clear the cache, run:")
        self.stdout.write("  python manage.py cache_analytics --action=clear") 