import { ref, reactive, computed } from 'vue'
import { api } from '../services/api'

export function useInventoryReports() {
  // Loading states
  const loading = ref(false)
  const error = ref('')
  
  // Individual loading states for better UX
  const loadingStates = ref({
    locations: false,
    products: false,
    currentStock: false,
    restockSummary: false,
    stockCoverage: false
  })

  // Data
  const locations = ref([])
  const products = ref([])
  const currentStockData = ref(null)
  const restockSummaryData = ref(null)
  const stockCoverageData = ref(null)

  // Filters
  const filters = reactive({
    location: '',
    product: '',
    machine: '',
    startDate: '',
    endDate: '',
    days: '7',
    analysisDays: '30'
  })

  // Computed properties
  const isAnyLoading = computed(() => {
    return Object.values(loadingStates.value).some(state => state) || loading.value
  })

  const hasFilters = computed(() => {
    return filters.location || filters.product || filters.machine
  })

  // Build parameters for different report types
  const buildCurrentStockParams = () => {
    const params = {}
    if (filters.location) params.location = filters.location
    if (filters.product) params.product = filters.product
    if (filters.machine) params.machine = filters.machine
    return params
  }

  const buildRestockSummaryParams = () => {
    const params = {}
    if (filters.location) params.location = filters.location
    if (filters.product) params.product = filters.product
    if (filters.startDate && filters.endDate) {
      params.start_date = filters.startDate
      params.end_date = filters.endDate
    } else if (filters.days) {
      params.days = filters.days
    }
    return params
  }

  const buildStockCoverageParams = () => {
    const params = {}
    if (filters.location) params.location = filters.location
    if (filters.product) params.product = filters.product
    if (filters.analysisDays) params.analysis_days = filters.analysisDays
    return params
  }

  // Load locations
  const loadLocations = async () => {
    if (locations.value.length > 0) return // Already loaded
    
    loadingStates.value.locations = true
    try {
      const response = await api.getLocations()
      locations.value = response.data.results || response.data || []
    } catch (err) {
      console.error('Error loading locations:', err)
      // Don't throw error for locations as they're not critical
    } finally {
      loadingStates.value.locations = false
    }
  }

  // Load products
  const loadProducts = async () => {
    if (products.value.length > 0) return // Already loaded
    
    loadingStates.value.products = true
    try {
      const response = await api.getProducts()
      products.value = response.data.results || response.data || []
    } catch (err) {
      console.error('Error loading products:', err)
      // Don't throw error for products as they're not critical
    } finally {
      loadingStates.value.products = false
    }
  }

  // Load current stock report
  const loadCurrentStock = async () => {
    loadingStates.value.currentStock = true
    try {
      const params = buildCurrentStockParams()
      const response = await api.getCurrentStockReport(params)
      currentStockData.value = response.data
    } catch (err) {
      console.error('Error loading current stock:', err)
      currentStockData.value = null
      throw new Error('Failed to load current stock report')
    } finally {
      loadingStates.value.currentStock = false
    }
  }

  // Load restock summary
  const loadRestockSummary = async () => {
    loadingStates.value.restockSummary = true
    try {
      const params = buildRestockSummaryParams()
      const response = await api.getRestockSummary(params)
      restockSummaryData.value = response.data
    } catch (err) {
      console.error('Error loading restock summary:', err)
      restockSummaryData.value = null
      throw new Error('Failed to load restock summary')
    } finally {
      loadingStates.value.restockSummary = false
    }
  }

  // Load stock coverage estimate
  const loadStockCoverage = async () => {
    loadingStates.value.stockCoverage = true
    try {
      const params = buildStockCoverageParams()
      const response = await api.getStockCoverageEstimate(params)
      stockCoverageData.value = response.data
    } catch (err) {
      console.error('Error loading stock coverage:', err)
      stockCoverageData.value = null
      throw new Error('Failed to load stock coverage estimate')
    } finally {
      loadingStates.value.stockCoverage = false
    }
  }

  // Initialize data with optimized loading
  const initialize = async () => {
    loading.value = true
    error.value = ''
    
    try {
      // First load reference data (locations and products) in parallel
      const referenceDataCalls = [
        loadLocations(),
        loadProducts()
      ]
      
      await Promise.allSettled(referenceDataCalls)
      
      // Then load all reports in parallel
      const reportCalls = [
        loadCurrentStock(),
        loadRestockSummary(),
        loadStockCoverage()
      ]
      
      const results = await Promise.allSettled(reportCalls)
      
      // Check if any critical reports failed
      const failedReports = results.filter(result => result.status === 'rejected')
      if (failedReports.length > 0) {
        console.warn(`${failedReports.length} inventory reports failed to load:`, 
          failedReports.map(f => f.reason?.message))
        error.value = `Some reports could not be loaded. ${failedReports.length} of ${reportCalls.length} reports failed.`
      }
      
    } catch (err) {
      console.error('Error initializing inventory reports:', err)
      error.value = 'Failed to load inventory data. Please try again.'
    } finally {
      loading.value = false
    }
  }

  // Apply filters to all reports
  const applyFilters = async () => {
    loading.value = true
    error.value = ''
    
    try {
      // Load all reports with new filters in parallel
      const reportCalls = [
        loadCurrentStock(),
        loadRestockSummary(),
        loadStockCoverage()
      ]
      
      const results = await Promise.allSettled(reportCalls)
      
      // Check if any reports failed
      const failedReports = results.filter(result => result.status === 'rejected')
      if (failedReports.length > 0) {
        console.warn(`${failedReports.length} inventory reports failed to reload:`, 
          failedReports.map(f => f.reason?.message))
        error.value = `Some reports could not be reloaded with the new filters.`
      }
      
    } catch (err) {
      console.error('Error applying filters:', err)
      error.value = 'Failed to apply filters. Please try again.'
    } finally {
      loading.value = false
    }
  }

  // Refresh specific report
  const refreshReport = async (reportType) => {
    try {
      switch (reportType) {
        case 'currentStock':
          await loadCurrentStock()
          break
        case 'restockSummary':
          await loadRestockSummary()
          break
        case 'stockCoverage':
          await loadStockCoverage()
          break
        default:
          await applyFilters()
      }
    } catch (err) {
      console.error(`Error refreshing ${reportType}:`, err)
      error.value = `Failed to refresh ${reportType} report`
    }
  }

  // Force refresh all data (bypass cache)
  const forceRefresh = async () => {
    loading.value = true
    error.value = ''
    
    try {
      // Clear inventory-related cache
      api.invalidateCache('/inventory')
      api.invalidateCache('/locations')
      api.invalidateCache('/products')
      
      // Reset reference data to force reload
      locations.value = []
      products.value = []
      
      await initialize()
    } catch (err) {
      console.error('Error force refreshing inventory reports:', err)
      error.value = 'Failed to refresh inventory data'
    } finally {
      loading.value = false
    }
  }

  // Clear all data
  const clearData = () => {
    currentStockData.value = null
    restockSummaryData.value = null
    stockCoverageData.value = null
    error.value = ''
  }

  // Reset filters
  const resetFilters = () => {
    Object.assign(filters, {
      location: '',
      product: '',
      machine: '',
      startDate: '',
      endDate: '',
      days: '7',
      analysisDays: '30'
    })
  }

  return {
    // State
    loading,
    error,
    locations,
    products,
    currentStockData,
    restockSummaryData,
    stockCoverageData,
    filters,
    loadingStates,
    
    // Computed
    isAnyLoading,
    hasFilters,
    
    // Individual loaders (for granular control)
    loadCurrentStock,
    loadRestockSummary,
    loadStockCoverage,
    
    // Main actions
    initialize,
    applyFilters,
    refreshReport,
    forceRefresh,
    clearData,
    resetFilters
  }
} 