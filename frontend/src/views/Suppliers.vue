<template>
  <div>
    <div class="flex justify-between items-center mb-6">
      <h1 class="text-2xl font-semibold text-gray-900">Suppliers</h1>
      <button 
        @click="openAddModal" 
        class="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-primary-600 hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500"
      >
        <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
        </svg>
        Add Supplier
      </button>
    </div>
    
    <!-- Filters -->
    <div class="mb-6 bg-white shadow-sm rounded-lg p-4">
      <div class="flex flex-wrap gap-4 items-center">
        <div class="flex-1 min-w-64">
          <label for="search" class="sr-only">Search suppliers</label>
          <div class="relative">
            <div class="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
              <svg class="h-5 w-5 text-gray-400" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
              </svg>
            </div>
            <input 
              id="search"
              v-model="searchTerm"
              type="search" 
              placeholder="Search suppliers..." 
              class="block w-full pl-10 pr-3 py-2 border border-gray-300 rounded-md leading-5 bg-white placeholder-gray-500 focus:outline-none focus:placeholder-gray-400 focus:ring-1 focus:ring-primary-500 focus:border-primary-500 sm:text-sm"
            >
          </div>
        </div>
        <div class="flex items-center space-x-4">
          <div class="flex items-center">
            <input 
              id="show-active"
              v-model="showActive"
              type="checkbox"
              class="h-4 w-4 text-primary-600 focus:ring-primary-500 border-gray-300 rounded"
            >
            <label for="show-active" class="ml-2 block text-sm text-gray-900">
              Active only
            </label>
          </div>
          <div class="flex items-center">
            <input 
              id="show-inactive"
              v-model="showInactive"
              type="checkbox"
              class="h-4 w-4 text-primary-600 focus:ring-primary-500 border-gray-300 rounded"
            >
            <label for="show-inactive" class="ml-2 block text-sm text-gray-900">
              Inactive only
            </label>
          </div>
        </div>
      </div>
    </div>
    
    <!-- Stats Cards -->
    <div class="grid grid-cols-1 md:grid-cols-3 gap-6 mb-6">
      <div class="bg-white overflow-hidden shadow rounded-lg">
        <div class="p-5">
          <div class="flex items-center">
            <div class="flex-shrink-0">
              <svg class="h-6 w-6 text-gray-400" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4" />
              </svg>
            </div>
            <div class="ml-5 w-0 flex-1">
              <dl>
                <dt class="text-sm font-medium text-gray-500 truncate">Total Suppliers</dt>
                <dd class="text-lg font-medium text-gray-900">{{ supplierCount }}</dd>
              </dl>
            </div>
          </div>
        </div>
      </div>
      
      <div class="bg-white overflow-hidden shadow rounded-lg">
        <div class="p-5">
          <div class="flex items-center">
            <div class="flex-shrink-0">
              <svg class="h-6 w-6 text-green-400" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
            </div>
            <div class="ml-5 w-0 flex-1">
              <dl>
                <dt class="text-sm font-medium text-gray-500 truncate">Active Suppliers</dt>
                <dd class="text-lg font-medium text-gray-900">{{ activeSuppliers.length }}</dd>
              </dl>
            </div>
          </div>
        </div>
      </div>
      
      <div class="bg-white overflow-hidden shadow rounded-lg">
        <div class="p-5">
          <div class="flex items-center">
            <div class="flex-shrink-0">
              <svg class="h-6 w-6 text-gray-400" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M18.364 18.364A9 9 0 005.636 5.636m12.728 12.728L5.636 5.636m12.728 12.728L18.364 5.636M5.636 18.364l12.728-12.728" />
              </svg>
            </div>
            <div class="ml-5 w-0 flex-1">
              <dl>
                <dt class="text-sm font-medium text-gray-500 truncate">Inactive Suppliers</dt>
                <dd class="text-lg font-medium text-gray-900">{{ inactiveSuppliers.length }}</dd>
              </dl>
            </div>
          </div>
        </div>
      </div>
    </div>
    
    <!-- Error Message -->
    <div v-if="error" class="mb-6 bg-red-50 border border-red-200 rounded-md p-4">
      <div class="flex">
        <div class="flex-shrink-0">
          <svg class="h-5 w-5 text-red-400" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor">
            <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clip-rule="evenodd" />
          </svg>
        </div>
        <div class="ml-3">
          <p class="text-sm text-red-800">{{ error }}</p>
        </div>
      </div>
    </div>
    
    <!-- Loading State -->
    <div v-if="loading" class="flex justify-center items-center py-12">
      <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600"></div>
      <span class="ml-2 text-gray-600">Loading suppliers...</span>
    </div>
    
    <!-- Empty State -->
    <div v-else-if="filteredSuppliers.length === 0" class="text-center py-12">
      <svg class="mx-auto h-12 w-12 text-gray-400" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4" />
      </svg>
      <h3 class="mt-2 text-sm font-medium text-gray-900">No suppliers found</h3>
      <p class="mt-1 text-sm text-gray-500">
        {{ searchTerm ? 'Try adjusting your search terms.' : 'Get started by adding a new supplier.' }}
      </p>
      <div class="mt-6">
        <button 
          @click="openAddModal"
          class="inline-flex items-center px-4 py-2 border border-transparent shadow-sm text-sm font-medium rounded-md text-white bg-primary-600 hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500"
        >
          <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
          </svg>
          Add Supplier
        </button>
      </div>
    </div>
    
    <!-- Suppliers List -->
    <SupplierList
      v-else
      :suppliers="filteredSuppliers"
      @edit="editSupplier"
      @toggle-active="toggleSupplierActive"
      @delete="confirmDelete"
    />
    
    <!-- Form Modal -->
    <SupplierFormModal
      :show="showModal"
      :supplier="selectedSupplier"
      :loading="modalLoading"
      @close="closeModal"
      @save="saveSupplierWithLoading"
    />
    
    <!-- Delete Confirmation Modal -->
    <DeleteConfirmationModal
      :show="showDeleteModal"
      :supplier="supplierToDelete"
      :loading="deleteLoading"
      @close="closeDeleteModal"
      @confirm="handleDeleteSupplier"
      @deactivate="handleDeactivateSupplier"
    />
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useSuppliers } from '../composables/useSuppliers'
import SupplierList from '../components/suppliers/SupplierList.vue'
import SupplierFormModal from '../components/suppliers/SupplierFormModal.vue'
import DeleteConfirmationModal from '../components/suppliers/DeleteConfirmationModal.vue'

// Use the suppliers composable
const {
  // State
  suppliers,
  loading,
  error,
  showModal,
  showDeleteModal,
  isEditing,
  supplierToDelete,
  selectedSupplier,
  
  // Computed
  supplierCount,
  activeSuppliers,
  inactiveSuppliers,
  
  // Methods
  openAddModal,
  editSupplier,
  closeModal,
  confirmDelete,
  closeDeleteModal,
  saveSupplier,
  handleDeleteSupplier,
  toggleSupplierActive,
  initialize
} = useSuppliers()

// Local state for filtering
const searchTerm = ref('')
const showActive = ref(true)
const showInactive = ref(true)
const modalLoading = ref(false)
const deleteLoading = ref(false)

// Computed filtered suppliers
const filteredSuppliers = computed(() => {
  let filtered = suppliers.value

  // Filter by search term
  if (searchTerm.value) {
    const search = searchTerm.value.toLowerCase()
    filtered = filtered.filter(supplier => 
      supplier.name.toLowerCase().includes(search) ||
      supplier.contact_person?.toLowerCase().includes(search) ||
      supplier.email?.toLowerCase().includes(search)
    )
  }

  // Filter by active status
  if (showActive.value && !showInactive.value) {
    filtered = filtered.filter(supplier => supplier.is_active)
  } else if (!showActive.value && showInactive.value) {
    filtered = filtered.filter(supplier => !supplier.is_active)
  }

  return filtered
})

// Override save supplier to handle loading state
const saveSupplierWithLoading = async (supplierData) => {
  modalLoading.value = true
  try {
    await saveSupplier(supplierData)
  } catch (err) {
    console.error('Error saving supplier:', err)
    // Error handling is done in the composable
  } finally {
    modalLoading.value = false
  }
}

// Override delete supplier to handle loading state
const handleDeleteSupplierWithLoading = async () => {
  deleteLoading.value = true
  try {
    await handleDeleteSupplier()
  } catch (err) {
    console.error('Error deleting supplier:', err)
    // Error handling is done in the composable
  } finally {
    deleteLoading.value = false
  }
}

// Handle deactivating supplier instead of deleting
const handleDeactivateSupplier = async () => {
  if (supplierToDelete.value) {
    deleteLoading.value = true
    try {
      await toggleSupplierActive(supplierToDelete.value.id)
      closeDeleteModal()
    } catch (err) {
      console.error('Error deactivating supplier:', err)
    } finally {
      deleteLoading.value = false
    }
  }
}

// Initialize data on component mount
onMounted(async () => {
  await initialize()
})

// Watch for changes in filter checkboxes to ensure at least one is selected
watch([showActive, showInactive], ([active, inactive]) => {
  if (!active && !inactive) {
    showActive.value = true
  }
})
</script> 