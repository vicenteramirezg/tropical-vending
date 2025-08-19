import { ref, reactive, computed } from 'vue'
import { api } from '../services/api'

export function useDashboard() {
  const loading = ref(true)
  const error = ref(null)
  const locations = ref([])
  
  // Individual loading states for better UX
  const loadingStates = ref({
    locations: false,
    dashboard: false
  })
  
  const data = ref({
    locations: 0,
    machines: 0,
    products: 0,
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
    machineType: ''
  })

  // Computed properties
  const isAnyLoading = computed(() => {
    return Object.values(loadingStates.value).some(state => state) || loading.value
  })

  const hasData = computed(() => {
    return data.value.locations > 0 || data.value.machines > 0 || data.value.products > 0
  })

  // Build request parameters
  const buildRequestParams = () => {
    const params = {
      days: filters.timeRange
    }
    
    if (filters.location) {
      params.location = filters.location
    }
    
    if (filters.machineType) {
      params.machine_type = filters.machineType
    }
    
    return params
  }

  // Fetch locations for the dropdown
  const fetchLocations = async () => {
    if (locations.value.length > 0) return // Already loaded
    
    loadingStates.value.locations = true
    try {
      const response = await api.getLocations()
      // Handle paginated response - extract results array
      locations.value = response.data.results || response.data
    } catch (err) {
      console.error('Error fetching locations:', err)
      // Don't set global error for locations as dashboard can work without them
    } finally {
      loadingStates.value.locations = false
    }
  }

  // Fetch dashboard data
  const fetchDashboardData = async (params) => {
    loadingStates.value.dashboard = true
    try {
      const response = await api.getDashboardData(params)
      data.value = {
        locations: response.data.locations || 0,
        machines: response.data.machines || 0,
        products: response.data.products || 0,
        low_stock_items: response.data.low_stock_items || [],
        low_stock_count: response.data.low_stock_count || 0,
        recent_restocks: response.data.recent_restocks || 0,
        revenue_total: response.data.revenue_total || 0,
        profit_total: response.data.profit_total || 0,
        profit_margin: response.data.profit_margin || 0
      }
    } catch (err) {
      console.error('Error fetching dashboard data:', err)
      // Reset to default values on error
      data.value = {
        locations: 0,
        machines: 0,
        products: 0,
        low_stock_items: [],
        low_stock_count: 0,
        recent_restocks: 0,
        revenue_total: 0,
        profit_total: 0,
        profit_margin: 0
      }
      throw new Error('Failed to load dashboard data')
    } finally {
      loadingStates.value.dashboard = false
    }
  }

  // Apply filters and refresh dashboard data
  const applyFilters = async () => {
    loading.value = true
    error.value = null
    
    try {
      const params = buildRequestParams()
      await fetchDashboardData(params)
    } catch (err) {
      console.error('Error applying filters:', err)
      error.value = 'Failed to load dashboard data'
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
        fetchDashboardData(buildRequestParams())
      ]
      
      // Execute API calls in parallel and handle individual errors
      const results = await Promise.allSettled(apiCalls)
      
      // Check if critical API calls failed
      const failedCalls = results.filter(result => result.status === 'rejected')
      if (failedCalls.length > 0) {
        console.warn(`${failedCalls.length} dashboard API calls failed:`, failedCalls.map(f => f.reason?.message))
        
        // Only show error if dashboard data failed to load
        const dashboardFailed = results[1].status === 'rejected'
        if (dashboardFailed) {
          error.value = 'Failed to load dashboard data'
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
        case 'dashboard':
          await fetchDashboardData(buildRequestParams())
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
      api.invalidateCache('/dashboard')
      api.invalidateCache('/locations')
      
      // Reset locations to force reload
      locations.value = []
      
      await initializeDashboard()
    } catch (err) {
      console.error('Error force refreshing dashboard:', err)
      error.value = 'Failed to refresh dashboard data'
    } finally {
      loading.value = false
    }
  }

  // Utility function for stock level classes
  const getStockLevelClass = (quantity) => {
    if (quantity <= 0) return 'bg-red-100 text-red-800'
    if (quantity <= 3) return 'bg-yellow-100 text-yellow-800'
    return 'bg-blue-100 text-blue-800'
  }

  return {
    // State
    loading,
    error,
    locations,
    data,
    filters,
    loadingStates,
    
    // Computed
    isAnyLoading,
    hasData,
    
    // Methods
    fetchLocations,
    applyFilters,
    initializeDashboard,
    refreshSection,
    forceRefresh,
    getStockLevelClass
  }
} 