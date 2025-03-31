<template>
  <div>
    <div class="flex justify-between items-center mb-6">
      <h1 class="text-2xl font-semibold text-gray-900">Restocks</h1>
      <button 
        @click="openAddModal" 
        class="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-primary-600 hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500"
      >
        Add Restock
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
    
    <div v-else-if="restocks.length === 0" class="bg-white shadow overflow-hidden sm:rounded-lg">
      <div class="px-4 py-5 sm:p-6 text-center">
        <h3 class="text-lg leading-6 font-medium text-gray-900">No restocks found</h3>
        <div class="mt-2 max-w-xl text-sm text-gray-500">
          <p>Get started by recording your first restock operation.</p>
        </div>
        <div class="mt-5">
          <button
            @click="openAddModal"
            class="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-primary-600 hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500"
          >
            Add Restock
          </button>
        </div>
      </div>
    </div>
    
    <div v-else class="bg-white shadow overflow-hidden sm:rounded-lg">
      <ul role="list" class="divide-y divide-gray-200">
        <li v-for="restock in restocks" :key="restock.id" class="px-4 py-4 sm:px-6">
          <div class="flex items-center justify-between">
            <div>
              <div class="flex items-center">
                <p class="text-sm font-medium text-primary-600">Visit: {{ formatDate(restock.visit.visit_date) }}</p>
                <span class="ml-2 px-2 inline-flex text-xs leading-5 font-semibold rounded-full bg-green-100 text-green-800">
                  {{ restock.entry_count }} items
                </span>
              </div>
              <div class="mt-1">
                <p class="text-sm text-gray-500">
                  Machine: {{ restock.machine.machine_type }} at {{ restock.machine.location_name }}
                </p>
              </div>
            </div>
            <div class="flex space-x-2">
              <button
                @click="viewDetails(restock)"
                class="inline-flex items-center px-2.5 py-1.5 border border-gray-300 shadow-sm text-xs font-medium rounded text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500"
              >
                Details
              </button>
              <button
                @click="editRestock(restock)"
                class="inline-flex items-center px-2.5 py-1.5 border border-gray-300 shadow-sm text-xs font-medium rounded text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500"
              >
                Edit
              </button>
              <button
                @click="confirmDelete(restock)"
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
          <form @submit.prevent="saveRestock">
            <div class="bg-white px-4 pt-5 pb-4 sm:p-6 sm:pb-4">
              <div class="sm:flex sm:items-start">
                <div class="mt-3 text-center sm:mt-0 sm:text-left w-full">
                  <h3 class="text-lg leading-6 font-medium text-gray-900" id="modal-title">
                    {{ isEditing ? 'Edit Restock' : 'Add New Restock' }}
                  </h3>
                  <div class="mt-4 space-y-4">
                    <div>
                      <label for="location" class="block text-sm font-medium text-gray-700">Location</label>
                      <select
                        id="location"
                        name="location"
                        v-model="selectedLocation"
                        @change="fetchLocationMachines"
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
                      <label for="machine" class="block text-sm font-medium text-gray-700">Machine</label>
                      <select
                        id="machine"
                        name="machine"
                        v-model="restockForm.machine"
                        class="mt-1 block w-full pl-3 pr-10 py-2 text-base border-gray-300 focus:outline-none focus:ring-primary-500 focus:border-primary-500 sm:text-sm rounded-md"
                        required
                        :disabled="!selectedLocation"
                      >
                        <option value="" disabled>{{ locationMachines.length ? 'Select a machine' : 'Select a location first' }}</option>
                        <option v-for="machine in locationMachines" :key="machine.id" :value="machine.id">
                          {{ machine.machine_type }} ({{ machine.model }})
                        </option>
                      </select>
                    </div>
                    
                    <div>
                      <label for="visit_date" class="block text-sm font-medium text-gray-700">Visit Date</label>
                      <input 
                        type="datetime-local" 
                        name="visit_date" 
                        id="visit_date" 
                        v-model="restockForm.visit_date"
                        class="mt-1 focus:ring-primary-500 focus:border-primary-500 block w-full shadow-sm sm:text-sm border-gray-300 rounded-md"
                        required
                      >
                    </div>
                    
                    <div>
                      <label for="notes" class="block text-sm font-medium text-gray-700">Notes</label>
                      <textarea 
                        id="notes" 
                        name="notes" 
                        rows="2" 
                        v-model="restockForm.notes"
                        class="shadow-sm focus:ring-primary-500 focus:border-primary-500 mt-1 block w-full sm:text-sm border border-gray-300 rounded-md"
                      ></textarea>
                    </div>
                    
                    <div v-if="restockItems.length > 0">
                      <label class="block text-sm font-medium text-gray-700 mb-2">Restock Items</label>
                      <div class="border border-gray-200 rounded-md overflow-hidden">
                        <div class="px-4 py-3 bg-gray-50 text-xs font-medium text-gray-500 uppercase tracking-wider">
                          <div class="grid grid-cols-6 gap-2">
                            <div class="col-span-3">Product</div>
                            <div class="col-span-1 text-center">Prev Qty</div>
                            <div class="col-span-1 text-center">Add</div>
                            <div class="col-span-1 text-center">New Qty</div>
                          </div>
                        </div>
                        <div class="divide-y divide-gray-200">
                          <div 
                            v-for="(item, index) in restockItems" 
                            :key="index" 
                            class="px-4 py-3"
                          >
                            <div class="grid grid-cols-6 gap-2 items-center">
                              <div class="col-span-3 text-sm font-medium text-gray-900">
                                {{ item.product_name }}
                              </div>
                              <div class="col-span-1 text-center text-sm text-gray-500">
                                {{ item.current_quantity }}
                              </div>
                              <div class="col-span-1">
                                <input 
                                  type="number" 
                                  v-model="item.quantity_added" 
                                  min="0" 
                                  class="block w-full border-gray-300 rounded-md shadow-sm focus:ring-primary-500 focus:border-primary-500 sm:text-sm"
                                >
                              </div>
                              <div class="col-span-1 text-center text-sm font-medium text-gray-900">
                                {{ item.current_quantity + (parseInt(item.quantity_added) || 0) }}
                              </div>
                            </div>
                          </div>
                        </div>
                      </div>
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
    
    <!-- View Details Modal -->
    <div v-if="showDetailsModal" class="fixed inset-0 overflow-y-auto" aria-labelledby="modal-title" role="dialog" aria-modal="true">
      <div class="flex items-end justify-center min-h-screen pt-4 px-4 pb-20 text-center sm:block sm:p-0">
        <div class="fixed inset-0 bg-gray-500 bg-opacity-75 transition-opacity" aria-hidden="true" @click="showDetailsModal = false"></div>
        
        <span class="hidden sm:inline-block sm:align-middle sm:h-screen" aria-hidden="true">&#8203;</span>
        
        <div class="inline-block align-bottom bg-white rounded-lg text-left overflow-hidden shadow-xl transform transition-all sm:my-8 sm:align-middle sm:max-w-lg sm:w-full">
          <div class="bg-white px-4 pt-5 pb-4 sm:p-6 sm:pb-4">
            <div class="sm:flex sm:items-start">
              <div class="mt-3 text-center sm:mt-0 sm:text-left w-full">
                <h3 class="text-lg leading-6 font-medium text-gray-900" id="modal-title">
                  Restock Details
                </h3>
                <div class="mt-4">
                  <dl class="grid grid-cols-1 gap-x-4 gap-y-6 sm:grid-cols-2">
                    <div class="sm:col-span-1">
                      <dt class="text-sm font-medium text-gray-500">Location</dt>
                      <dd class="mt-1 text-sm text-gray-900">{{ selectedRestock?.machine?.location_name }}</dd>
                    </div>
                    <div class="sm:col-span-1">
                      <dt class="text-sm font-medium text-gray-500">Machine</dt>
                      <dd class="mt-1 text-sm text-gray-900">{{ selectedRestock?.machine?.machine_type }}</dd>
                    </div>
                    <div class="sm:col-span-1">
                      <dt class="text-sm font-medium text-gray-500">Visit Date</dt>
                      <dd class="mt-1 text-sm text-gray-900">{{ formatDate(selectedRestock?.visit?.visit_date) }}</dd>
                    </div>
                    <div class="sm:col-span-1">
                      <dt class="text-sm font-medium text-gray-500">Restocked By</dt>
                      <dd class="mt-1 text-sm text-gray-900">{{ selectedRestock?.visit?.user_name }}</dd>
                    </div>
                    <div class="sm:col-span-2">
                      <dt class="text-sm font-medium text-gray-500">Notes</dt>
                      <dd class="mt-1 text-sm text-gray-900">{{ selectedRestock?.visit?.notes || 'No notes' }}</dd>
                    </div>
                  </dl>
                  
                  <div class="mt-6">
                    <h4 class="text-sm font-medium text-gray-500">Restocked Items</h4>
                    <div class="mt-2 border border-gray-200 rounded-md overflow-hidden">
                      <div class="px-4 py-3 bg-gray-50 text-xs font-medium text-gray-500 uppercase tracking-wider">
                        <div class="grid grid-cols-5 gap-2">
                          <div class="col-span-2">Product</div>
                          <div class="col-span-1 text-center">Prev Qty</div>
                          <div class="col-span-1 text-center">Added</div>
                          <div class="col-span-1 text-center">New Qty</div>
                        </div>
                      </div>
                      <div class="divide-y divide-gray-200">
                        <div 
                          v-for="entry in selectedRestock?.entries" 
                          :key="entry.id" 
                          class="px-4 py-3"
                        >
                          <div class="grid grid-cols-5 gap-2 items-center">
                            <div class="col-span-2 text-sm font-medium text-gray-900">
                              {{ entry.product_name }}
                            </div>
                            <div class="col-span-1 text-center text-sm text-gray-500">
                              {{ entry.previous_quantity }}
                            </div>
                            <div class="col-span-1 text-center text-sm text-green-600 font-medium">
                              +{{ entry.quantity_added }}
                            </div>
                            <div class="col-span-1 text-center text-sm font-medium text-gray-900">
                              {{ entry.previous_quantity + entry.quantity_added }}
                            </div>
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
          <div class="bg-gray-50 px-4 py-3 sm:px-6 sm:flex sm:flex-row-reverse">
            <button 
              type="button"
              @click="showDetailsModal = false"
              class="w-full inline-flex justify-center rounded-md border border-gray-300 shadow-sm px-4 py-2 bg-white text-base font-medium text-gray-700 hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500 sm:w-auto sm:text-sm"
            >
              Close
            </button>
          </div>
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
                  Delete Restock
                </h3>
                <div class="mt-2">
                  <p class="text-sm text-gray-500">
                    Are you sure you want to delete this restock record? This action cannot be undone.
                  </p>
                </div>
              </div>
            </div>
          </div>
          <div class="bg-gray-50 px-4 py-3 sm:px-6 sm:flex sm:flex-row-reverse">
            <button 
              type="button"
              @click="deleteRestock"
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

const restocks = ref([])
const locations = ref([])
const locationMachines = ref([])
const restockItems = ref([])
const loading = ref(true)
const error = ref(null)

// Modal states
const showModal = ref(false)
const showDetailsModal = ref(false)
const showDeleteModal = ref(false)
const isEditing = ref(false)
const selectedRestock = ref(null)
const selectedLocation = ref('')

// Form for creating/editing a restock
const restockForm = ref({
  id: null,
  machine: '',
  visit_date: '',
  notes: '',
  entries: []
})

// Format date for display
const formatDate = (dateString) => {
  if (!dateString) return ''
  const date = new Date(dateString)
  return date.toLocaleString()
}

// Fetch all restocks
const fetchRestocks = async () => {
  loading.value = true
  try {
    const response = await api.getRestocks()
    restocks.value = response.data
  } catch (err) {
    console.error('Error fetching restocks:', err)
    error.value = 'Failed to load restocks. Please try again later.'
  } finally {
    loading.value = false
  }
}

// Fetch all locations
const fetchLocations = async () => {
  try {
    const response = await api.getLocations()
    locations.value = response.data
  } catch (err) {
    console.error('Error fetching locations:', err)
  }
}

// Fetch machines for selected location
const fetchLocationMachines = async () => {
  if (!selectedLocation.value) {
    locationMachines.value = []
    return
  }
  
  try {
    const response = await api.getMachines({ location: selectedLocation.value })
    locationMachines.value = response.data
    restockForm.value.machine = ''
    restockItems.value = []
  } catch (err) {
    console.error('Error fetching machines:', err)
  }
}

// Fetch machine items for selected machine
const fetchMachineItems = async () => {
  if (!restockForm.value.machine) {
    restockItems.value = []
    return
  }
  
  try {
    const response = await api.getMachineItems({ machine: restockForm.value.machine })
    restockItems.value = response.data.map(item => ({
      machine_item_id: item.id,
      product_id: item.product,
      product_name: item.product_name,
      current_quantity: item.current_quantity,
      quantity_added: 0
    }))
  } catch (err) {
    console.error('Error fetching machine items:', err)
  }
}

// Reset form and open modal
const openAddModal = () => {
  isEditing.value = false
  selectedLocation.value = ''
  locationMachines.value = []
  restockItems.value = []
  
  // Set default visit date to now
  const now = new Date()
  const year = now.getFullYear()
  const month = String(now.getMonth() + 1).padStart(2, '0')
  const day = String(now.getDate()).padStart(2, '0')
  const hours = String(now.getHours()).padStart(2, '0')
  const minutes = String(now.getMinutes()).padStart(2, '0')
  
  restockForm.value = {
    id: null,
    machine: '',
    visit_date: `${year}-${month}-${day}T${hours}:${minutes}`,
    notes: '',
    entries: []
  }
  
  showModal.value = true
}

// Open modal with restock details
const viewDetails = (restock) => {
  selectedRestock.value = restock
  showDetailsModal.value = true
}

// Open modal to edit an existing restock (simplified for demo)
const editRestock = (restock) => {
  isEditing.value = true
  selectedRestock.value = restock
  
  // In a real app, you would need to fetch the detailed restock data
  // and populate the form properly
  
  // This is simplified for the example - in a real app you would
  // need to handle this more thoroughly
  alert('Editing restocks is complex and not fully implemented in this demo')
}

// Save the restock (create or update)
const saveRestock = async () => {
  try {
    // Prepare entries data
    const entries = restockItems.value
      .filter(item => parseInt(item.quantity_added) > 0)
      .map(item => ({
        machine_item: item.machine_item_id,
        quantity_added: parseInt(item.quantity_added)
      }))
    
    if (entries.length === 0) {
      error.value = 'Please add at least one restock entry'
      return
    }
    
    const payload = {
      machine: restockForm.value.machine,
      visit_date: restockForm.value.visit_date,
      notes: restockForm.value.notes,
      entries: entries
    }
    
    if (isEditing.value) {
      await api.updateRestock(restockForm.value.id, payload)
    } else {
      await api.createRestock(payload)
    }
    
    showModal.value = false
    await fetchRestocks()
  } catch (err) {
    console.error('Error saving restock:', err)
    error.value = 'Failed to save restock. Please try again.'
  }
}

// Show delete confirmation modal
const confirmDelete = (restock) => {
  selectedRestock.value = restock
  showDeleteModal.value = true
}

// Delete the restock
const deleteRestock = async () => {
  if (!selectedRestock.value) return
  
  try {
    await api.deleteRestock(selectedRestock.value.id)
    showDeleteModal.value = false
    await fetchRestocks()
  } catch (err) {
    console.error('Error deleting restock:', err)
    error.value = 'Failed to delete restock. Please try again.'
  }
}

// Watch for machine changes to fetch items
const watchMachine = computed(() => restockForm.value.machine)
import { watch } from 'vue'

watch(watchMachine, (newVal) => {
  if (newVal) {
    fetchMachineItems()
  }
})

// Initialize data on component mount
onMounted(async () => {
  await Promise.all([fetchRestocks(), fetchLocations()])
})
</script> 