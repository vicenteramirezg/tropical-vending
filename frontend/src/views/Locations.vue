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
    
    <div v-if="loading" class="flex justify-center py-20">
      <div class="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-primary-500"></div>
    </div>
    
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
    
    <div v-else-if="locations.length === 0" class="bg-white shadow-lg rounded-xl overflow-hidden">
      <div class="px-6 py-8 text-center">
        <svg xmlns="http://www.w3.org/2000/svg" class="h-16 w-16 mx-auto text-gray-400 mb-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z" />
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 11a3 3 0 11-6 0 3 3 0 016 0z" />
        </svg>
        <h3 class="text-lg leading-6 font-medium text-gray-900 mb-2">No locations found</h3>
        <div class="mt-2 max-w-xl text-sm text-gray-500 mx-auto mb-6">
          <p>Get started by adding your first location.</p>
        </div>
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
    </div>
    
    <div v-else class="bg-white shadow-lg rounded-xl overflow-hidden">
      <ul role="list" class="divide-y divide-gray-200">
        <li v-for="location in locations" :key="location.id" class="px-4 sm:px-6 py-4 sm:py-5 hover:bg-gray-50 transition-colors duration-150">
          <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
            <div>
              <p class="text-sm font-medium text-primary-600">{{ location.name }}</p>
              <p class="text-sm text-gray-500 mt-1">
                <span class="inline-flex items-center">
                  <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 mr-1 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z" />
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 11a3 3 0 11-6 0 3 3 0 016 0z" />
                  </svg>
                  {{ location.address }}
                </span>
              </p>
              <!-- Machine counts -->
              <div v-if="locationMachines[location.id]" class="mt-2 flex flex-wrap gap-2">
                <span 
                  v-for="(count, type) in locationMachines[location.id]" 
                  :key="type"
                  class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium"
                  :class="machineTypeColors[type] || 'bg-gray-100 text-gray-800'"
                >
                  {{ type }}: {{ count }}
                </span>
              </div>
            </div>
            <div class="flex flex-wrap gap-2 sm:flex-nowrap">
              <button
                @click="openMapForLocation(location)"
                class="w-full sm:w-auto inline-flex items-center justify-center px-3 py-1.5 border border-gray-300 shadow-sm text-xs font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500 transition-colors duration-150"
              >
                <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 mr-1" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z" />
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 11a3 3 0 11-6 0 3 3 0 016 0z" />
                </svg>
                View on Maps
              </button>
              <button
                @click="editLocation(location)"
                class="w-full sm:w-auto inline-flex items-center justify-center px-3 py-1.5 border border-gray-300 shadow-sm text-xs font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500 transition-colors duration-150"
              >
                <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 mr-1" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
                </svg>
                Edit
              </button>
              <button
                @click="confirmDelete(location)"
                class="w-full sm:w-auto inline-flex items-center justify-center px-3 py-1.5 border border-gray-300 shadow-sm text-xs font-medium rounded-md text-gray-700 bg-white hover:bg-red-50 hover:text-red-700 hover:border-red-300 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-red-500 transition-colors duration-150"
              >
                <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 mr-1" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                </svg>
                Delete
              </button>
            </div>
          </div>
        </li>
      </ul>
    </div>
    
    <!-- Add/Edit Modal -->
    <div v-if="showModal" class="fixed inset-0 overflow-y-auto z-50" aria-labelledby="modal-title" role="dialog" aria-modal="true">
      <div class="flex items-end justify-center min-h-screen pt-4 px-4 pb-20 text-center sm:block sm:p-0">
        <div class="fixed inset-0 bg-gray-500 bg-opacity-75 transition-opacity" aria-hidden="true" @click="showModal = false"></div>
        
        <span class="hidden sm:inline-block sm:align-middle sm:h-screen" aria-hidden="true">&#8203;</span>
        
        <div class="inline-block align-bottom bg-white rounded-xl text-left overflow-hidden shadow-xl transform transition-all sm:my-8 sm:align-middle sm:max-w-lg sm:w-full">
          <form @submit.prevent="saveLocation">
            <div class="bg-white px-4 pt-5 pb-4 sm:p-6 sm:pb-4">
              <div class="sm:flex sm:items-start">
                <div class="mt-3 text-center sm:mt-0 sm:text-left w-full">
                  <h3 class="text-lg leading-6 font-medium text-gray-900" id="modal-title">
                    {{ isEditing ? 'Edit Location' : 'Add New Location' }}
                  </h3>
                  <div class="mt-4 space-y-4">
                    <div>
                      <label for="name" class="block text-sm font-medium text-gray-700">Name</label>
                      <input 
                        type="text" 
                        name="name" 
                        id="name" 
                        v-model="locationForm.name"
                        class="mt-1 focus:ring-primary-500 focus:border-primary-500 block w-full shadow-sm sm:text-sm border-gray-300 rounded-md"
                        required
                      >
                    </div>
                    <div>
                      <label for="address" class="block text-sm font-medium text-gray-700">Address</label>
                      <textarea 
                        id="address" 
                        name="address" 
                        rows="3" 
                        v-model="locationForm.address"
                        class="shadow-sm focus:ring-primary-500 focus:border-primary-500 mt-1 block w-full sm:text-sm border border-gray-300 rounded-md"
                        required
                      ></textarea>
                    </div>
                  </div>
                </div>
              </div>
            </div>
            <div class="bg-gray-50 px-4 py-3 sm:px-6 sm:flex sm:flex-row-reverse">
              <button 
                type="submit"
                class="w-full inline-flex justify-center rounded-md border border-transparent shadow-sm px-4 py-2 bg-primary-600 text-base font-medium text-white hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500 sm:ml-3 sm:w-auto sm:text-sm transition-colors duration-150"
              >
                {{ isEditing ? 'Update' : 'Add' }}
              </button>
              <button 
                type="button"
                @click="showModal = false"
                class="mt-3 w-full inline-flex justify-center rounded-md border border-gray-300 shadow-sm px-4 py-2 bg-white text-base font-medium text-gray-700 hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500 sm:mt-0 sm:ml-3 sm:w-auto sm:text-sm transition-colors duration-150"
              >
                Cancel
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
    
    <!-- Delete Confirmation Modal -->
    <div v-if="showDeleteModal" class="fixed inset-0 overflow-y-auto z-50" aria-labelledby="modal-title" role="dialog" aria-modal="true">
      <div class="flex items-end justify-center min-h-screen pt-4 px-4 pb-20 text-center sm:block sm:p-0">
        <div class="fixed inset-0 bg-gray-500 bg-opacity-75 transition-opacity" aria-hidden="true" @click="showDeleteModal = false"></div>
        
        <span class="hidden sm:inline-block sm:align-middle sm:h-screen" aria-hidden="true">&#8203;</span>
        
        <div class="inline-block align-bottom bg-white rounded-xl text-left overflow-hidden shadow-xl transform transition-all sm:my-8 sm:align-middle sm:max-w-lg sm:w-full">
          <div class="bg-white px-4 pt-5 pb-4 sm:p-6 sm:pb-4">
            <div class="sm:flex sm:items-start">
              <div class="mx-auto flex-shrink-0 flex items-center justify-center h-12 w-12 rounded-full bg-red-100 sm:mx-0 sm:h-10 sm:w-10">
                <!-- Warning icon -->
                <svg class="h-6 w-6 text-red-600" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor" aria-hidden="true">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
                </svg>
              </div>
              <div class="mt-3 text-center sm:mt-0 sm:ml-4 sm:text-left">
                <h3 class="text-lg leading-6 font-medium text-gray-900" id="modal-title">
                  Delete Location
                </h3>
                <div class="mt-2">
                  <p class="text-sm text-gray-500">
                    Are you sure you want to delete <span class="font-medium">{{ locationToDelete?.name }}</span>? This action cannot be undone.
                  </p>
                </div>
              </div>
            </div>
          </div>
          <div class="bg-gray-50 px-4 py-3 sm:px-6 sm:flex sm:flex-row-reverse">
            <button 
              type="button"
              @click="deleteLocation"
              class="w-full inline-flex justify-center rounded-md border border-transparent shadow-sm px-4 py-2 bg-red-600 text-base font-medium text-white hover:bg-red-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-red-500 sm:ml-3 sm:w-auto sm:text-sm transition-colors duration-150"
            >
              Delete
            </button>
            <button 
              type="button"
              @click="showDeleteModal = false"
              class="mt-3 w-full inline-flex justify-center rounded-md border border-gray-300 shadow-sm px-4 py-2 bg-white text-base font-medium text-gray-700 hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500 sm:mt-0 sm:ml-3 sm:w-auto sm:text-sm transition-colors duration-150"
            >
              Cancel
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { api } from '../services/api'

const locations = ref([])
const machines = ref([])
const loading = ref(true)
const error = ref(null)

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

// Modal states
const showModal = ref(false)
const showDeleteModal = ref(false)
const isEditing = ref(false)
const locationToDelete = ref(null)

// Form for creating/editing a location
const locationForm = ref({
  id: null,
  name: '',
  address: ''
})

// Fetch all locations
const fetchLocations = async () => {
  loading.value = true
  try {
    const response = await api.getLocations()
    locations.value = response.data
    
    // After locations are loaded, fetch machines
    await fetchMachines()
  } catch (err) {
    console.error('Error fetching locations:', err)
    error.value = 'Failed to load locations. Please try again later.'
  } finally {
    loading.value = false
  }
}

// Fetch all machines to count by location
const fetchMachines = async () => {
  try {
    const response = await api.getMachines()
    machines.value = response.data
  } catch (err) {
    console.error('Error fetching machines:', err)
  }
}

// Open modal to add a new location
const openAddModal = () => {
  isEditing.value = false
  locationForm.value = {
    id: null,
    name: '',
    address: ''
  }
  showModal.value = true
}

// Open modal to edit an existing location
const editLocation = (location) => {
  isEditing.value = true
  locationForm.value = {
    id: location.id,
    name: location.name,
    address: location.address
  }
  showModal.value = true
}

// Save the location (create or update)
const saveLocation = async () => {
  try {
    if (isEditing.value) {
      await api.updateLocation(locationForm.value.id, locationForm.value)
    } else {
      await api.createLocation(locationForm.value)
    }
    
    showModal.value = false
    await fetchLocations()
  } catch (err) {
    console.error('Error saving location:', err)
    error.value = 'Failed to save location. Please try again.'
  }
}

// Show delete confirmation modal
const confirmDelete = (location) => {
  locationToDelete.value = location
  showDeleteModal.value = true
}

// Delete the location
const deleteLocation = async () => {
  if (!locationToDelete.value) return
  
  try {
    await api.deleteLocation(locationToDelete.value.id)
    showDeleteModal.value = false
    await fetchLocations()
  } catch (err) {
    console.error('Error deleting location:', err)
    error.value = 'Failed to delete location. Please try again.'
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

// Initialize data on component mount
onMounted(fetchLocations)
</script> 