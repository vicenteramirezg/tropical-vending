import { ref, computed } from 'vue'
import { api } from '../services/api'
import { getCurrentDateLocal, formatDateShort } from '../utils/dateUtils'

export function useAnalytics() {
  // Loading and error states
  const loading = ref(true)
  const error = ref(null)
  const locations = ref([])

  // Filter states
  const filters = ref({
    dateRange: '30',
    startDate: '',
    endDate: '',
    location: ''
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

  // Data fetching functions
  const fetchLocations = async () => {
    try {
      const response = await api.getLocations()
      locations.value = response.data
    } catch (err) {
      console.error('Error fetching locations:', err)
    }
  }

  const fetchRevenueProfitData = async () => {
    try {
      const params = {
        days: filters.value.dateRange !== 'custom' ? filters.value.dateRange : undefined,
        start_date: filters.value.dateRange === 'custom' ? filters.value.startDate : undefined,
        end_date: filters.value.dateRange === 'custom' ? filters.value.endDate : undefined,
        location: filters.value.location || undefined
      }
      
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
      error.value = 'Failed to load revenue and profit data'
      revenueProfitData.value = {
        revenue: { total: 0, change: 0 },
        profit: { total: 0, change: 0 },
        margin: { total: 0, change: 0 }
      }
    }
  }

  const fetchStockLevelData = async () => {
    try {
      const params = {
        location: filters.value.location || undefined
      }
      
      const response = await api.getStockLevels(params)
      
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
      error.value = 'Failed to load stock level data'
      stockLevelData.value = {
        low_stock_count: 0,
        items: []
      }
    }
  }

  const fetchDemandData = async () => {
    try {
      const params = {
        days: filters.value.dateRange !== 'custom' ? filters.value.dateRange : undefined,
        start_date: filters.value.dateRange === 'custom' ? filters.value.startDate : undefined,
        end_date: filters.value.dateRange === 'custom' ? filters.value.endDate : undefined,
        location: filters.value.location || undefined
      }
      
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
      error.value = 'Failed to load demand analysis data'
      demandData.value = {
        products: [],
        unit_counts: []
      }
    }
  }

  // Apply filters and refresh data
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
      
      await Promise.all([
        fetchRevenueProfitData(),
        fetchStockLevelData(),
        fetchDemandData()
      ])
    } catch (err) {
      console.error('Error refreshing data:', err)
      error.value = 'Failed to refresh analytics data'
    } finally {
      loading.value = false
    }
  }

  // Initialize data
  const initialize = async () => {
    try {
      await fetchLocations()
      await applyFilters()
    } catch (err) {
      console.error('Error initializing analytics:', err)
      error.value = 'Failed to load analytics data'
    } finally {
      loading.value = false
    }
  }

  return {
    // State
    loading,
    error,
    locations,
    filters,
    revenueProfitData,
    stockLevelData,
    demandData,
    
    // Computed
    sortedDemandCounts,
    
    // Helper functions
    getStockLevelClass,
    getTrendClass,
    formatTrend,
    formatDailyDemand,
    formatDateShort,
    
    // Actions
    applyFilters,
    initialize
  }
} 