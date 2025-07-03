<template>
  <div>
    <!-- Header -->
    <div class="flex justify-between items-center mb-6">
      <h1 class="text-2xl font-semibold text-gray-900">Location Visits</h1>
      <button 
        @click="handleAddRestock" 
        class="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-primary-600 hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500"
      >
        Record New Visit
      </button>
    </div>
    
    <!-- Restock List -->
    <RestockList
      :restocks="restocks"
      :loading="loading"
      :error="error"
      @add-restock="handleAddRestock"
      @view-details="handleViewDetails"
      @edit-restock="handleEditRestock"
      @delete-restock="handleDeleteRestock"
    />
    
    <!-- Add/Edit Modal -->
    <RestockFormModal
      :show="showModal"
      :is-editing="isEditing"
      :restock-form="restockForm"
      :selected-location="selectedLocation"
      :selected-route="selectedRoute"
      :location-search-text="locationSearchText"
      :locations="filteredLocations"
      :routes="routes"
      :location-machines="locationMachines"
      @close="showModal = false"
      @save="handleSaveRestock"
      @route-change="handleRouteChange"
      @location-search="handleLocationSearch"
      @location-change="handleLocationChange"
    />
    
    <!-- View Details Modal -->
    <RestockDetailsModal
      :show="showDetailsModal"
      :restock="selectedRestock"
      @close="showDetailsModal = false"
    />

    <!-- Delete Confirmation Modal -->
    <DeleteConfirmationModal
      :show="showDeleteModal"
      :restock="selectedDeleteRestock"
      @close="showDeleteModal = false"
      @confirm="handleConfirmDelete"
    />
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useAuthStore } from '../store/auth'
import { useRestocks } from '../composables/useRestocks'
import { useLocations } from '../composables/useLocations'
import { useMachines } from '../composables/useMachines'
import { useRestockForm } from '../composables/useRestockForm'

// Components
import RestockList from '../components/restocks/RestockList.vue'
import RestockFormModal from '../components/restocks/RestockFormModal.vue'
import RestockDetailsModal from '../components/restocks/RestockDetailsModal.vue'
import DeleteConfirmationModal from '../components/restocks/DeleteConfirmationModal.vue'

// Composables
const authStore = useAuthStore()
const { restocks, loading, error, fetchRestocks, createVisit, updateVisit, deleteVisit, getVisitDetails } = useRestocks()
const { filteredLocations, routes, selectedRoute, locationSearchText, fetchLocations, fetchRoutes, resetFilters } = useLocations()
const { locationMachines, fetchLocationMachines, updateMachineProductData, resetMachineData } = useMachines()
const { restockForm, isEditing, selectedLocation, initializeForm, saveRestock, resetForm } = useRestockForm()

// Modal states
const showModal = ref(false)
const showDetailsModal = ref(false)
const showDeleteModal = ref(false)
const selectedRestock = ref(null)
const selectedDeleteRestock = ref(null)

// Handlers
const handleAddRestock = () => {
  initializeForm()
  resetFilters()
  resetMachineData()
  showModal.value = true
}

const handleEditRestock = async (restock) => {
  initializeForm(restock)
  resetFilters()
  
  // Fetch machines for this location first
  await fetchLocationMachines(restock.location_id)
  
  try {
    // Update machine product data with existing restock entries
    for (const machine of locationMachines.value) {
      await updateMachineProductData(restock.id, machine.id)
    }
    
    showModal.value = true
  } catch (err) {
    console.error('Error loading visit for editing:', err)
    error.value = 'Failed to load visit details for editing. Please try again.'
  }
}

const handleViewDetails = async (restock) => {
  selectedRestock.value = restock
  
  try {
    const entries = await getVisitDetails(restock.id)
    selectedRestock.value = {
      ...restock,
      entries: entries
    }
    
    showDetailsModal.value = true
  } catch (err) {
    console.error('Error fetching visit details:', err)
    error.value = 'Failed to load visit details. Please try again.'
  }
}

const handleDeleteRestock = (restock) => {
  selectedDeleteRestock.value = restock
  showDeleteModal.value = true
}

const handleConfirmDelete = async () => {
  try {
    await deleteVisit(selectedDeleteRestock.value.id)
    showDeleteModal.value = false
    selectedDeleteRestock.value = null
  } catch (err) {
    console.error('Error deleting visit:', err)
    error.value = 'Failed to delete visit. Please try again.'
  }
}

const handleSaveRestock = async () => {
  const success = await saveRestock(locationMachines.value, createVisit, updateVisit)
  if (success) {
    showModal.value = false
    await fetchRestocks()
  }
}

const handleRouteChange = (value) => {
  selectedRoute.value = value
  selectedLocation.value = ''
  resetMachineData()
}

const handleLocationSearch = (value) => {
  locationSearchText.value = value
}

const handleLocationChange = (value) => {
  selectedLocation.value = value
  fetchLocationMachines(value)
}

// Initialize data on component mount
onMounted(async () => {
  // Make sure user data is loaded if we're authenticated but don't have user info
  if (authStore.isAuthenticated && !authStore.user) {
    await authStore.fetchUser()
  }
  
  // Log the current user to help with debugging
  console.log('Current user:', authStore.user)
  
  await Promise.all([fetchRestocks(), fetchLocations(), fetchRoutes()])
})
</script> 