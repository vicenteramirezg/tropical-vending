import { ref, reactive } from 'vue'
import { api } from '../services/api'

export function useDashboard() {
  const loading = ref(true)
  const error = ref(null)
  const locations = ref([])
  
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

  // Fetch locations for the dropdown
  const fetchLocations = async () => {
    try {
      const response = await api.getLocations()
      locations.value = response.data
    } catch (err) {
      console.error('Error fetching locations:', err)
      error.value = 'Failed to load locations'
    }
  }

  // Apply filters and refresh dashboard data
  const applyFilters = async () => {
    loading.value = true
    error.value = null
    
    try {
      const params = {
        days: filters.timeRange,
        location: filters.location || undefined,
        machine_type: filters.machineType || undefined
      }
      
      const response = await api.getDashboardData(params)
      data.value = response.data
    } catch (err) {
      console.error('Error fetching dashboard data:', err)
      error.value = 'Failed to load dashboard data'
    } finally {
      loading.value = false
    }
  }

  // Initialize dashboard data
  const initializeDashboard = async () => {
    await fetchLocations()
    await applyFilters()
  }

  // Utility function for stock level classes
  const getStockLevelClass = (quantity) => {
    if (quantity <= 0) return 'bg-red-100 text-red-800'
    if (quantity <= 3) return 'bg-yellow-100 text-yellow-800'
    return 'bg-blue-100 text-blue-800'
  }

  return {
    loading,
    error,
    locations,
    data,
    filters,
    fetchLocations,
    applyFilters,
    initializeDashboard,
    getStockLevelClass
  }
} 