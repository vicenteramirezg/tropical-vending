<template>
  <div>
    <div class="flex justify-between items-center mb-6">
      <h1 class="text-2xl font-bold text-gray-900">Machines</h1>
      <button 
        @click="openAddModal" 
        class="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-primary-600 hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500 transition-colors duration-150"
      >
        <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 mr-1.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
        </svg>
        Add Machine
      </button>
    </div>
    
    <!-- Filter Options -->
    <div class="bg-white p-5 shadow-lg rounded-xl mb-6">
      <div class="flex flex-wrap items-center gap-4">
        <div>
          <label for="locationFilter" class="block text-sm font-medium text-gray-700 mb-1">Location</label>
          <select
            id="locationFilter"
            v-model="filters.location"
            class="block w-full border-gray-300 rounded-md shadow-sm focus:ring-primary-500 focus:border-primary-500 sm:text-sm"
            @change="applyFilters"
          >
            <option value="">All Locations</option>
            <option v-for="location in locations" :key="location.id" :value="location.id">
              {{ location.name }}
            </option>
          </select>
        </div>
        
        <div>
          <label for="typeFilter" class="block text-sm font-medium text-gray-700 mb-1">Machine Type</label>
          <select
            id="typeFilter"
            v-model="filters.machineType"
            class="block w-full border-gray-300 rounded-md shadow-sm focus:ring-primary-500 focus:border-primary-500 sm:text-sm"
            @change="applyFilters"
          >
            <option value="">All Types</option>
            <option value="Snack">Snack</option>
            <option value="Soda">Soda</option>
            <option value="Combo">Combo</option>
          </select>
        </div>
        
        <div class="self-end ml-auto mt-4">
          <button
            type="button"
            @click="applyFilters"
            class="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-primary-600 hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500 transition-colors duration-150"
          >
            <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 mr-1.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 4a1 1 0 011-1h16a1 1 0 011 1v2.586a1 1 0 01-.293.707l-6.414 6.414a1 1 0 00-.293.707V17l-4 4v-6.586a1 1 0 00-.293-.707L3.293 7.293A1 1 0 013 6.586V4z" />
            </svg>
            Apply Filters
          </button>
        </div>
      </div>
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
    
    <div v-else-if="Object.keys(groupedMachines).length === 0" class="bg-white shadow-lg rounded-xl overflow-hidden">
      <div class="px-6 py-8 text-center">
        <svg xmlns="http://www.w3.org/2000/svg" class="h-16 w-16 mx-auto text-gray-400 mb-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 3v2m6-2v2M9 19v2m6-2v2M5 9H3m2 6H3m18-6h-2m2 6h-2M7 19h10a2 2 0 002-2V7a2 2 0 00-2-2H7a2 2 0 00-2 2v10a2 2 0 002 2zM9 9h6v6H9V9z" />
        </svg>
        <h3 class="text-lg leading-6 font-medium text-gray-900 mb-2">No machines found</h3>
        <div class="mt-2 max-w-xl text-sm text-gray-500 mx-auto mb-6">
          <p>Get started by adding your first machine.</p>
        </div>
        <button
          @click="openAddModal"
          class="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-primary-600 hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500 transition-colors duration-150"
        >
          <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 mr-1.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
          </svg>
          Add Machine
        </button>
      </div>
    </div>
    
    <div v-else class="space-y-6">
      <!-- Group machines by location -->
      <div v-for="(machines, locationId) in groupedMachines" :key="locationId" class="bg-white shadow-lg rounded-xl overflow-hidden">
        <div class="px-6 py-4 bg-gray-50 border-b border-gray-200 flex justify-between items-center">
          <div>
            <h2 class="text-lg font-medium text-gray-900">{{ locationNames[locationId] }}</h2>
            <p class="text-sm text-gray-500">{{ machines.length }} machines</p>
          </div>
          <button 
            @click="openMapForLocation(locationInfo[locationId])" 
            class="inline-flex items-center px-3 py-1.5 border border-gray-300 shadow-sm text-xs font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500 transition-colors duration-150"
          >
            <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 mr-1.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z" />
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 11a3 3 0 11-6 0 3 3 0 016 0z" />
            </svg>
            View on Maps
          </button>
        </div>
        
        <ul role="list" class="divide-y divide-gray-200">
          <li v-for="machine in machines" :key="machine.id" class="px-6 py-5 hover:bg-gray-50 transition-colors duration-150">
            <div class="flex items-center justify-between">
              <div>
                <div class="flex items-center">
                  <p class="text-sm font-medium text-primary-600">{{ machine.name }}</p>
                  <span 
                    class="ml-2 inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium"
                    :class="{
                      'bg-blue-100 text-blue-800': machine.machine_type === 'Soda',
                      'bg-green-100 text-green-800': machine.machine_type === 'Snack',
                      'bg-purple-100 text-purple-800': machine.machine_type === 'Combo'
                    }"
                  >
                    {{ machine.machine_type }}
                  </span>
                </div>
                <p v-if="machine.model" class="text-sm text-gray-500 mt-1">Model: {{ machine.model }}</p>
              </div>
              <div class="flex space-x-2">
                <button
                  @click="editMachine(machine)"
                  class="inline-flex items-center px-3 py-1.5 border border-gray-300 shadow-sm text-xs font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500 transition-colors duration-150"
                >
                  <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 mr-1" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
                  </svg>
                  Edit
                </button>
                <button
                  @click="confirmDelete(machine)"
                  class="inline-flex items-center px-3 py-1.5 border border-gray-300 shadow-sm text-xs font-medium rounded-md text-gray-700 bg-white hover:bg-red-50 hover:text-red-700 hover:border-red-300 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-red-500 transition-colors duration-150"
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
    </div>
    
    <!-- Add/Edit Modal -->
    <div v-if="showModal" class="fixed inset-0 overflow-y-auto" aria-labelledby="modal-title" role="dialog" aria-modal="true">
      <div class="flex items-end justify-center min-h-screen pt-4 px-4 pb-20 text-center sm:block sm:p-0">
        <div class="fixed inset-0 bg-gray-500 bg-opacity-75 transition-opacity" aria-hidden="true" @click="showModal = false"></div>
        
        <span class="hidden sm:inline-block sm:align-middle sm:h-screen" aria-hidden="true">&#8203;</span>
        
        <div class="inline-block align-bottom bg-white rounded-lg text-left overflow-hidden shadow-xl transform transition-all sm:my-8 sm:align-middle sm:max-w-lg sm:w-full">
          <form @submit.prevent="saveMachine">
            <div class="bg-white px-4 pt-5 pb-4 sm:p-6 sm:pb-4">
              <div class="sm:flex sm:items-start">
                <div class="mt-3 text-center sm:mt-0 sm:text-left w-full">
                  <h3 class="text-lg leading-6 font-medium text-gray-900" id="modal-title">
                    {{ isEditing ? 'Edit Machine' : 'Add New Machine' }}
                  </h3>
                  <div class="mt-4 space-y-4">
                    <div>
                      <label for="name" class="block text-sm font-medium text-gray-700">Machine Name</label>
                      <input 
                        type="text" 
                        name="name" 
                        id="name" 
                        v-model="machineForm.name"
                        placeholder="e.g. Building A Snack Machine"
                        class="mt-1 focus:ring-primary-500 focus:border-primary-500 block w-full shadow-sm sm:text-sm border-gray-300 rounded-md"
                        required
                      >
                    </div>
                    <div>
                      <label for="location" class="block text-sm font-medium text-gray-700">Location</label>
                      <select
                        id="location"
                        name="location"
                        v-model="machineForm.location"
                        class="mt-1 block w-full pl-3 pr-10 py-2 text-base border-gray-300 focus:outline-none focus:ring-primary-500 focus:border-primary-500 sm:text-sm rounded-md"
                        required
                      >
                        <option value="" disabled>Select a location</option>
                        <option v-for="location in locations" :key="location.id" :value="location.id">
                          {{ location.name }}
                        </option>
                      </select>
                    </div>
                    <div>
                      <label for="machine_type" class="block text-sm font-medium text-gray-700">Machine Type</label>
                      <select
                        id="machine_type"
                        name="machine_type"
                        v-model="machineForm.machine_type"
                        class="mt-1 block w-full pl-3 pr-10 py-2 text-base border-gray-300 focus:outline-none focus:ring-primary-500 focus:border-primary-500 sm:text-sm rounded-md"
                        required
                      >
                        <option value="" disabled>Select a machine type</option>
                        <option value="Snack">Snack</option>
                        <option value="Soda">Soda</option>
                        <option value="Combo">Combo</option>
                      </select>
                    </div>
                    <div>
                      <label for="model" class="block text-sm font-medium text-gray-700">Model (Optional)</label>
                      <select
                        id="model"
                        name="model"
                        v-model="machineForm.model"
                        class="mt-1 block w-full pl-3 pr-10 py-2 text-base border-gray-300 focus:outline-none focus:ring-primary-500 focus:border-primary-500 sm:text-sm rounded-md"
                      >
                        <option value="">Select a model (optional)</option>
                        <option v-for="model in machineModels" :key="model" :value="model">
                          {{ model }}
                        </option>
                      </select>
                    </div>
                  </div>
                </div>
              </div>
            </div>
            <div class="bg-gray-50 px-4 py-3 sm:px-6 sm:flex sm:flex-row-reverse">
              <button 
                type="submit"
                class="w-full inline-flex justify-center rounded-md border border-transparent shadow-sm px-4 py-2 bg-primary-600 text-base font-medium text-white hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500 sm:ml-3 sm:w-auto sm:text-sm"
              >
                {{ isEditing ? 'Update' : 'Add' }}
              </button>
              <button 
                type="button"
                @click="showModal = false"
                class="mt-3 w-full inline-flex justify-center rounded-md border border-gray-300 shadow-sm px-4 py-2 bg-white text-base font-medium text-gray-700 hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500 sm:mt-0 sm:ml-3 sm:w-auto sm:text-sm"
              >
                Cancel
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
    
    <!-- Delete Confirmation Modal -->
    <div v-if="showDeleteModal" class="fixed inset-0 overflow-y-auto" aria-labelledby="modal-title" role="dialog" aria-modal="true">
      <div class="flex items-end justify-center min-h-screen pt-4 px-4 pb-20 text-center sm:block sm:p-0">
        <div class="fixed inset-0 bg-gray-500 bg-opacity-75 transition-opacity" aria-hidden="true" @click="showDeleteModal = false"></div>
        
        <span class="hidden sm:inline-block sm:align-middle sm:h-screen" aria-hidden="true">&#8203;</span>
        
        <div class="inline-block align-bottom bg-white rounded-lg text-left overflow-hidden shadow-xl transform transition-all sm:my-8 sm:align-middle sm:max-w-lg sm:w-full">
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
                  Delete Machine
                </h3>
                <div class="mt-2">
                  <p class="text-sm text-gray-500">
                    Are you sure you want to delete the {{ machineToDelete?.name }} ({{ machineToDelete?.machine_type }})? This action cannot be undone.
                  </p>
                </div>
              </div>
            </div>
          </div>
          <div class="bg-gray-50 px-4 py-3 sm:px-6 sm:flex sm:flex-row-reverse">
            <button 
              type="button"
              @click="deleteMachine"
              class="w-full inline-flex justify-center rounded-md border border-transparent shadow-sm px-4 py-2 bg-red-600 text-base font-medium text-white hover:bg-red-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-red-500 sm:ml-3 sm:w-auto sm:text-sm"
            >
              Delete
            </button>
            <button 
              type="button"
              @click="showDeleteModal = false"
              class="mt-3 w-full inline-flex justify-center rounded-md border border-gray-300 shadow-sm px-4 py-2 bg-white text-base font-medium text-gray-700 hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500 sm:mt-0 sm:ml-3 sm:w-auto sm:text-sm"
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

const machines = ref([])
const locations = ref([])
const loading = ref(true)
const error = ref(null)
const locationInfo = ref({})
const locationNames = ref({})

// Filter state
const filters = ref({
  location: '',
  machineType: ''
})

// Group machines by location
const groupedMachines = computed(() => {
  const grouped = {}
  
  machines.value.forEach(machine => {
    if (!grouped[machine.location]) {
      grouped[machine.location] = []
    }
    grouped[machine.location].push(machine)
  })
  
  return grouped
})

// Machine models list
const machineModels = ref([
  '3D14',
  'AMS 39640',
  'AMS GB624',
  'AMS-LB9 Combo',
  'AP Snack Shop 111',
  'AP Snack Shop 133',
  'AP Snack Shop 152-D',
  'AP Snack Shop 6600',
  'AP Snack Shop III D20C',
  'AP Studio 3',
  'Crane 147',
  'Crane 148',
  'Crane 157',
  'Crane 158',
  'Crane 168',
  'Crane 172',
  'Crane 180',
  'Crane 181',
  'Crane 452',
  'Crane 784',
  'Dixie Narco',
  'Dixie Narco 276E',
  'Dixie Narco 348C',
  'Dixie Narco 368',
  'Dixie Narco 368 12',
  'Dixie Narco 368 R',
  'Dixie Narco 36812',
  'Dixie Narco 414 CC',
  'Dixie Narco 501-C',
  'Dixie Narco 501E',
  'ISI 3177',
  'Lektro Vending V599C Serie II',
  'Royal Vendor 390-9',
  'Royal Vendor 462-9',
  'Royal Vendor 550-6',
  'Royal Vendor 630-10',
  'Royal Vendor 650-10',
  'Royal Vendor 660',
  'Royal Vendor 660-8',
  'Royal Vendor 660-9',
  'Royal Vendor 804-',
  'Royal Vendor 804-13',
  'Royal Vendor 804-9',
  'Snack Mart 111 3000/Model: 301A',
  'Snack Shop 111',
  'Snack Shop 111 D206',
  'Snack Shop 113',
  'Snack Shop 6000',
  'Snack Shop 6600',
  'Snack Shop III 400 / Model:3014',
  'Snack Shop LCM2',
  'USA 3129',
  'USI 3014A',
  'USI 3166'
])

// Modal states
const showModal = ref(false)
const showDeleteModal = ref(false)
const isEditing = ref(false)
const machineToDelete = ref(null)

// Form for creating/editing a machine
const machineForm = ref({
  id: null,
  name: '',
  location: '',
  machine_type: '',
  model: ''
})

// Fetch all machines with filters
const fetchMachines = async () => {
  loading.value = true
  try {
    const params = {
      location: filters.value.location || undefined,
      machine_type: filters.value.machineType || undefined
    }
    
    const response = await api.getMachines(params)
    machines.value = response.data
  } catch (err) {
    console.error('Error fetching machines:', err)
    error.value = 'Failed to load machines. Please try again later.'
  } finally {
    loading.value = false
  }
}

// Fetch all locations for the dropdown and mapping
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

// Apply filters
const applyFilters = () => {
  fetchMachines()
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

// Open modal to add a new machine
const openAddModal = () => {
  isEditing.value = false
  machineForm.value = {
    id: null,
    name: '',
    location: '',
    machine_type: '',
    model: ''
  }
  showModal.value = true
}

// Open modal to edit an existing machine
const editMachine = (machine) => {
  isEditing.value = true
  machineForm.value = {
    id: machine.id,
    name: machine.name,
    location: machine.location,
    machine_type: machine.machine_type,
    model: machine.model
  }
  showModal.value = true
}

// Save the machine (create or update)
const saveMachine = async () => {
  try {
    if (isEditing.value) {
      await api.updateMachine(machineForm.value.id, machineForm.value)
    } else {
      await api.createMachine(machineForm.value)
    }
    
    showModal.value = false
    await fetchMachines()
  } catch (err) {
    console.error('Error saving machine:', err)
    error.value = 'Failed to save machine. Please try again.'
  }
}

// Show delete confirmation modal
const confirmDelete = (machine) => {
  machineToDelete.value = machine
  showDeleteModal.value = true
}

// Delete the machine
const deleteMachine = async () => {
  if (!machineToDelete.value) return
  
  try {
    await api.deleteMachine(machineToDelete.value.id)
    showDeleteModal.value = false
    await fetchMachines()
  } catch (err) {
    console.error('Error deleting machine:', err)
    error.value = 'Failed to delete machine. Please try again.'
  }
}

// Initialize data on component mount
onMounted(async () => {
  await Promise.all([fetchLocations(), fetchMachines()])
})
</script> 