<template>
  <div>
    <div class="flex justify-between items-center mb-6">
      <h1 class="text-2xl font-semibold text-gray-900">Locations</h1>
      <button 
        @click="openAddModal" 
        class="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-primary-600 hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500 transition-colors duration-150"
      >
        <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 mr-1.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
        </svg>
        Add Location
      </button>
    </div>
    
    <!-- Route Filter -->
    <RouteFilter
      v-model:selectedRoute="selectedRoute"
      :available-routes="availableRoutes"
      @update:selectedRoute="applyRouteFilter"
      @clear-filter="clearRouteFilter"
    />
    
    <!-- Loading State -->
    <div v-if="loading" class="flex justify-center py-20">
      <div class="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-primary-500"></div>
    </div>
    
    <!-- Error State -->
    <div v-else-if="error" class="bg-red-50 border-l-4 border-red-400 p-4 mb-6 rounded-r-lg shadow-sm">
      <div class="flex">
        <div class="flex-shrink-0">
          <svg class="h-5 w-5 text-red-400" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor">
            <path fill-rule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clip-rule="evenodd" />
          </svg>
        </div>
        <div class="ml-3">
          <p class="text-sm text-red-700">{{ error }}</p>
        </div>
      </div>
    </div>
    
    <!-- Location List -->
    <LocationList
      v-else
      :locations="locations"
      :location-machines="locationMachines"
      :machine-type-colors="machineTypeColors"
      @add-location="openAddModal"
      @view-on-map="openMapForLocation"
      @edit-location="openEditModal"
      @delete-location="openDeleteModal"
    />
    
    <!-- Add/Edit Modal -->
    <LocationModal
      :show="showModal"
      :location="editingLocation"
      @close="closeModal"
      @save="saveLocation"
    />
    
    <!-- Delete Confirmation Modal -->
    <DeleteConfirmationModal
      :show="showDeleteModal"
      :location="locationToDelete"
      @close="closeDeleteModal"
      @confirm="confirmDelete"
    />
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useLocations } from '../composables/useLocations'
import RouteFilter from '../components/locations/RouteFilter.vue'
import LocationList from '../components/locations/LocationList.vue'
import LocationModal from '../components/locations/LocationModal.vue'
import DeleteConfirmationModal from '../components/locations/DeleteConfirmationModal.vue'

// Use the locations composable
const {
  locations,
  loading,
  error,
  selectedRoute,
  availableRoutes,
  machineTypeColors,
  locationMachines,
  createLocation,
  updateLocation,
  deleteLocation,
  applyRouteFilter,
  clearRouteFilter,
  openMapForLocation
} = useLocations()

// Modal states
const showModal = ref(false)
const showDeleteModal = ref(false)
const editingLocation = ref(null)
const locationToDelete = ref(null)

// Modal handlers
const openAddModal = () => {
  editingLocation.value = null
  showModal.value = true
}

const openEditModal = (location) => {
  editingLocation.value = location
  showModal.value = true
}

const closeModal = () => {
  showModal.value = false
  editingLocation.value = null
}

const openDeleteModal = (location) => {
  locationToDelete.value = location
  showDeleteModal.value = true
}

const closeDeleteModal = () => {
  showDeleteModal.value = false
  locationToDelete.value = null
}

// Save location (create or update)
const saveLocation = async (locationData) => {
  try {
    if (locationData.id) {
      await updateLocation(locationData.id, locationData)
    } else {
      await createLocation(locationData)
    }
    closeModal()
  } catch (err) {
    // Error handling is done in the composable
    console.error('Error saving location:', err)
  }
}

// Confirm delete
const confirmDelete = async () => {
  if (!locationToDelete.value) return
  
  try {
    await deleteLocation(locationToDelete.value.id)
    closeDeleteModal()
  } catch (err) {
    // Error handling is done in the composable
    console.error('Error deleting location:', err)
  }
}
</script> 