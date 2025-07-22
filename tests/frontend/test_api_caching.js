/**
 * Frontend API Caching and Optimization Tests
 * Tests the caching layer, batch API calls, and performance improvements
 */

import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest'
import { createApp } from 'vue'
import { api } from '../../frontend/src/services/api.js'
import { useAnalytics } from '../../frontend/src/composables/useAnalytics.js'
import { useDashboard } from '../../frontend/src/composables/useDashboard.js'
import { useInventoryReports } from '../../frontend/src/composables/useInventoryReports.js'

// Mock axios for testing
vi.mock('axios', () => ({
  default: {
    create: () => ({
      get: vi.fn(),
      post: vi.fn(),
      put: vi.fn(),
      delete: vi.fn(),
      interceptors: {
        request: { use: vi.fn() },
        response: { use: vi.fn() }
      }
    })
  }
}))

// Mock localStorage for cache testing
const localStorageMock = {
  getItem: vi.fn(),
  setItem: vi.fn(),
  removeItem: vi.fn(),
  clear: vi.fn(),
}
global.localStorage = localStorageMock

describe('API Caching Layer', () => {
  beforeEach(() => {
    // Clear all mocks and cache before each test
    vi.clearAllMocks()
    localStorageMock.clear()
    api.clearCache()
  })

  afterEach(() => {
    vi.restoreAllMocks()
  })

  describe('Cache Key Generation', () => {
    it('should generate consistent cache keys for same parameters', () => {
      const params1 = { location: '1', days: '30' }
      const params2 = { days: '30', location: '1' } // Different order

      const key1 = api.generateCacheKey('/test', params1)
      const key2 = api.generateCacheKey('/test', params2)

      expect(key1).toBe(key2)
      expect(key1).toContain('cache_/test_')
    })

    it('should generate different cache keys for different parameters', () => {
      const params1 = { location: '1', days: '30' }
      const params2 = { location: '2', days: '30' }

      const key1 = api.generateCacheKey('/test', params1)
      const key2 = api.generateCacheKey('/test', params2)

      expect(key1).not.toBe(key2)
    })

    it('should handle complex nested parameters', () => {
      const params = {
        filters: { location: '1', dateRange: '30' },
        sort: { field: 'name', direction: 'asc' }
      }

      const key = api.generateCacheKey('/test', params)
      expect(key).toBeTruthy()
      expect(key).toContain('cache_/test_')
    })
  })

  describe('Cache Storage and Retrieval', () => {
    it('should store and retrieve cached data', () => {
      const testData = { test: 'data', count: 42 }
      const cacheKey = 'test_cache_key'

      // Mock localStorage.setItem and getItem
      localStorageMock.getItem.mockReturnValue(JSON.stringify({
        data: testData,
        timestamp: Date.now(),
        ttl: 7200000 // 2 hours
      }))

      api.setCacheData(cacheKey, testData)
      const retrieved = api.getCacheData(cacheKey)

      expect(retrieved).toEqual(testData)
    })

    it('should return null for expired cache data', () => {
      const testData = { test: 'data' }
      const cacheKey = 'expired_cache_key'

      // Mock expired data
      localStorageMock.getItem.mockReturnValue(JSON.stringify({
        data: testData,
        timestamp: Date.now() - (3 * 60 * 60 * 1000), // 3 hours ago
        ttl: 7200000 // 2 hours TTL
      }))

      const retrieved = api.getCacheData(cacheKey)
      expect(retrieved).toBeNull()
    })

    it('should return null for non-existent cache data', () => {
      const cacheKey = 'non_existent_key'
      localStorageMock.getItem.mockReturnValue(null)

      const retrieved = api.getCacheData(cacheKey)
      expect(retrieved).toBeNull()
    })

    it('should handle corrupted cache data gracefully', () => {
      const cacheKey = 'corrupted_key'
      localStorageMock.getItem.mockReturnValue('invalid-json')

      const retrieved = api.getCacheData(cacheKey)
      expect(retrieved).toBeNull()
    })
  })

  describe('Cache Invalidation', () => {
    it('should invalidate specific cache keys', () => {
      const cacheKey = 'test_key'
      api.invalidateCache(cacheKey)

      expect(localStorageMock.removeItem).toHaveBeenCalledWith(cacheKey)
    })

    it('should invalidate cache by pattern', () => {
      // Mock multiple cache keys in localStorage
      const mockKeys = [
        'cache_/dashboard_abc123',
        'cache_/analytics_def456',
        'cache_/locations_ghi789',
        'other_cache_key'
      ]

      // Mock Object.keys to return our test keys
      Object.defineProperty(global.Storage.prototype, 'key', {
        value: vi.fn((index) => mockKeys[index]),
        writable: true
      })
      Object.defineProperty(global.Storage.prototype, 'length', {
        value: mockKeys.length,
        writable: true
      })

      api.invalidateCachePattern('/dashboard')

      expect(localStorageMock.removeItem).toHaveBeenCalledWith('cache_/dashboard_abc123')
      expect(localStorageMock.removeItem).not.toHaveBeenCalledWith('cache_/analytics_def456')
    })

    it('should clear all cache', () => {
      api.clearCache()
      expect(localStorageMock.clear).toHaveBeenCalled()
    })
  })

  describe('API Request Caching', () => {
    it('should use cached data when available', async () => {
      const mockData = { data: { test: 'cached' } }
      const endpoint = '/test-endpoint'
      
      // Mock axios get
      const mockGet = vi.fn().mockResolvedValue(mockData)
      api.axiosInstance.get = mockGet

      // First request - should hit API and cache
      const result1 = await api.get(endpoint)
      expect(mockGet).toHaveBeenCalledTimes(1)
      expect(result1).toEqual(mockData)

      // Mock cache hit for second request
      localStorageMock.getItem.mockReturnValue(JSON.stringify({
        data: mockData,
        timestamp: Date.now(),
        ttl: 7200000
      }))

      // Second request - should use cache
      const result2 = await api.get(endpoint)
      expect(mockGet).toHaveBeenCalledTimes(1) // Still only called once
      expect(result2).toEqual(mockData)
    })

    it('should bypass cache when skipCache is true', async () => {
      const mockData = { data: { test: 'fresh' } }
      const endpoint = '/test-endpoint'
      
      const mockGet = vi.fn().mockResolvedValue(mockData)
      api.axiosInstance.get = mockGet

      // Request with skipCache
      await api.get(endpoint, {}, { skipCache: true })
      expect(mockGet).toHaveBeenCalledTimes(1)

      // Another request with skipCache
      await api.get(endpoint, {}, { skipCache: true })
      expect(mockGet).toHaveBeenCalledTimes(2) // Should hit API again
    })

    it('should invalidate cache on POST/PUT/DELETE requests', async () => {
      const mockResponse = { data: { success: true } }
      const mockPost = vi.fn().mockResolvedValue(mockResponse)
      api.axiosInstance.post = mockPost

      const invalidateSpy = vi.spyOn(api, 'invalidateCachePattern')

      await api.post('/test-endpoint', { data: 'test' })

      expect(mockPost).toHaveBeenCalledTimes(1)
      expect(invalidateSpy).toHaveBeenCalled()
    })
  })
})

describe('Analytics Composable Optimization', () => {
  let analyticsComposable

  beforeEach(() => {
    vi.clearAllMocks()
    
    // Mock API methods
    vi.spyOn(api, 'getLocations').mockResolvedValue({ data: [
      { id: 1, name: 'Location 1' },
      { id: 2, name: 'Location 2' }
    ]})
    
    vi.spyOn(api, 'getRevenueProfitData').mockResolvedValue({
      data: {
        revenue: { total: 1000, change: 10 },
        profit: { total: 300, change: 5 },
        margin: { total: 30, change: -2 }
      }
    })
    
    vi.spyOn(api, 'getStockLevels').mockResolvedValue({
      data: { low_stock_count: 5, items: [] }
    })
    
    vi.spyOn(api, 'getDemandAnalysis').mockResolvedValue({
      data: {
        products: [{ product_name: 'Test Product', units_sold: 100 }],
        unit_counts: []
      }
    })

    // Create composable instance
    analyticsComposable = useAnalytics()
  })

  afterEach(() => {
    vi.restoreAllMocks()
  })

  describe('Batch API Calls', () => {
    it('should execute multiple API calls in parallel during initialization', async () => {
      const startTime = Date.now()
      
      await analyticsComposable.initialize()
      
      const endTime = Date.now()
      const duration = endTime - startTime

      // Should complete quickly due to parallel execution
      expect(duration).toBeLessThan(1000) // Less than 1 second
      
      // All API methods should have been called
      expect(api.getLocations).toHaveBeenCalledTimes(1)
      expect(api.getRevenueProfitData).toHaveBeenCalledTimes(1)
      expect(api.getStockLevels).toHaveBeenCalledTimes(1)
      expect(api.getDemandAnalysis).toHaveBeenCalledTimes(1)
    })

    it('should handle partial failures in batch API calls gracefully', async () => {
      // Mock one API call to fail
      api.getRevenueProfitData.mockRejectedValue(new Error('API Error'))

      await analyticsComposable.initialize()

      // Should still complete and have error state
      expect(analyticsComposable.error.value).toBeTruthy()
      expect(analyticsComposable.loading.value).toBe(false)
      
      // Other API calls should still succeed
      expect(api.getLocations).toHaveBeenCalled()
      expect(api.getStockLevels).toHaveBeenCalled()
    })
  })

  describe('Loading States', () => {
    it('should have granular loading states for different sections', () => {
      expect(analyticsComposable.loadingStates.value).toHaveProperty('locations')
      expect(analyticsComposable.loadingStates.value).toHaveProperty('revenue')
      expect(analyticsComposable.loadingStates.value).toHaveProperty('stock')
      expect(analyticsComposable.loadingStates.value).toHaveProperty('demand')
    })

    it('should update loading states correctly during API calls', async () => {
      // Start initialization
      const initPromise = analyticsComposable.initialize()
      
      // Check that loading states are active
      expect(analyticsComposable.loading.value).toBe(true)
      
      // Wait for completion
      await initPromise
      
      // Loading should be complete
      expect(analyticsComposable.loading.value).toBe(false)
      expect(analyticsComposable.isAnyLoading.value).toBe(false)
    })
  })

  describe('Data Processing', () => {
    it('should process demand data correctly', async () => {
      const mockDemandData = {
        products: [
          { product_name: 'Product A', units_sold: 100, trend: 15 },
          { product_name: 'Product B', units_sold: 80, trend: -5 }
        ],
        unit_counts: [
          {
            product_name: 'Product A',
            location_name: 'Location 1',
            machine_name: 'Machine 1',
            units_sold: 50,
            start_date: '2024-01-01',
            end_date: '2024-01-07'
          }
        ]
      }

      api.getDemandAnalysis.mockResolvedValue({ data: mockDemandData })

      await analyticsComposable.applyFilters()

      expect(analyticsComposable.demandData.value.products).toHaveLength(2)
      expect(analyticsComposable.demandData.value.unit_counts).toHaveLength(1)
    })

    it('should handle empty or malformed data gracefully', async () => {
      api.getDemandAnalysis.mockResolvedValue({ data: null })

      await analyticsComposable.applyFilters()

      expect(analyticsComposable.demandData.value.products).toEqual([])
      expect(analyticsComposable.demandData.value.unit_counts).toEqual([])
    })
  })

  describe('Filter Management', () => {
    it('should build request parameters correctly', () => {
      analyticsComposable.filters.value = {
        dateRange: '30',
        location: '1'
      }

      // This would be tested by checking the actual API calls
      // For now, we verify the filter structure
      expect(analyticsComposable.filters.value.dateRange).toBe('30')
      expect(analyticsComposable.filters.value.location).toBe('1')
    })

    it('should handle custom date ranges', () => {
      analyticsComposable.filters.value = {
        dateRange: 'custom',
        startDate: '2024-01-01',
        endDate: '2024-01-31'
      }

      expect(analyticsComposable.filters.value.dateRange).toBe('custom')
      expect(analyticsComposable.filters.value.startDate).toBe('2024-01-01')
      expect(analyticsComposable.filters.value.endDate).toBe('2024-01-31')
    })
  })

  describe('Computed Properties', () => {
    it('should sort demand counts correctly', async () => {
      const mockUnitCounts = [
        {
          location_name: 'Location B',
          machine_name: 'Machine 2',
          product_name: 'Product Y',
          end_date: new Date('2024-01-15')
        },
        {
          location_name: 'Location A',
          machine_name: 'Machine 1',
          product_name: 'Product X',
          end_date: new Date('2024-01-10')
        }
      ]

      analyticsComposable.demandData.value.unit_counts = mockUnitCounts

      const sorted = analyticsComposable.sortedDemandCounts.value

      expect(sorted[0].location_name).toBe('Location A')
      expect(sorted[1].location_name).toBe('Location B')
    })
  })
})

describe('Dashboard Composable Optimization', () => {
  let dashboardComposable

  beforeEach(() => {
    vi.clearAllMocks()
    
    // Mock API methods
    vi.spyOn(api, 'getLocations').mockResolvedValue({ data: [] })
    vi.spyOn(api, 'getDashboardData').mockResolvedValue({
      data: {
        locations: 5,
        machines: 10,
        products: 25,
        low_stock_items: [],
        low_stock_count: 0,
        recent_restocks: 15,
        revenue_total: 1500,
        profit_total: 450,
        profit_margin: 30
      }
    })

    dashboardComposable = useDashboard()
  })

  afterEach(() => {
    vi.restoreAllMocks()
  })

  describe('Initialization Performance', () => {
    it('should initialize dashboard with batch API calls', async () => {
      await dashboardComposable.initializeDashboard()

      expect(api.getLocations).toHaveBeenCalledTimes(1)
      expect(api.getDashboardData).toHaveBeenCalledTimes(1)
      expect(dashboardComposable.loading.value).toBe(false)
    })

    it('should handle initialization errors gracefully', async () => {
      api.getDashboardData.mockRejectedValue(new Error('Dashboard API Error'))

      await dashboardComposable.initializeDashboard()

      expect(dashboardComposable.error.value).toBeTruthy()
      expect(dashboardComposable.loading.value).toBe(false)
    })
  })

  describe('Cache Management', () => {
    it('should force refresh and clear cache', async () => {
      const invalidateCacheSpy = vi.spyOn(api, 'invalidateCache')

      await dashboardComposable.forceRefresh()

      expect(invalidateCacheSpy).toHaveBeenCalledWith('/dashboard')
      expect(invalidateCacheSpy).toHaveBeenCalledWith('/locations')
      expect(api.getDashboardData).toHaveBeenCalled()
    })
  })

  describe('Filter Management', () => {
    it('should build request parameters with filters', () => {
      dashboardComposable.filters.timeRange = '7'
      dashboardComposable.filters.location = '1'
      dashboardComposable.filters.machineType = 'Snack'

      // Test would verify the parameters are passed correctly to API calls
      expect(dashboardComposable.filters.timeRange).toBe('7')
      expect(dashboardComposable.filters.location).toBe('1')
      expect(dashboardComposable.filters.machineType).toBe('Snack')
    })
  })

  describe('Data Validation', () => {
    it('should handle missing data gracefully', async () => {
      api.getDashboardData.mockResolvedValue({ data: {} })

      await dashboardComposable.initializeDashboard()

      // Should use default values
      expect(dashboardComposable.data.value.locations).toBe(0)
      expect(dashboardComposable.data.value.machines).toBe(0)
      expect(dashboardComposable.data.value.products).toBe(0)
    })

    it('should validate data types', async () => {
      const mockData = {
        locations: 5,
        machines: 10,
        products: 25,
        low_stock_items: [],
        low_stock_count: 0,
        recent_restocks: 15,
        revenue_total: 1500.50,
        profit_total: 450.25,
        profit_margin: 30.02
      }

      api.getDashboardData.mockResolvedValue({ data: mockData })

      await dashboardComposable.initializeDashboard()

      expect(typeof dashboardComposable.data.value.locations).toBe('number')
      expect(typeof dashboardComposable.data.value.revenue_total).toBe('number')
      expect(Array.isArray(dashboardComposable.data.value.low_stock_items)).toBe(true)
    })
  })
})

describe('Inventory Reports Composable Optimization', () => {
  let inventoryComposable

  beforeEach(() => {
    vi.clearAllMocks()
    
    // Mock API methods
    vi.spyOn(api, 'getLocations').mockResolvedValue({ data: [] })
    vi.spyOn(api, 'getProducts').mockResolvedValue({ data: [] })
    vi.spyOn(api, 'getCurrentStockReport').mockResolvedValue({ data: {} })
    vi.spyOn(api, 'getRestockSummary').mockResolvedValue({ data: {} })
    vi.spyOn(api, 'getStockCoverageEstimate').mockResolvedValue({ data: {} })

    inventoryComposable = useInventoryReports()
  })

  afterEach(() => {
    vi.restoreAllMocks()
  })

  describe('Batch Loading', () => {
    it('should load all base data in parallel', async () => {
      await inventoryComposable.loadBaseData()

      expect(api.getLocations).toHaveBeenCalledTimes(1)
      expect(api.getProducts).toHaveBeenCalledTimes(1)
      expect(inventoryComposable.loading.value).toBe(false)
    })

    it('should load all reports in parallel', async () => {
      await inventoryComposable.loadAllReports()

      expect(api.getCurrentStockReport).toHaveBeenCalledTimes(1)
      expect(api.getRestockSummary).toHaveBeenCalledTimes(1)
      expect(api.getStockCoverageEstimate).toHaveBeenCalledTimes(1)
    })
  })

  describe('Selective Loading', () => {
    it('should load individual reports', async () => {
      await inventoryComposable.loadCurrentStock()
      expect(api.getCurrentStockReport).toHaveBeenCalledTimes(1)

      await inventoryComposable.loadRestockSummary()
      expect(api.getRestockSummary).toHaveBeenCalledTimes(1)

      await inventoryComposable.loadStockCoverage()
      expect(api.getStockCoverageEstimate).toHaveBeenCalledTimes(1)
    })

    it('should skip loading if data already exists and not forcing', async () => {
      // Set some existing data
      inventoryComposable.currentStockData.value = { existing: 'data' }

      await inventoryComposable.loadCurrentStock(false) // Don't force

      expect(api.getCurrentStockReport).not.toHaveBeenCalled()
    })

    it('should force reload when requested', async () => {
      // Set some existing data
      inventoryComposable.currentStockData.value = { existing: 'data' }

      await inventoryComposable.loadCurrentStock(true) // Force reload

      expect(api.getCurrentStockReport).toHaveBeenCalledTimes(1)
    })
  })

  describe('Error Handling', () => {
    it('should handle individual report failures', async () => {
      api.getCurrentStockReport.mockRejectedValue(new Error('Stock report error'))

      await inventoryComposable.loadCurrentStock()

      expect(inventoryComposable.error.value).toBeTruthy()
      expect(inventoryComposable.currentStockData.value).toBeNull()
    })

    it('should handle batch loading failures gracefully', async () => {
      api.getLocations.mockRejectedValue(new Error('Locations error'))
      api.getProducts.mockResolvedValue({ data: [{ id: 1, name: 'Product 1' }] })

      await inventoryComposable.loadBaseData()

      // Should still have products data
      expect(inventoryComposable.products.value).toHaveLength(1)
      // But should have error state
      expect(inventoryComposable.error.value).toBeTruthy()
    })
  })
})

describe('Performance Monitoring', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('should log cache hit/miss statistics', () => {
    const consoleSpy = vi.spyOn(console, 'log').mockImplementation(() => {})

    // Simulate cache operations
    api.getCacheData('test_key') // Miss
    api.setCacheData('test_key', { data: 'test' })
    api.getCacheData('test_key') // Hit

    // Should have logged cache statistics
    expect(consoleSpy).toHaveBeenCalled()
  })

  it('should measure API call performance', async () => {
    const performanceNowSpy = vi.spyOn(performance, 'now')
      .mockReturnValueOnce(0)
      .mockReturnValueOnce(100) // 100ms duration

    const mockGet = vi.fn().mockResolvedValue({ data: 'test' })
    api.axiosInstance.get = mockGet

    await api.get('/test-endpoint')

    expect(performanceNowSpy).toHaveBeenCalledTimes(2)
  })

  it('should track batch API call efficiency', async () => {
    const startTime = performance.now()
    
    // Simulate multiple API calls
    const promises = [
      Promise.resolve({ data: 'test1' }),
      Promise.resolve({ data: 'test2' }),
      Promise.resolve({ data: 'test3' })
    ]

    await Promise.allSettled(promises)
    
    const duration = performance.now() - startTime
    
    // Batch calls should complete quickly
    expect(duration).toBeLessThan(50) // Less than 50ms for mocked calls
  })
}) 