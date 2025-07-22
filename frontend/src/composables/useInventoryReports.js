import { ref, reactive, computed } from 'vue'
import { api } from '../services/api'

export function useInventoryReports() {
  // Loading states
  const loading = ref(false)
  const error = ref('')
  const currentStockLoading = ref(false)
  const restockSummaryLoading = ref(false)
  const stockCoverageLoading = ref(false)

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

  // Initialize data
  const initialize = async () => {
    loading.value = true
    error.value = ''
    
    try {
      // Load initial data
      await Promise.all([
        loadLocations(),
        loadProducts(),
        loadCurrentStock(),
        loadRestockSummary(),
        loadStockCoverage()
      ])
    } catch (err) {
      console.error('Error initializing inventory reports:', err)
      error.value = 'Failed to load inventory data. Please try again.'
    } finally {
      loading.value = false
    }
  }

  // Load locations
  const loadLocations = async () => {
    try {
      const response = await api.get('/locations/')
      locations.value = response.data.results || response.data || []
    } catch (err) {
      console.error('Error loading locations:', err)
    }
  }

  // Load products
  const loadProducts = async () => {
    try {
      const response = await api.get('/products/')
      products.value = response.data.results || response.data || []
    } catch (err) {
      console.error('Error loading products:', err)
    }
  }

  // Load current stock report
  const loadCurrentStock = async () => {
    currentStockLoading.value = true
    try {
      const params = {}
      if (filters.location) params.location = filters.location
      if (filters.product) params.product = filters.product
      if (filters.machine) params.machine = filters.machine

      const response = await api.get('/inventory/current-stock/', { params })
      currentStockData.value = response.data
    } catch (err) {
      console.error('Error loading current stock:', err)
      throw err
    } finally {
      currentStockLoading.value = false
    }
  }

  // Load restock summary
  const loadRestockSummary = async () => {
    restockSummaryLoading.value = true
    try {
      const params = {}
      if (filters.location) params.location = filters.location
      if (filters.product) params.product = filters.product
      if (filters.startDate && filters.endDate) {
        params.start_date = filters.startDate
        params.end_date = filters.endDate
      } else if (filters.days) {
        params.days = filters.days
      }

      const response = await api.get('/inventory/restock-summary/', { params })
      restockSummaryData.value = response.data
    } catch (err) {
      console.error('Error loading restock summary:', err)
      throw err
    } finally {
      restockSummaryLoading.value = false
    }
  }

  // Load stock coverage estimate
  const loadStockCoverage = async () => {
    stockCoverageLoading.value = true
    try {
      const params = {}
      if (filters.location) params.location = filters.location
      if (filters.product) params.product = filters.product
      if (filters.analysisDays) params.analysis_days = filters.analysisDays

      const response = await api.get('/inventory/stock-coverage/', { params })
      stockCoverageData.value = response.data
    } catch (err) {
      console.error('Error loading stock coverage:', err)
      throw err
    } finally {
      stockCoverageLoading.value = false
    }
  }

  // Apply filters and refresh data
  const applyFilters = async () => {
    error.value = ''
    try {
      await Promise.all([
        loadCurrentStock(),
        loadRestockSummary(),
        loadStockCoverage()
      ])
    } catch (err) {
      error.value = 'Failed to apply filters. Please try again.'
    }
  }

  // Format utilities
  const formatDate = (date) => {
    return new Date(date).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric'
    })
  }

  const formatDateTime = (date) => {
    return new Date(date).toLocaleString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    })
  }

  const getStockLevelClass = (stock, threshold = 5) => {
    if (stock === 0) return 'text-red-600 bg-red-50'
    if (stock < threshold) return 'text-orange-600 bg-orange-50'
    return 'text-green-600 bg-green-50'
  }

  const getCoverageStatusClass = (status) => {
    switch (status) {
      case 'critical':
        return 'text-red-600 bg-red-50'
      case 'low':
        return 'text-orange-600 bg-orange-50'
      case 'moderate':
        return 'text-yellow-600 bg-yellow-50'
      case 'good':
        return 'text-green-600 bg-green-50'
      default:
        return 'text-gray-600 bg-gray-50'
    }
  }

  const getCoverageStatusText = (status) => {
    switch (status) {
      case 'critical':
        return 'Critical'
      case 'low':
        return 'Low'
      case 'moderate':
        return 'Moderate'
      case 'good':
        return 'Good'
      default:
        return 'Unknown'
    }
  }

  return {
    // State
    loading,
    error,
    currentStockLoading,
    restockSummaryLoading,
    stockCoverageLoading,
    
    // Data
    locations,
    products,
    currentStockData,
    restockSummaryData,
    stockCoverageData,
    
    // Filters
    filters,
    
    // Methods
    initialize,
    applyFilters,
    loadCurrentStock,
    loadRestockSummary,
    loadStockCoverage,
    
    // Utilities
    formatDate,
    formatDateTime,
    getStockLevelClass,
    getCoverageStatusClass,
    getCoverageStatusText
  }
} 