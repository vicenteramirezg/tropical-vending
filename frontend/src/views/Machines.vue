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
    <MachineFilters
      :filters="filters"
      :locations="locations"
      :available-routes="availableRoutes"
      @filter-change="applyFilters"
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
    
    <!-- Empty State -->
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
    
    <!-- Machine List -->
    <MachineList
      v-else
      :grouped-machines="groupedMachines"
      :location-names="locationNames"
      :location-info="locationInfo"
      @open-map="openMapForLocation"
      @edit-machine="editMachine"
      @manage-products="manageProducts"
      @confirm-delete="confirmDelete"
    />
    
    <!-- Add/Edit Modal -->
    <MachineModal
      :show="showModal"
      :is-editing="isEditing"
      :machine-form="machineForm"
      :locations="locations"
      :machine-models="machineModels"
      @close="closeModal"
      @save="saveMachine"
    />
    
    <!-- Delete Confirmation Modal -->
    <DeleteConfirmationModal
      :show="showDeleteModal"
      :machine-to-delete="machineToDelete"
      @close="showDeleteModal = false"
      @confirm="deleteMachine"
    />
    
    <!-- Products Modal -->
    <MachineProductsModal
      :show="showProductsModal"
      :selected-machine="selectedMachine"
      :machine-products="machineProducts"
      :available-products="availableProducts"
      :product-form="productForm"
      :error="productError"
      @close="closeProductsModal"
      @add-product="addProductToMachine"
      @edit-price="editProductPrice"
      @update-price="updateProductPrice"
      @edit-slot="editProductSlot"
      @update-slot="updateProductSlot"
      @remove-product="removeProductFromMachine"
    />
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useMachines } from '../composables/useMachines'
import { useMachineProducts } from '../composables/useMachineProducts'
import { useMachineFilters } from '../composables/useMachineFilters'
import MachineFilters from '../components/machines/MachineFilters.vue'
import MachineList from '../components/machines/MachineList.vue'
import MachineModal from '../components/machines/MachineModal.vue'
import DeleteConfirmationModal from '../components/machines/DeleteConfirmationModal.vue'
import MachineProductsModal from '../components/machines/MachineProductsModal.vue'

// Composables
const {
  machines,
  loading,
  error,
  machineModels,
  groupedMachines,
  fetchMachines,
  createMachine,
  updateMachine,
  deleteMachine: deleteMachineApi,
  clearError
} = useMachines()

const {
  allProducts,
  machineProducts,
  productForm,
  availableProducts,
  error: productError,
  fetchAllProducts,
  fetchMachineProducts,
  addProductToMachine: addProductToMachineApi,
  updateProductPrice: updateProductPriceApi,
  updateProductSlot: updateProductSlotApi,
  removeProductFromMachine: removeProductFromMachineApi,
  editProductPrice: editProductPriceApi,
  editProductSlot: editProductSlotApi,
  resetState: resetProductState,
  clearError: clearProductError
} = useMachineProducts()

const {
  locations,
  availableRoutes,
  locationInfo,
  locationNames,
  filters,
  fetchLocations,
  fetchRoutes,
  openMapForLocation
} = useMachineFilters()

// Modal states
const showModal = ref(false)
const showDeleteModal = ref(false)
const showProductsModal = ref(false)
const isEditing = ref(false)
const machineToDelete = ref(null)
const selectedMachine = ref(null)

// Form for creating/editing a machine
const machineForm = ref({
  id: null,
  name: '',
  location: '',
  machine_type: '',
  model: ''
})

// Apply filters
const applyFilters = () => {
  fetchMachines(filters.value)
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

// Close modal
const closeModal = () => {
  showModal.value = false
  clearError()
}

// Save the machine (create or update)
const saveMachine = async (formData) => {
  let success = false
  
  if (isEditing.value) {
    success = await updateMachine(formData.id, formData)
  } else {
    success = await createMachine(formData)
  }
  
  if (success) {
    showModal.value = false
    await fetchMachines(filters.value)
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
  
  const success = await deleteMachineApi(machineToDelete.value.id)
  
  if (success) {
    showDeleteModal.value = false
    await fetchMachines(filters.value)
  }
}

// Open modal to manage products for a machine
const manageProducts = async (machine) => {
  selectedMachine.value = machine
  resetProductState()
  
  try {
    await fetchAllProducts()
    await fetchMachineProducts(machine.id)
    showProductsModal.value = true
  } catch (err) {
    console.error('Error opening products modal:', err)
  }
}

// Close products modal
const closeProductsModal = () => {
  showProductsModal.value = false
  resetProductState()
  selectedMachine.value = null
}

// Add product to machine
const addProductToMachine = async () => {
  if (!selectedMachine.value) return
  
  const success = await addProductToMachineApi(selectedMachine.value.id)
  
  if (success) {
    await fetchMachines(filters.value) // Refresh machines list to update product counts
  }
}

// Edit product price
const editProductPrice = (product) => {
  editProductPriceApi(product)
}

// Update product price
const updateProductPrice = async (product) => {
  if (!selectedMachine.value) return
  
  await updateProductPriceApi(product, selectedMachine.value.id)
}

// Edit product slot
const editProductSlot = (product) => {
  editProductSlotApi(product)
}

// Update product slot
const updateProductSlot = async (product) => {
  if (!selectedMachine.value) return
  
  await updateProductSlotApi(product, selectedMachine.value.id)
}

// Remove product from machine
const removeProductFromMachine = async (product) => {
  if (!confirm(`Are you sure you want to remove ${product.product_name} from this machine?`)) {
    return
  }
  
  if (!selectedMachine.value) return
  
  const success = await removeProductFromMachineApi(product, selectedMachine.value.id)
  
  if (success) {
    await fetchMachines(filters.value) // Refresh machines list to update product counts
  }
}

// Initialize data on component mount
onMounted(async () => {
  await Promise.all([fetchLocations(), fetchRoutes()])
  await fetchMachines()
})
</script> 