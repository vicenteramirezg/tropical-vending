import { ref, computed } from 'vue'
import { api } from '../services/api'
import { getCurrentDateLocal, formatDateShort } from '../utils/dateUtils'

export function useAnalytics() {
  // Loading and error states
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
    revenue: false,
    stock: false,
    demand: false
  })

  // Filter states
  const filters = ref({
    dateRange: '30',
    startDate: '',
    endDate: '',
    location: '',
    machine: '',
    product: ''
  })

  // Data states
  const revenueProfitData = ref({
    revenue: { total: 0, change: 0 },
    profit: { total: 0, change: 0 },
    margin: { total: 0, change: 0 }
  })

  const stockLevelData = ref({
    low_stock_count: 0,
    items: []
  })

  const demandData = ref({
    unit_counts: [],
    products: []
  })

  // Computed properties
  const sortedDemandCounts = computed(() => {
    if (!demandData.value.unit_counts) return []
    
    return [...demandData.value.unit_counts]
      .sort((a, b) => {
        // Sort by location, then machine, then product, then date
        if (a.location_name !== b.location_name) return a.location_name.localeCompare(b.location_name)
        if (a.machine_name !== b.machine_name) return a.machine_name.localeCompare(b.machine_name)
        if (a.product_name !== b.product_name) return a.product_name.localeCompare(b.product_name)
        return new Date(b.end_date) - new Date(a.end_date) // Most recent first
      })
  })

  const isAnyLoading = computed(() => {
    return Object.values(loadingStates.value).some(state => state) || loading.value
  })

  // Helper functions
  const getStockLevelClass = (quantity) => {
    if (quantity <= 0) return 'bg-red-100 text-red-800'
    if (quantity <= 3) return 'bg-yellow-100 text-yellow-800'
    return 'bg-blue-100 text-blue-800'
  }

  const getTrendClass = (trend) => {
    if (trend === undefined || trend === null) return 'bg-gray-100 text-gray-800'
    if (trend > 10) return 'bg-green-100 text-green-800'
    if (trend < -10) return 'bg-red-100 text-red-800'
    return 'bg-gray-100 text-gray-800'
  }

  const formatTrend = (trend) => {
    if (trend === undefined || trend === null) return '+0.0%'
    return `${trend >= 0 ? '+' : ''}${trend.toFixed(1)}%`
  }

  const formatDailyDemand = (demand) => {
    if (demand === undefined || demand === null) return '0.0/day'
    return demand.toFixed(1) + '/day'
  }

  // Build request parameters
  const buildRequestParams = () => {
    const params = {}
    
    if (filters.value.dateRange !== 'custom') {
      params.days = filters.value.dateRange
    } else {
      params.start_date = filters.value.startDate
      params.end_date = filters.value.endDate
    }
    
    if (filters.value.location) {
      params.location = filters.value.location
    }
    
    if (filters.value.machine) {
      params.machine = filters.value.machine
    }
    
    if (filters.value.product) {
      params.product = filters.value.product
    }
    
    return params
  }

  // Data fetching functions
  const fetchLocations = async () => {
    if (locations.value.length > 0) return // Already loaded
    
    loadingStates.value.locations = true
    try {
      const response = await api.getLocations()
      // Handle paginated response - extract results array
      locations.value = response.data.results || response.data
    } catch (err) {
      console.error('Error fetching locations:', err)
      // Don't set global error for locations as it's not critical
    } finally {
      loadingStates.value.locations = false
    }
  }

  const fetchMachines = async (locationId) => {
    loadingStates.value.machines = true
    try {
      if (!locationId) {
        machines.value = []
        return
      }
      
      const response = await api.getMachines({ location: locationId })
      // Handle paginated response - extract results array
      machines.value = response.data.results || response.data
    } catch (err) {
      console.error('Error fetching machines:', err)
      machines.value = []
    } finally {
      loadingStates.value.machines = false
    }
  }

  const fetchProducts = async (machineId) => {
    loadingStates.value.products = true
    try {
      if (!machineId) {
        products.value = []
        return
      }
      
      // Fetch machine items (products for specific machine)
      const response = await api.getMachineItems({ machine: machineId })
      // Handle paginated response - extract results array
      const machineItems = response.data.results || response.data
      
      // Transform machine items to products list with unique products
      const uniqueProducts = new Map()
      machineItems.forEach(item => {
        if (!uniqueProducts.has(item.product)) {
          uniqueProducts.set(item.product, {
            id: item.product,
            name: item.product_name
          })
        }
      })
      
      products.value = Array.from(uniqueProducts.values())
    } catch (err) {
      console.error('Error fetching products:', err)
      products.value = []
    } finally {
      loadingStates.value.products = false
    }
  }

  const fetchRevenueProfitData = async (params) => {
    loadingStates.value.revenue = true
    try {
      const response = await api.getRevenueProfitData(params)
      
      if (!response.data) {
        revenueProfitData.value = {
          revenue: { total: 0, change: 0 },
          profit: { total: 0, change: 0 },
          margin: { total: 0, change: 0 }
        }
        return
      }
      
      revenueProfitData.value = {
        revenue: {
          total: response.data.revenue?.total || 0,
          change: response.data.revenue?.change || 0
        },
        profit: {
          total: response.data.profit?.total || 0,
          change: response.data.profit?.change || 0
        },
        margin: {
          total: response.data.margin?.total || 0,
          change: response.data.margin?.change || 0
        }
      }
    } catch (err) {
      console.error('Error fetching revenue/profit data:', err)
      revenueProfitData.value = {
        revenue: { total: 0, change: 0 },
        profit: { total: 0, change: 0 },
        margin: { total: 0, change: 0 }
      }
      throw new Error('Failed to load revenue and profit data')
    } finally {
      loadingStates.value.revenue = false
    }
  }

  const fetchStockLevelData = async (params) => {
    loadingStates.value.stock = true
    try {
      const stockParams = { location: params.location }
      const response = await api.getStockLevels(stockParams)
      
      if (!response.data) {
        stockLevelData.value = {
          low_stock_count: 0,
          items: []
        }
        return
      }
      
      stockLevelData.value = {
        low_stock_count: response.data.low_stock_count || 0,
        items: response.data.items || []
      }
    } catch (err) {
      console.error('Error fetching stock level data:', err)
      stockLevelData.value = {
        low_stock_count: 0,
        items: []
      }
      throw new Error('Failed to load stock level data')
    } finally {
      loadingStates.value.stock = false
    }
  }

  const fetchDemandData = async (params) => {
    loadingStates.value.demand = true
    try {
      const response = await api.getDemandAnalysis(params)
      console.log('Demand analysis data:', response.data)
      
      if (!response.data) {
        demandData.value = {
          products: [],
          unit_counts: []
        }
        return
      }
      
      // Handle both old and new response formats
      if (Array.isArray(response.data)) {
        // Old format - just products array
        demandData.value = {
          products: response.data || [],
          unit_counts: []
        }
      } else {
        // New format with both unit_counts and products
        demandData.value = {
          products: response.data.products || [],
          unit_counts: response.data.unit_counts || []
        }
        
        // Convert date strings to Date objects for better sorting
        if (demandData.value.unit_counts && demandData.value.unit_counts.length > 0) {
          demandData.value.unit_counts.forEach(count => {
            if (count.start_date) count.start_date = new Date(count.start_date)
            if (count.end_date) count.end_date = new Date(count.end_date)
          })
        }
      }
    } catch (err) {
      console.error('Error fetching demand analysis data:', err)
      demandData.value = {
        products: [],
        unit_counts: []
      }
      throw new Error('Failed to load demand analysis data')
    } finally {
      loadingStates.value.demand = false
    }
  }

  // Apply filters and refresh data using batch API calls
  const applyFilters = async () => {
    loading.value = true
    error.value = null
    
    try {
      // Set default date range if custom is selected but dates are not
      if (filters.value.dateRange === 'custom' && (!filters.value.startDate || !filters.value.endDate)) {
        const today = getCurrentDateLocal()
        const thirtyDaysAgo = new Date()
        thirtyDaysAgo.setDate(thirtyDaysAgo.getDate() - 30)
        const thirtyDaysAgoFormatted = thirtyDaysAgo.toLocaleDateString('en-CA', {timeZone: 'America/New_York'}) // YYYY-MM-DD format
        
        if (!filters.value.endDate) {
          filters.value.endDate = today
        }
        
        if (!filters.value.startDate) {
          filters.value.startDate = thirtyDaysAgoFormatted
        }
      }
      
      const params = buildRequestParams()
      
      // Use batch API calls for better performance
      const apiCalls = [
        fetchRevenueProfitData(params),
        fetchStockLevelData(params),
        fetchDemandData(params)
      ]
      
      // Execute all API calls in parallel and handle individual errors
      const results = await Promise.allSettled(apiCalls)
      
      // Check if any critical API calls failed
      const failedCalls = results.filter(result => result.status === 'rejected')
      if (failedCalls.length > 0) {
        console.warn(`${failedCalls.length} API calls failed:`, failedCalls.map(f => f.reason.message))
        // Set a general error but don't prevent the page from working
        error.value = `Some data could not be loaded. ${failedCalls.length} of ${apiCalls.length} requests failed.`
      }
      
    } catch (err) {
      console.error('Error refreshing data:', err)
      error.value = 'Failed to refresh analytics data'
    } finally {
      loading.value = false
    }
  }

  // Initialize data with optimized loading
  const initialize = async () => {
    loading.value = true
    error.value = null
    
    try {
      // Load locations first (they're needed for filters)
      await fetchLocations()
      
      // Then load analytics data
      await applyFilters()
    } catch (err) {
      console.error('Error initializing analytics:', err)
      error.value = 'Failed to load analytics data'
    } finally {
      loading.value = false
    }
  }

  // Refresh specific data section
  const refreshSection = async (section) => {
    const params = buildRequestParams()
    
    try {
      switch (section) {
        case 'revenue':
          await fetchRevenueProfitData(params)
          break
        case 'stock':
          await fetchStockLevelData(params)
          break
        case 'demand':
          await fetchDemandData(params)
          break
        default:
          await applyFilters()
      }
    } catch (err) {
      console.error(`Error refreshing ${section}:`, err)
      error.value = `Failed to refresh ${section} data`
    }
  }

  return {
    // State
    loading,
    error,
    locations,
    machines,
    products,
    filters,
    revenueProfitData,
    stockLevelData,
    demandData,
    loadingStates,
    
    // Computed
    sortedDemandCounts,
    isAnyLoading,
    
    // Helper functions
    getStockLevelClass,
    getTrendClass,
    formatTrend,
    formatDailyDemand,
    formatDateShort,
    
    // Actions
    applyFilters,
    initialize,
    refreshSection,
    fetchMachines,
    fetchProducts
  }
} 