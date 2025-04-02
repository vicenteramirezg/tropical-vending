<template>
  <div>
    <div class="flex justify-between items-center mb-6">
      <h1 class="text-2xl font-semibold text-gray-900">Location Visits</h1>
      <button 
        @click="openAddModal" 
        class="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-primary-600 hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500"
      >
        Record New Visit
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
        <h3 class="text-lg leading-6 font-medium text-gray-900">No visits recorded</h3>
        <div class="mt-2 max-w-xl text-sm text-gray-500">
          <p>Get started by recording your first location visit.</p>
        </div>
        <div class="mt-5">
          <button
            @click="openAddModal"
            class="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-primary-600 hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500"
          >
            Record New Visit
          </button>
        </div>
      </div>
    </div>
    
    <div v-else class="bg-white shadow overflow-hidden sm:rounded-lg">
      <ul role="list" class="divide-y divide-gray-200">
        <li v-for="restock in restocks" :key="restock.id" class="px-4 py-4 sm:px-6">
          <div class="flex items-center justify-between">
            <div class="flex-1 min-w-0">
              <p class="text-sm font-medium text-primary-600 truncate">
                {{ restock.location_name }}
              </p>
              <p class="text-sm text-gray-500">
                {{ formatDate(restock.visit_date) }}
              </p>
            </div>
            <div class="ml-4 flex-shrink-0 flex space-x-2">
              <button
                @click="viewDetails(restock)"
                class="inline-flex items-center px-3 py-1 border border-gray-300 shadow-sm text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500"
              >
                View Details
              </button>
              <button
                @click="editRestock(restock)"
                class="inline-flex items-center px-3 py-1 border border-transparent text-sm font-medium rounded-md text-white bg-primary-600 hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500"
              >
                Edit
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
        
        <div class="inline-block align-bottom bg-white rounded-lg text-left overflow-hidden shadow-xl transform transition-all sm:my-8 sm:align-middle sm:max-w-4xl sm:w-full">
          <form @submit.prevent="saveRestock">
            <div class="bg-white px-4 pt-5 pb-4 sm:p-6 sm:pb-4">
              <div class="sm:flex sm:items-start">
                <div class="mt-3 text-center sm:mt-0 sm:text-left w-full">
                  <h3 class="text-lg leading-6 font-medium text-gray-900" id="modal-title">
                    {{ isEditing ? 'Edit Visit' : 'Record New Visit' }}
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

                    <div v-if="locationMachines.length > 0">
                      <h4 class="text-sm font-medium text-gray-700 mb-2">Machines at Location</h4>
                      <div class="space-y-4">
                        <div v-for="machine in locationMachines" :key="machine.id" class="border rounded-lg p-4">
                          <div class="flex justify-between items-center mb-2">
                            <h5 class="text-sm font-medium text-gray-900">
                              {{ machine.machine_type }} ({{ machine.model }})
                            </h5>
                            <div class="text-sm text-gray-500">
                              {{ machine.products.length }} products
                            </div>
                          </div>
                          
                          <div class="space-y-2">
                            <div v-if="machine.products.length === 0" class="text-sm text-gray-500 italic p-2 text-center">
                              No products in this machine
                            </div>
                            <div v-for="product in machine.products" :key="product.id" class="grid grid-cols-4 gap-4 items-center">
                              <div class="col-span-1 text-sm font-medium text-gray-900">
                                {{ product.name }}
                              </div>
                              <div class="col-span-1">
                                <label class="block text-xs text-gray-500">Current Stock</label>
                                <div class="mt-1 flex rounded-md shadow-sm">
                                  <button 
                                    type="button"
                                    @click="product.stock_before = Math.max(0, (parseInt(product.stock_before) || 0) - 1)"
                                    class="relative inline-flex items-center px-2 py-2 rounded-l-md border border-gray-300 bg-white text-sm font-medium text-gray-500 hover:bg-gray-50"
                                  >
                                    <span class="sr-only">Decrease</span>
                                    -
                                  </button>
                                  <input 
                                    type="number" 
                                    v-model="product.stock_before"
                                    min="0"
                                    class="focus:ring-primary-500 focus:border-primary-500 block w-full border-gray-300 rounded-none text-center sm:text-sm"
                                    required
                                  >
                                  <button 
                                    type="button"
                                    @click="product.stock_before = (parseInt(product.stock_before) || 0) + 1"
                                    class="relative inline-flex items-center px-2 py-2 rounded-r-md border border-gray-300 bg-white text-sm font-medium text-gray-500 hover:bg-gray-50"
                                  >
                                    <span class="sr-only">Increase</span>
                                    +
                                  </button>
                                </div>
                              </div>
                              <div class="col-span-1">
                                <label class="block text-xs text-gray-500">Discarded Amount</label>
                                <div class="mt-1 flex rounded-md shadow-sm">
                                  <button 
                                    type="button"
                                    @click="product.discarded = Math.max(0, (parseInt(product.discarded) || 0) - 1)"
                                    class="relative inline-flex items-center px-2 py-2 rounded-l-md border border-gray-300 bg-white text-sm font-medium text-gray-500 hover:bg-gray-50"
                                  >
                                    <span class="sr-only">Decrease</span>
                                    -
                                  </button>
                                  <input 
                                    type="number" 
                                    v-model="product.discarded"
                                    min="0"
                                    class="focus:ring-primary-500 focus:border-primary-500 block w-full border-gray-300 rounded-none text-center sm:text-sm"
                                    required
                                  >
                                  <button 
                                    type="button"
                                    @click="product.discarded = (parseInt(product.discarded) || 0) + 1"
                                    class="relative inline-flex items-center px-2 py-2 rounded-r-md border border-gray-300 bg-white text-sm font-medium text-gray-500 hover:bg-gray-50"
                                  >
                                    <span class="sr-only">Increase</span>
                                    +
                                  </button>
                                </div>
                              </div>
                              <div class="col-span-1">
                                <label class="block text-xs text-gray-500">Restock Amount</label>
                                <div class="mt-1 flex rounded-md shadow-sm">
                                  <button 
                                    type="button"
                                    @click="product.restocked = Math.max(0, (parseInt(product.restocked) || 0) - 1)"
                                    class="relative inline-flex items-center px-2 py-2 rounded-l-md border border-gray-300 bg-white text-sm font-medium text-gray-500 hover:bg-gray-50"
                                  >
                                    <span class="sr-only">Decrease</span>
                                    -
                                  </button>
                                  <input 
                                    type="number" 
                                    v-model="product.restocked"
                                    min="0"
                                    class="focus:ring-primary-500 focus:border-primary-500 block w-full border-gray-300 rounded-none text-center sm:text-sm"
                                    required
                                  >
                                  <button 
                                    type="button"
                                    @click="product.restocked = (parseInt(product.restocked) || 0) + 1"
                                    class="relative inline-flex items-center px-2 py-2 rounded-r-md border border-gray-300 bg-white text-sm font-medium text-gray-500 hover:bg-gray-50"
                                  >
                                    <span class="sr-only">Increase</span>
                                    +
                                  </button>
                                </div>
                              </div>
                              <div class="col-span-1 text-sm text-gray-500">
                                New Total: {{ (parseInt(product.stock_before) || 0) - (parseInt(product.discarded) || 0) + (parseInt(product.restocked) || 0) }}
                              </div>
                            </div>
                          </div>
                        </div>
                      </div>
                    </div>
                    
                    <div>
                      <label for="notes" class="block text-sm font-medium text-gray-700">Visit Notes</label>
                      <textarea 
                        id="notes" 
                        name="notes" 
                        rows="2" 
                        v-model="restockForm.notes"
                        class="shadow-sm focus:ring-primary-500 focus:border-primary-500 mt-1 block w-full sm:text-sm border border-gray-300 rounded-md"
                      ></textarea>
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
                Save Visit
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
                      <dd class="mt-1 text-sm text-gray-900">{{ selectedRestock?.location_name }}</dd>
                    </div>
                    <div class="sm:col-span-1">
                      <dt class="text-sm font-medium text-gray-500">Visit Date</dt>
                      <dd class="mt-1 text-sm text-gray-900">{{ formatDate(selectedRestock?.visit_date) }}</dd>
                    </div>
                    <div class="sm:col-span-1">
                      <dt class="text-sm font-medium text-gray-500">Restocked By</dt>
                      <dd class="mt-1 text-sm text-gray-900">{{ selectedRestock?.user_name }}</dd>
                    </div>
                    <div class="sm:col-span-2">
                      <dt class="text-sm font-medium text-gray-500">Notes</dt>
                      <dd class="mt-1 text-sm text-gray-900">{{ selectedRestock?.notes || 'No notes' }}</dd>
                    </div>
                  </dl>
                  
                  <div class="mt-6">
                    <h4 class="text-sm font-medium text-gray-500">Restocked Items</h4>
                    <div class="mt-2 border border-gray-200 rounded-md overflow-hidden">
                      <div class="px-4 py-3 bg-gray-50 text-xs font-medium text-gray-500 uppercase tracking-wider">
                        <div class="grid grid-cols-5 gap-2">
                          <div class="col-span-2">Product</div>
                          <div class="col-span-1 text-center">Prev Qty</div>
                          <div class="col-span-1 text-center">Discarded</div>
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
                            <div class="col-span-1 text-center text-sm text-gray-500">
                              {{ entry.quantity_discarded }}
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
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { api } from '../services/api'
import { useAuthStore } from '../store/auth'

// Add auth store reference
const authStore = useAuthStore()

const restocks = ref([])
const locations = ref([])
const locationMachines = ref([])
const loading = ref(true)
const error = ref(null)

// Modal states
const showModal = ref(false)
const showDetailsModal = ref(false)
const isEditing = ref(false)
const selectedRestock = ref(null)
const selectedLocation = ref('')

// Form for creating/editing a restock
const restockForm = ref({
  id: null,
  visit_date: '',
  notes: '',
  location: '',
  machines: []
})

// Format date for display
const formatDate = (dateString) => {
  if (!dateString) return ''
  const date = new Date(dateString)
  return date.toLocaleString()
}

// Fetch all visits (formerly restocks)
const fetchRestocks = async () => {
  loading.value = true
  try {
    const response = await api.getVisits()
    restocks.value = response.data.map(visit => ({
      id: visit.id,
      location_id: visit.location,
      location_name: visit.location_name,
      visit_date: visit.visit_date,
      notes: visit.notes,
      user_name: visit.user_name
    }))
  } catch (err) {
    console.error('Error fetching visits:', err)
    error.value = 'Failed to load visits. Please try again later.'
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

// Fetch machines and their products for selected location
const fetchLocationMachines = async () => {
  if (!selectedLocation.value) {
    locationMachines.value = []
    return
  }
  
  try {
    // First fetch machines for the location
    const machinesResponse = await api.getMachines({ location: selectedLocation.value })
    const machines = machinesResponse.data
    
    // Then fetch the machine items (products) for each machine
    const machinesWithProducts = []
    
    for (const machine of machines) {
      // Get products for this machine
      const itemsResponse = await api.getMachineItems({ machine: machine.id })
      const products = itemsResponse.data.map(item => ({
        id: item.product,
        name: item.product_name,
        price: item.price,
        current_stock: item.current_stock || 0,
        stock_before: item.current_stock || 0,
        discarded: 0,
        restocked: 0
      }))
      
      machinesWithProducts.push({
        ...machine,
        products: products
      })
    }
    
    locationMachines.value = machinesWithProducts
  } catch (err) {
    console.error('Error fetching machines and products:', err)
    error.value = 'Failed to load machine products. Please try again.'
  }
}

// Reset form and open modal
const openAddModal = () => {
  isEditing.value = false
  selectedRestock.value = null
  selectedLocation.value = ''
  locationMachines.value = []
  restockForm.value = {
    id: null,
    visit_date: new Date().toISOString().slice(0, 16),
    notes: '',
    location: '',
    machines: []
  }
  showModal.value = true
}

// Edit existing restock
const editRestock = async (restock) => {
  isEditing.value = true
  selectedRestock.value = restock
  selectedLocation.value = restock.location_id
  
  restockForm.value = {
    id: restock.id,
    visit_date: restock.visit_date,
    notes: restock.notes,
    location: restock.location_id
  }
  
  // Fetch machines for this location first
  await fetchLocationMachines()
  
  try {
    // Fetch the machine restocks for this visit
    const machineRestocksResponse = await api.getRestocks({ visit: restock.id })
    const machineRestocks = machineRestocksResponse.data
    
    // Fetch entries for each machine restock and update the machines
    for (const machineRestock of machineRestocks) {
      const entriesResponse = await api.getRestockEntries({ visit_machine_restock: machineRestock.id })
      const entries = entriesResponse.data
      
      // Find the machine in locationMachines and update its products
      const machineIndex = locationMachines.value.findIndex(m => m.id === machineRestock.machine)
      
      if (machineIndex !== -1) {
        // Update each product with the restock entry data
        const machine = locationMachines.value[machineIndex]
        
        entries.forEach(entry => {
          const productIndex = machine.products.findIndex(p => p.id === entry.product)
          
          if (productIndex !== -1) {
            machine.products[productIndex].stock_before = entry.stock_before
            machine.products[productIndex].discarded = entry.discarded || 0
            machine.products[productIndex].restocked = entry.restocked
          }
        })
      }
    }
    
    showModal.value = true
  } catch (err) {
    console.error('Error loading visit for editing:', err)
    error.value = 'Failed to load visit details for editing. Please try again.'
  }
}

// View restock details
const viewDetails = async (restock) => {
  selectedRestock.value = restock
  
  try {
    // Fetch the machine restocks for this visit
    const machineRestocksResponse = await api.getRestocks({ visit: restock.id })
    const machineRestocks = machineRestocksResponse.data
    
    // Fetch entries for each machine restock
    const entries = []
    
    for (const machineRestock of machineRestocks) {
      const entriesResponse = await api.getRestockEntries({ visit_machine_restock: machineRestock.id })
      entries.push(...entriesResponse.data)
    }
    
    // Combine the data
    selectedRestock.value = {
      ...restock,
      entries: entries.map(entry => ({
        id: entry.id,
        product_name: entry.product_name,
        product_id: entry.product,
        previous_quantity: entry.stock_before,
        quantity_discarded: entry.discarded,
        quantity_added: entry.restocked,
        machine_info: entry.machine_info
      }))
    }
    
    showDetailsModal.value = true
  } catch (err) {
    console.error('Error fetching visit details:', err)
    error.value = 'Failed to load visit details. Please try again.'
  }
}

// Save the restock
const saveRestock = async () => {
  try {
    // Validate that all products have stock levels recorded
    const hasEmptyFields = locationMachines.value.some(machine => 
      machine.products.some(product => 
        product.stock_before === '' || product.restocked === ''
      )
    )
    
    if (hasEmptyFields) {
      error.value = 'Please record stock levels for all products in all machines'
      return
    }
    
    // First create/update the Visit
    let visitId
    
    const visitData = {
      location: selectedLocation.value,
      visit_date: restockForm.value.visit_date,
      notes: restockForm.value.notes,
      user: authStore.user?.id  // Add user ID from auth store
    }
    
    console.log('Saving visit with data:', visitData)
    
    if (isEditing.value && restockForm.value.id) {
      // If editing, update the visit
      const visitResponse = await api.updateVisit(restockForm.value.id, visitData)
      visitId = visitResponse.data.id
    } else {
      // Create a new visit
      const visitResponse = await api.createVisit(visitData)
      visitId = visitResponse.data.id
    }
    
    // Process each machine restock
    for (const machine of locationMachines.value) {
      let visitMachineRestockId;
      
      if (isEditing.value) {
        // When editing, look for an existing restock for this machine
        try {
          const existingRestocksResponse = await api.getRestocks({ 
            visit: visitId,
            machine: machine.id 
          });
          
          if (existingRestocksResponse.data.length > 0) {
            // Update the existing restock
            const existingRestock = existingRestocksResponse.data[0];
            const restockData = {
              visit: visitId,
              machine: machine.id,
              notes: existingRestock.notes || ''
            };
            
            await api.updateRestock(existingRestock.id, restockData);
            visitMachineRestockId = existingRestock.id;
          } else {
            // Create a new restock if none exists for this machine
            const restockData = {
              visit: visitId,
              machine: machine.id,
              notes: ''
            };
            
            const machineRestockResponse = await api.createRestock(restockData);
            visitMachineRestockId = machineRestockResponse.data.id;
          }
        } catch (err) {
          console.error('Error handling machine restock:', err);
          throw err;
        }
      } else {
        // Creating a new visit, so create new restocks
        const restockData = {
          visit: visitId,
          machine: machine.id,
          notes: ''
        };
        
        const machineRestockResponse = await api.createRestock(restockData);
        visitMachineRestockId = machineRestockResponse.data.id;
      }
      
      // Process restock entries for each product
      for (const product of machine.products) {
        try {
          // For editing, check if an entry already exists
          if (isEditing.value) {
            const existingEntriesResponse = await api.getRestockEntries({
              visit_machine_restock: visitMachineRestockId,
              product: product.id
            });
            
            const restockEntryData = {
              visit_machine_restock: visitMachineRestockId,
              product: product.id,
              stock_before: parseInt(product.stock_before) || 0,
              discarded: parseInt(product.discarded) || 0,
              restocked: parseInt(product.restocked) || 0
            };
            
            if (existingEntriesResponse.data.length > 0) {
              // Update existing entry
              await api.updateRestockEntry(existingEntriesResponse.data[0].id, restockEntryData);
            } else {
              // Create new entry
              await api.createRestockEntry(restockEntryData);
            }
          } else {
            // For new visits, always create new entries
            const restockEntryData = {
              visit_machine_restock: visitMachineRestockId,
              product: product.id,
              stock_before: parseInt(product.stock_before) || 0,
              discarded: parseInt(product.discarded) || 0,
              restocked: parseInt(product.restocked) || 0
            };
            
            await api.createRestockEntry(restockEntryData);
          }
        } catch (err) {
          console.error('Error handling restock entry:', err);
          throw err;
        }
      }
    }
    
    showModal.value = false
    await fetchRestocks()
  } catch (err) {
    console.error('Error saving restock visit:', err)
    error.value = 'Failed to save visit. Please try again.'
  }
}

// Initialize data on component mount
onMounted(async () => {
  // Make sure user data is loaded if we're authenticated but don't have user info
  if (authStore.isAuthenticated && !authStore.user) {
    await authStore.fetchUser()
  }
  
  // Log the current user to help with debugging
  console.log('Current user:', authStore.user)
  
  await Promise.all([fetchRestocks(), fetchLocations()])
})
</script> 