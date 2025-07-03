import { ref, computed, onMounted } from 'vue'
import { api } from '../services/api'

export function useLocations() {
  // State
  const locations = ref([])
  const allLocations = ref([]) // Store all locations for filtering
  const machines = ref([])
  const loading = ref(true)
  const error = ref(null)
  const selectedRoute = ref('')
  const availableRoutes = ref([])

  // Machine type colors for badges
  const machineTypeColors = {
    'Vending': 'bg-blue-100 text-blue-800',
    'Coffee': 'bg-amber-100 text-amber-800',
    'Snack': 'bg-green-100 text-green-800',
    'Drink': 'bg-purple-100 text-purple-800'
  }

  // Computed property to organize machines by location
  const locationMachines = computed(() => {
    const result = {}
    
    // Initialize all locations with empty objects
    locations.value.forEach(location => {
      result[location.id] = {}
    })
    
    // Count machines by type for each location
    machines.value.forEach(machine => {
      if (machine.location) {
        if (!result[machine.location]) {
          result[machine.location] = {}
        }
        
        if (!result[machine.location][machine.machine_type]) {
          result[machine.location][machine.machine_type] = 0
        }
        
        result[machine.location][machine.machine_type]++
      }
    })
    
    return result
  })

  // API Methods
  const fetchLocations = async () => {
    loading.value = true
    try {
      const response = await api.getLocations()
      allLocations.value = response.data
      locations.value = response.data
      
      // After locations are loaded, fetch machines and routes
      await Promise.all([fetchMachines(), fetchRoutes()])
    } catch (err) {
      console.error('Error fetching locations:', err)
      error.value = 'Failed to load locations. Please try again later.'
    } finally {
      loading.value = false
    }
  }

  const fetchMachines = async () => {
    try {
      const response = await api.getMachines()
      machines.value = response.data
    } catch (err) {
      console.error('Error fetching machines:', err)
    }
  }

  const fetchRoutes = async () => {
    try {
      const response = await api.getRoutes()
      availableRoutes.value = response.data.routes
    } catch (err) {
      console.error('Error fetching routes:', err)
    }
  }

  const createLocation = async (locationData) => {
    try {
      await api.createLocation(locationData)
      await fetchLocations()
      clearRouteFilter()
    } catch (err) {
      console.error('Error creating location:', err)
      error.value = 'Failed to create location. Please try again.'
      throw err
    }
  }

  const updateLocation = async (id, locationData) => {
    try {
      await api.updateLocation(id, locationData)
      await fetchLocations()
      clearRouteFilter()
    } catch (err) {
      console.error('Error updating location:', err)
      error.value = 'Failed to update location. Please try again.'
      throw err
    }
  }

  const deleteLocation = async (id) => {
    try {
      await api.deleteLocation(id)
      await fetchLocations()
      clearRouteFilter()
    } catch (err) {
      console.error('Error deleting location:', err)
      error.value = 'Failed to delete location. Please try again.'
      throw err
    }
  }

  // Filter Methods
  const applyRouteFilter = () => {
    if (!selectedRoute.value) {
      locations.value = allLocations.value
    } else if (selectedRoute.value === 'unassigned') {
      locations.value = allLocations.value.filter(location => !location.route)
    } else {
      locations.value = allLocations.value.filter(location => location.route === selectedRoute.value)
    }
  }

  const clearRouteFilter = () => {
    selectedRoute.value = ''
    locations.value = allLocations.value
  }

  // Utility Methods
  const openMapForLocation = (location) => {
    if (!location || !location.address) return
    
    const formattedAddress = encodeURIComponent(location.address)
    const mapsUrl = `https://www.google.com/maps/search/?api=1&query=${formattedAddress}`
    
    window.open(mapsUrl, '_blank')
  }

  // Initialize data
  onMounted(fetchLocations)

  return {
    // State
    locations,
    allLocations,
    machines,
    loading,
    error,
    selectedRoute,
    availableRoutes,
    machineTypeColors,
    locationMachines,
    
    // Methods
    fetchLocations,
    createLocation,
    updateLocation,
    deleteLocation,
    applyRouteFilter,
    clearRouteFilter,
    openMapForLocation
  }
} 