import { ref } from 'vue'
import { api } from '../services/api'

export function useMachineFilters() {
  const locations = ref([])
  const availableRoutes = ref([])
  const locationInfo = ref({})
  const locationNames = ref({})
  
  // Filter state
  const filters = ref({
    location: '',
    machineType: '',
    route: ''
  })

  // Fetch all locations
  const fetchLocations = async () => {
    try {
      const response = await api.getLocations()
      locations.value = response.data
      
      // Create lookup objects for location names and info
      response.data.forEach(location => {
        locationNames.value[location.id] = location.name
        locationInfo.value[location.id] = location
      })
    } catch (err) {
      console.error('Error fetching locations:', err)
    }
  }

  // Fetch available routes
  const fetchRoutes = async () => {
    try {
      const response = await api.getRoutes()
      availableRoutes.value = response.data.routes
    } catch (err) {
      console.error('Error fetching routes:', err)
    }
  }

  // Reset filters
  const resetFilters = () => {
    filters.value = {
      location: '',
      machineType: '',
      route: ''
    }
  }

  // Open Google Maps for location
  const openMapForLocation = (location) => {
    if (!location || !location.address) return
    
    // Format the address for Google Maps URL
    const formattedAddress = encodeURIComponent(location.address)
    const mapsUrl = `https://www.google.com/maps/search/?api=1&query=${formattedAddress}`
    
    // Open in a new window/tab
    window.open(mapsUrl, '_blank')
  }

  return {
    // State
    locations,
    availableRoutes,
    locationInfo,
    locationNames,
    filters,
    
    // Actions
    fetchLocations,
    fetchRoutes,
    resetFilters,
    openMapForLocation
  }
} 