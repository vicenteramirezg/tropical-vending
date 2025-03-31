<template>
  <div>
    <div class="flex justify-between items-center mb-6">
      <h1 class="text-2xl font-semibold text-gray-900">Machines</h1>
      <button 
        @click="openAddModal" 
        class="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-primary-600 hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500"
      >
        Add Machine
      </button>
    </div>
    
    <div v-if="loading" class="flex justify-center">
      <div class="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-primary-500"></div>
    </div>
    
    <div v-else-if="error" class="bg-red-50 border-l-4 border-red-400 p-4 mb-4">
      <div class="flex">
        <div class="flex-shrink-0">
          <span class="text-red-400">⚠</span>
        </div>
        <div class="ml-3">
          <p class="text-sm text-red-700">{{ error }}</p>
        </div>
      </div>
    </div>
    
    <div v-else-if="machines.length === 0" class="bg-white shadow overflow-hidden sm:rounded-lg">
      <div class="px-4 py-5 sm:p-6 text-center">
        <h3 class="text-lg leading-6 font-medium text-gray-900">No machines found</h3>
        <div class="mt-2 max-w-xl text-sm text-gray-500">
          <p>Get started by adding your first machine.</p>
        </div>
        <div class="mt-5">
          <button
            @click="openAddModal"
            class="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-primary-600 hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500"
          >
            Add Machine
          </button>
        </div>
      </div>
    </div>
    
    <div v-else class="bg-white shadow overflow-hidden sm:rounded-lg">
      <ul role="list" class="divide-y divide-gray-200">
        <li v-for="machine in machines" :key="machine.id" class="px-4 py-4 sm:px-6">
          <div class="flex items-center justify-between">
            <div>
              <div class="flex items-center">
                <p class="text-sm font-medium text-primary-600 truncate">{{ machine.name }}</p>
                <p class="ml-2 text-sm text-gray-500">{{ machine.machine_type }}</p>
              </div>
              <p class="text-sm text-gray-500">Location: {{ machine.location_name }}</p>
              <p v-if="machine.model" class="text-sm text-gray-500">Model: {{ machine.model }}</p>
            </div>
            <div class="flex space-x-2">
              <button
                @click="editMachine(machine)"
                class="inline-flex items-center px-2.5 py-1.5 border border-gray-300 shadow-sm text-xs font-medium rounded text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500"
              >
                Edit
              </button>
              <button
                @click="confirmDelete(machine)"
                class="inline-flex items-center px-2.5 py-1.5 border border-gray-300 shadow-sm text-xs font-medium rounded text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-red-500"
              >
                Delete
              </button>
            </div>
          </div>
        </li>
      </ul>
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
import { ref, onMounted } from 'vue'
import { api } from '../services/api'

const machines = ref([])
const locations = ref([])
const loading = ref(true)
const error = ref(null)

// Machine models list
const machineModels = ref([
  'Dixie Narco 368 12',
  'AMS 39640',
  'Royal Vendor 650-10',
  'Snack Shop 6600',
  'Dixie Narco 501E',
  'Snack Shop LCM2',
  'Royal Vendor 630-10',
  'Royal Vendor 390-9',
  'Crane 181',
  'Royal Vendor 660-8',
  'Snack Shop 111',
  'Royal Vendor 804-9',
  'Crane 172',
  'Royal Vendor 660-9',
  'AMS-LB9 Combo',
  'Crane 784',
  'Crane 168',
  'USA 3129',
  '3D14',
  'AP Studio 3',
  'Royal Vendor 660-9',
  'Royal Vendor 804-13',
  'Crane 452',
  'Snack Mart 111 3000/Model: 301A',
  'Dixie Narco 368',
  'Crane 148',
  'Royal Vendor 462-9',
  'Royal Vendor 804-',
  'Royal Vendor 550-6',
  'AP Snack Shop 133',
  'AP Snack Shop 111',
  'Crane 157',
  'Lektro Vending V599C Serie II',
  'Dixie Narco',
  'Snack Shop III 400 / Model:3014',
  'Snack Shop 6000',
  'Crane 180',
  'USI 3014A',
  'Royal Vendor 660',
  'USI 3166',
  'AP Snack Shop 6600',
  'AP Snack Shop III D20C',
  'Dixie Narco 36812',
  'ISI 3177',
  'Dixie Narco 276E',
  'Snack Shop 113',
  'Dixie Narco 348C',
  'Crane 158',
  'AP Snack Shop 152-D',
  'Dixie Narco 414 CC',
  'AMS GB624',
  'Dixie Narco 368 R',
  'Dixie Narco 501-C',
  'Crane 147',
  'Snack Shop 111 D206'
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

// Fetch all machines
const fetchMachines = async () => {
  loading.value = true
  try {
    const response = await api.getMachines()
    machines.value = response.data
  } catch (err) {
    console.error('Error fetching machines:', err)
    error.value = 'Failed to load machines. Please try again later.'
  } finally {
    loading.value = false
  }
}

// Fetch all locations for the dropdown
const fetchLocations = async () => {
  try {
    const response = await api.getLocations()
    locations.value = response.data
  } catch (err) {
    console.error('Error fetching locations:', err)
    // We don't need to set error state here as it's a secondary operation
  }
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
  await Promise.all([fetchMachines(), fetchLocations()])
})
</script> 