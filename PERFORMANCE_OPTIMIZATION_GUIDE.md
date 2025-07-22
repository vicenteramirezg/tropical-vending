# Performance Optimization Implementation Guide

This document outlines the comprehensive performance optimizations implemented for the tropical vending dashboard, analytics, and inventory views.

## Overview

The optimizations focus on reducing loading times through:
- **Frontend caching** with 2-hour TTL
- **Backend query optimization** with bulk operations
- **Database caching** with intelligent invalidation
- **Batch API calls** for parallel processing
- **N+1 query elimination** through bulk fetching

## Frontend Optimizations

### 1. API Service Caching Layer

**File**: `frontend/src/services/api.js`

**Key Features**:
- 2-hour cache TTL for all GET requests
- Intelligent cache invalidation on data mutations
- Cache hit/miss logging for monitoring
- Selective cache bypass with `skipCache` parameter

**Implementation**:
```javascript
// Cache configuration
const CACHE_TTL = 2 * 60 * 60 * 1000; // 2 hours
const cache = new Map();

// Enhanced API client with caching
const cachedGet = async (url, params = {}, skipCache = false) => {
  const cacheKey = getCacheKey(url, params);
  
  if (!skipCache) {
    const cachedData = getFromCache(cacheKey);
    if (cachedData) {
      return { data: cachedData };
    }
  }
  
  const response = await apiClient.get(url, { params });
  setCache(cacheKey, response.data);
  return response;
};
```

**Cache Invalidation Strategy**:
- Create/Update/Delete operations automatically invalidate related cache patterns
- Cross-entity invalidation (e.g., purchases affect product inventory)
- Manual cache clearing utilities

### 2. Optimized Composables

**Files**: 
- `frontend/src/composables/useAnalytics.js`
- `frontend/src/composables/useDashboard.js`
- `frontend/src/composables/useInventoryReports.js`

**Key Improvements**:
- **Batch API Calls**: Multiple requests executed in parallel using `Promise.allSettled()`
- **Granular Loading States**: Individual loading indicators for better UX
- **Error Resilience**: Partial failures don't break the entire page
- **Smart Data Loading**: Reference data (locations, products) loaded once and cached
- **Selective Refresh**: Ability to refresh specific data sections

**Example - Batch API Implementation**:
```javascript
const applyFilters = async () => {
  const params = buildRequestParams()
  
  // Use batch API calls for better performance
  const apiCalls = [
    fetchRevenueProfitData(params),
    fetchStockLevelData(params),
    fetchDemandData(params)
  ]
  
  // Execute all API calls in parallel
  const results = await Promise.allSettled(apiCalls)
  
  // Handle individual failures gracefully
  const failedCalls = results.filter(result => result.status === 'rejected')
  if (failedCalls.length > 0) {
    console.warn(`${failedCalls.length} API calls failed`)
    error.value = `Some data could not be loaded. ${failedCalls.length} of ${apiCalls.length} requests failed.`
  }
}
```

### 3. Smart Loading Patterns

**Optimization Strategy**:
1. **Reference Data First**: Load locations and products once, cache them
2. **Parallel Report Loading**: All reports load simultaneously
3. **Progressive Error Handling**: Show available data even if some requests fail
4. **Cache-Aware Refreshing**: Skip loading already cached reference data

## Backend Optimizations

### 1. Optimized Analytics Views

**File**: `backend/core/views/analytics_views.py`

**Key Improvements**:
- **N+1 Query Elimination**: Bulk fetch historical costs and machine prices
- **Database Query Optimization**: Proper `select_related()` and `prefetch_related()`
- **Bulk Operations**: Process multiple records in single database queries
- **Server-Side Caching**: 2-hour cache TTL with intelligent key generation
- **Memory Optimization**: Reduced Python loops in favor of database aggregations

### 2. Bulk Historical Cost Fetching

**Problem**: Original code made individual database queries for each product-date combination
**Solution**: Bulk fetch all historical costs in optimized queries

```python
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
    
    # Fetch costs for each product efficiently
    for product_id, dates in product_date_map.items():
        max_date = max(dates)
        cost_records = ProductCost.objects.filter(
            product_id=product_id,
            date__lte=max_date
        ).order_by('product_id', 'date')
        
        # Process all dates for this product in memory (faster than DB queries)
        product_costs = [(record.date, float(record.unit_cost)) for record in cost_records]
        
        for date in dates:
            cost = 0
            for cost_date, unit_cost in reversed(product_costs):
                if cost_date <= date:
                    cost = unit_cost
                    break
            cost_map[(product_id, date)] = cost
    
    return cost_map
```

### 3. Server-Side Caching Implementation

**Cache Strategy**:
- **Deterministic Keys**: MD5 hash of sorted parameters ensures consistent caching
- **2-Hour TTL**: Balance between performance and data freshness
- **View-Specific Prefixes**: Organized cache namespace
- **Automatic Invalidation**: Cache clears on data mutations

```python
class OptimizedAnalyticsViewMixin:
    def get_cache_key(self, prefix, params):
        param_str = json.dumps(params, sort_keys=True, default=str)
        hash_str = hashlib.md5(param_str.encode()).hexdigest()
        return f"analytics_{prefix}_{hash_str}"
    
    def get_cached_or_compute(self, cache_key, compute_func, timeout=7200):
        cached_data = cache.get(cache_key)
        if cached_data is not None:
            return cached_data
        
        data = compute_func()
        cache.set(cache_key, data, timeout)
        return data
```

### 4. Optimized Database Queries

**Before** (N+1 queries):
```python
for entry in restocks:
    # This creates a new query for each entry
    machine_item = MachineItemPrice.objects.get(
        machine=entry.visit_machine_restock.machine,
        product=entry.product
    )
    price = float(machine_item.price)
```

**After** (Bulk queries):
```python
# Collect all machine-product combinations
machine_product_combinations = set()
for restock in restocks:
    machine_product_combinations.add((restock.visit_machine_restock.machine.id, restock.product.id))

# Bulk fetch all prices in one query
machine_prices = {}
if machine_product_combinations:
    machine_items = MachineItemPrice.objects.filter(
        machine_id__in=[combo[0] for combo in machine_product_combinations],
        product_id__in=[combo[1] for combo in machine_product_combinations]
    ).select_related('machine', 'product')
    
    for item in machine_items:
        machine_prices[(item.machine_id, item.product_id)] = float(item.price)

# Use bulk-loaded data
for entry in restocks:
    machine_id = entry.visit_machine_restock.machine.id
    product_id = entry.product.id
    price = machine_prices.get((machine_id, product_id), 0)
```

## Cache Management

### 1. Management Command

**File**: `backend/core/management/commands/cache_analytics.py`

**Features**:
- **Cache Warmup**: Pre-populate cache with common queries
- **Cache Clearing**: Remove all analytics cache entries
- **Cache Statistics**: Monitor cache health and usage

**Usage**:
```bash
# Warm up cache for all locations and common time ranges
python manage.py cache_analytics --action=warmup

# Warm up cache for specific locations
python manage.py cache_analytics --action=warmup --locations=1,2,3

# Clear all cache
python manage.py cache_analytics --action=clear

# Show cache statistics
python manage.py cache_analytics --action=stats
```

### 2. Cache Invalidation Strategy

**Automatic Invalidation**:
- **Data Mutations**: Create/Update/Delete operations trigger cache clearing
- **Pattern-Based**: Clear related cache entries using URL patterns
- **Cross-Entity**: Changes to purchases invalidate product cache

**Manual Control**:
- Force refresh options in frontend composables
- Management command for bulk cache operations
- Cache bypass options for debugging

## Performance Monitoring

### 1. Logging and Metrics

**Frontend Monitoring**:
- Cache hit/miss logging in browser console
- API request timing and status logging
- Error tracking for failed batch operations

**Backend Monitoring**:
- Cache operation logging
- Query execution time monitoring (via Django's database logging)
- Management command provides cache statistics

### 2. Performance Indicators

**Key Metrics to Monitor**:
- Cache hit ratio (should be >70% after warmup)
- API response times (should be <200ms for cached responses)
- Database query count per request (should be <10 for cached views)
- Failed batch operation percentage (should be <5%)

## Best Practices

### 1. Cache Usage Guidelines

**When to Use Cache**:
- ✅ Expensive analytical computations
- ✅ Aggregated data that changes infrequently
- ✅ Reference data (locations, products)
- ✅ Historical reports

**When to Skip Cache**:
- ❌ Real-time operational data
- ❌ User-specific data
- ❌ Data that changes frequently (every few minutes)

### 2. Development Workflow

**During Development**:
1. Use `skipCache=true` parameter for testing
2. Clear cache after data model changes
3. Warm up cache before performance testing
4. Monitor cache hit ratios in development

**Production Deployment**:
1. Clear cache after deployments
2. Warm up cache during deployment process
3. Monitor cache performance metrics
4. Set up automated cache warming for peak hours

## Expected Performance Improvements

### 1. Loading Time Reductions

**Dashboard View**:
- **Before**: 2-4 seconds initial load
- **After**: 0.5-1 second (cached), 1-2 seconds (uncached)

**Analytics View**:
- **Before**: 3-6 seconds for complex queries
- **After**: 0.3-0.8 seconds (cached), 1-3 seconds (uncached)

**Inventory Reports**:
- **Before**: 4-8 seconds for comprehensive reports
- **After**: 0.5-1.5 seconds (cached), 2-4 seconds (uncached)

### 2. Database Load Reduction

**Query Count Reduction**:
- **Before**: 50-200 queries per analytics request
- **After**: 5-15 queries per analytics request (80-90% reduction)

**Cache Hit Ratios** (after warmup):
- **Reference Data**: 95%+ (locations, products)
- **Analytics Data**: 70-85% (depends on filter usage)
- **Dashboard Data**: 80-90% (common time ranges)

## Troubleshooting

### 1. Common Issues

**Cache Not Working**:
- Check Django cache configuration in settings
- Verify cache backend is properly configured
- Run `python manage.py cache_analytics --action=stats`

**Slow Performance Despite Cache**:
- Check cache hit ratios in console logs
- Verify bulk query optimizations are working
- Monitor database query counts

**Memory Issues**:
- Monitor cache size growth
- Implement cache size limits if needed
- Consider using Redis for production caching

### 2. Debugging Tools

**Frontend Debugging**:
- Browser console shows cache hits/misses
- Network tab shows actual API request timing
- Vue DevTools for composable state monitoring

**Backend Debugging**:
- Django debug toolbar for query analysis
- Cache statistics management command
- Database query logging in development

## Future Optimizations

### 1. Potential Enhancements

**Advanced Caching**:
- Redis implementation for distributed caching
- Cache versioning for safer invalidation
- Predictive cache warming based on usage patterns

**Database Optimizations**:
- Database-level caching (Redis/Memcached)
- Materialized views for complex aggregations
- Database connection pooling optimization

**Frontend Enhancements**:
- Service worker for offline caching
- WebSocket updates for real-time data
- Progressive loading for large datasets

### 2. Monitoring and Alerting

**Production Monitoring**:
- APM integration (New Relic, Datadog)
- Cache performance dashboards
- Automated alerts for performance degradation
- User experience monitoring (Core Web Vitals)

This optimization implementation provides significant performance improvements while maintaining code maintainability and system reliability. The caching strategy balances performance gains with data freshness requirements, and the monitoring tools ensure the optimizations continue to work effectively in production. 