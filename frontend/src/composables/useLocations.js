import { ref, computed } from 'vue'
import { api } from '../services/api'

export function useLocations() {
  const allLocations = ref([])
  const routes = ref([])
  const selectedRoute = ref('')
  const locationSearchText = ref('')
  const loading = ref(false)
  const error = ref(null)

  // Computed filtered locations
  const filteredLocations = computed(() => {
    let filtered = allLocations.value
    
    // Filter by route if selected
    if (selectedRoute.value) {
      if (selectedRoute.value === 'unassigned') {
        filtered = filtered.filter(location => 
          !location.route || location.route.trim() === ''
        )
      } else {
        filtered = filtered.filter(location => 
          location.route === selectedRoute.value
        )
      }
    }
    
    // Filter by search text if provided
    if (locationSearchText.value.trim()) {
      const searchTerm = locationSearchText.value.toLowerCase().trim()
      filtered = filtered.filter(location =>
        location.name.toLowerCase().includes(searchTerm) ||
        (location.address && location.address.toLowerCase().includes(searchTerm))
      )
    }
    
    return filtered
  })

  const fetchLocations = async () => {
    loading.value = true
    error.value = null
    try {
      const response = await api.getLocations()
      allLocations.value = response.data
    } catch (err) {
      console.error('Error fetching locations:', err)
      error.value = 'Failed to load locations. Please try again later.'
    } finally {
      loading.value = false
    }
  }

  const fetchRoutes = async () => {
    try {
      const response = await api.getRoutes()
      routes.value = response.data.routes
    } catch (err) {
      console.error('Error fetching routes:', err)
      error.value = 'Failed to load routes. Please try again later.'
    }
  }

  const resetFilters = () => {
    selectedRoute.value = ''
    locationSearchText.value = ''
  }

  return {
    allLocations,
    routes,
    selectedRoute,
    locationSearchText,
    filteredLocations,
    loading,
    error,
    fetchLocations,
    fetchRoutes,
    resetFilters
  }
} 