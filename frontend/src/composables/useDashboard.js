import { ref, reactive, computed } from 'vue'
import { api } from '../services/api'

export function useDashboard() {
  const loading = ref(true)
  const error = ref(null)
  const locations = ref([])
  const machines = ref([])
  const products = ref([])
  
  // Individual loading states for better UX
  const loadingStates = ref({
    locations: false,
    machines: false,
    products: false,
    analytics: false
  })
  
  // Enhanced analytics data structure
  const data = ref({
    // Summary metrics
    summary: {
      total_demand_units: 0,
      total_revenue: 0,
      total_profit: 0,
      avg_daily_demand: 0,
      overall_profit_margin: 0,
      total_restocks: 0,
      unique_products: 0,
      unique_machines: 0,
      unique_locations: 0
    },
    
    // Performance data
    products: {
      top_performers: [],
      all: []
    },
    machines: {
      top_performers: [],
      all: []
    },
    locations: {
      performance: []
    },
    
    // Trends and insights
    trends: {
      time_series: [],
      daily_summary: []
    },
    insights: [],
    
    // Legacy compatibility
    locations_count: 0,
    machines_count: 0,
    products_count: 0,
    low_stock_items: [],
    low_stock_count: 0,
    recent_restocks: 0,
    revenue_total: 0,
    profit_total: 0,
    profit_margin: 0
  })

  const filters = reactive({
    timeRange: '30',
    location: '',
    machine: '',
    product: '',
    startDate: '',
    endDate: ''
  })

  // Computed properties
  const isAnyLoading = computed(() => {
    return Object.values(loadingStates.value).some(state => state) || loading.value
  })

  const hasData = computed(() => {
    return data.value.locations_count > 0 || data.value.machines_count > 0 || data.value.products_count > 0
  })

  // Build request parameters for advanced analytics
  const buildRequestParams = () => {
    const params = {}
    
    // Time range handling
    if (filters.startDate && filters.endDate) {
      params.start_date = filters.startDate
      params.end_date = filters.endDate
    } else if (filters.timeRange) {
      params.days = filters.timeRange
    }
    
    // Additional filters
    if (filters.location) params.location = filters.location
    if (filters.machine) params.machine = filters.machine
    if (filters.product) params.product = filters.product
    
    return params
  }

  // Fetch locations for the dropdown
  const fetchLocations = async () => {
    if (locations.value.length > 0) return // Already loaded
    
    loadingStates.value.locations = true
    try {
      const response = await api.getLocations()
      locations.value = response.data.results || response.data
    } catch (err) {
      console.error('Error fetching locations:', err)
      // Don't set global error for locations as dashboard can work without them
    } finally {
      loadingStates.value.locations = false
    }
  }

  // Fetch machines for the dropdown
  const fetchMachines = async () => {
    if (machines.value.length > 0) return // Already loaded
    
    loadingStates.value.machines = true
    try {
      const response = await api.getMachines()
      machines.value = response.data.results || response.data
    } catch (err) {
      console.error('Error fetching machines:', err)
    } finally {
      loadingStates.value.machines = false
    }
  }

  // Fetch products for the dropdown
  const fetchProducts = async () => {
    if (products.value.length > 0) return // Already loaded
    
    loadingStates.value.products = true
    try {
      const response = await api.getProducts()
      products.value = response.data.results || response.data
    } catch (err) {
      console.error('Error fetching products:', err)
    } finally {
      loadingStates.value.products = false
    }
  }

  // Fetch advanced analytics data
  const fetchAdvancedAnalyticsData = async (params) => {
    loadingStates.value.analytics = true
    try {
      // Use the existing API service which handles authentication correctly
      const response = await api.getAdvancedAnalytics(params)
      const analyticsData = response.data
      
      // Update the enhanced data structure
      data.value = {
        ...data.value,
        summary: analyticsData.summary || data.value.summary,
        products: analyticsData.products || data.value.products,
        machines: analyticsData.machines || data.value.machines,
        locations: analyticsData.locations || data.value.locations,
        trends: analyticsData.trends || data.value.trends,
        insights: analyticsData.insights || [],
        
        // Legacy compatibility - map from new structure (using different property names to avoid conflicts)
        locations_count: analyticsData.summary?.unique_locations || 0,
        machines_count: analyticsData.summary?.unique_machines || 0,
        products_count: analyticsData.summary?.unique_products || 0,
        low_stock_items: [], // This would come from a different endpoint now
        low_stock_count: 0,
        recent_restocks: analyticsData.summary?.total_restocks || 0,
        revenue_total: analyticsData.summary?.total_revenue || 0,
        profit_total: analyticsData.summary?.total_profit || 0,
        profit_margin: analyticsData.summary?.overall_profit_margin || 0
      }
      
    } catch (err) {
      console.error('Error fetching advanced analytics data:', err)
      throw new Error('Failed to load analytics data')
    } finally {
      loadingStates.value.analytics = false
    }
  }

  // Legacy dashboard data fetch (for backward compatibility)
  const fetchLegacyDashboardData = async (params) => {
    try {
      const response = await api.getDashboardData(params)
      
      // Update only legacy fields that aren't covered by analytics
      const legacyUpdate = {
        low_stock_items: response.data.low_stock_items || [],
        low_stock_count: response.data.low_stock_count || 0,
      }
      
      data.value = { ...data.value, ...legacyUpdate }
    } catch (err) {
      console.error('Error fetching legacy dashboard data:', err)
      // Don't throw here, analytics data is more important
    }
  }

  // Apply filters and refresh dashboard data
  const applyFilters = async () => {
    loading.value = true
    error.value = null
    
    try {
      const params = buildRequestParams()
      await Promise.all([
        fetchAdvancedAnalyticsData(params),
        fetchLegacyDashboardData(params) // For low stock items
      ])
    } catch (err) {
      console.error('Error applying filters:', err)
      error.value = 'Failed to load analytics data'
    } finally {
      loading.value = false
    }
  }

  // Initialize dashboard data with optimized loading
  const initializeDashboard = async () => {
    loading.value = true
    error.value = null
    
    try {
      // Use batch API calls for better performance
      const apiCalls = [
        fetchLocations(),
        fetchMachines(),
        fetchProducts(),
        fetchAdvancedAnalyticsData(buildRequestParams()),
        fetchLegacyDashboardData(buildRequestParams())
      ]
      
      // Execute API calls in parallel and handle individual errors
      const results = await Promise.allSettled(apiCalls)
      
      // Check if critical API calls failed
      const failedCalls = results.filter(result => result.status === 'rejected')
      if (failedCalls.length > 0) {
        console.warn(`${failedCalls.length} dashboard API calls failed:`, failedCalls.map(f => f.reason?.message))
        
        // Only show error if analytics data failed to load
        const analyticsFailed = results[3].status === 'rejected'
        if (analyticsFailed) {
          error.value = 'Failed to load analytics data'
        }
      }
    } catch (err) {
      console.error('Error initializing dashboard:', err)
      error.value = 'Failed to initialize dashboard'
    } finally {
      loading.value = false
    }
  }

  // Refresh specific section
  const refreshSection = async (section) => {
    try {
      switch (section) {
        case 'locations':
          await fetchLocations()
          break
        case 'machines':
          await fetchMachines()
          break
        case 'products':
          await fetchProducts()
          break
        case 'analytics':
          await fetchAdvancedAnalyticsData(buildRequestParams())
          break
        case 'dashboard':
        case 'legacy':
          await fetchLegacyDashboardData(buildRequestParams())
          break
        default:
          await applyFilters()
      }
    } catch (err) {
      console.error(`Error refreshing ${section}:`, err)
      error.value = `Failed to refresh ${section} data`
    }
  }

  // Force refresh all data (bypass cache)
  const forceRefresh = async () => {
    loading.value = true
    error.value = null
    
    try {
      // Clear cache for dashboard-related data
      if (api.invalidateCache) {
        api.invalidateCache('/dashboard')
        api.invalidateCache('/locations')
        api.invalidateCache('/analytics/advanced-demand')
      }
      
      // Reset all data to force reload
      locations.value = []
      machines.value = []
      products.value = []
      
      await initializeDashboard()
    } catch (err) {
      console.error('Error force refreshing dashboard:', err)
      error.value = 'Failed to refresh dashboard data'
    } finally {
      loading.value = false
    }
  }

  // Export analytics data as CSV via dedicated export endpoint
  const exportAnalyticsData = async () => {
    try {
      const params = { ...buildRequestParams() }

      const axiosResponse = await api.apiClient.get('/analytics/advanced-demand/export/', {
        params,
        responseType: 'blob',
        headers: { Accept: 'text/csv,application/octet-stream,*/*' },
      })

      const blob = axiosResponse.data
      if (blob instanceof Blob) {
        const downloadUrl = window.URL.createObjectURL(blob)
        const link = document.createElement('a')
        link.href = downloadUrl
        link.download = `analytics_report_${new Date().toISOString().split('T')[0]}.csv`
        document.body.appendChild(link)
        link.click()
        document.body.removeChild(link)
        window.URL.revokeObjectURL(downloadUrl)
      } else {
        console.error('Expected blob, got:', typeof blob, blob)
        throw new Error('Server did not return CSV data as expected')
      }

      return true
    } catch (err) {
      console.error('Error exporting data:', err)
      error.value = 'Failed to export data'
      return false
    }
  }

  // Get insights with priority filtering
  const getPriorityInsights = (priority = null) => {
    if (!data.value.insights) return []
    
    if (priority) {
      return data.value.insights.filter(insight => insight.priority === priority)
    }
    
    return data.value.insights
  }

  // Get top performing items by category
  const getTopPerformers = (category, limit = 5) => {
    switch (category) {
      case 'products':
        return data.value.products?.top_performers?.slice(0, limit) || []
      case 'machines':
        return data.value.machines?.top_performers?.slice(0, limit) || []
      case 'locations':
        return data.value.locations?.performance?.slice(0, limit) || []
      default:
        return []
    }
  }

  // Calculate period comparison
  const calculatePeriodComparison = (currentValue, comparisonField = null) => {
    // This would be enhanced with historical data comparison
    // For now, return a placeholder structure
    return {
      current: currentValue,
      previous: null,
      change: null,
      changePercent: null,
      trend: 'stable'
    }
  }

  // Utility function for stock level classes
  const getStockLevelClass = (quantity) => {
    if (quantity <= 0) return 'bg-red-100 text-red-800'
    if (quantity <= 3) return 'bg-yellow-100 text-yellow-800'
    return 'bg-blue-100 text-blue-800'
  }

  // Utility function for performance trend classes
  const getTrendClass = (trend) => {
    switch (trend) {
      case 'improving':
        return 'text-green-600'
      case 'declining':
        return 'text-red-600'
      default:
        return 'text-gray-600'
    }
  }

  // Utility function for trend icons
  const getTrendIcon = (trend) => {
    switch (trend) {
      case 'improving':
        return '📈'
      case 'declining':
        return '📉'
      default:
        return '➡️'
    }
  }

  return {
    // State
    loading,
    error,
    locations,
    machines,
    products,
    data,
    filters,
    loadingStates,
    
    // Computed
    isAnyLoading,
    hasData,
    
    // Core methods
    applyFilters,
    initializeDashboard,
    refreshSection,
    forceRefresh,
    
    // Data fetching methods
    fetchLocations,
    fetchMachines,
    fetchProducts,
    fetchAdvancedAnalyticsData,
    
    // Analytics methods
    exportAnalyticsData,
    getPriorityInsights,
    getTopPerformers,
    calculatePeriodComparison,
    
    // Utility methods
    getStockLevelClass,
    getTrendClass,
    getTrendIcon
  }
} 
