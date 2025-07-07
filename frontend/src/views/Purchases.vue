<template>
  <div>
    <div class="flex justify-between items-center mb-6">
      <h1 class="text-2xl font-semibold text-gray-900">Wholesale Purchases</h1>
      <div class="flex space-x-3">
        <router-link
          to="/suppliers"
          class="inline-flex items-center px-4 py-2 border border-gray-300 text-sm font-medium rounded-md shadow-sm text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500"
        >
          <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4" />
          </svg>
          Suppliers
        </router-link>
        <button 
          @click="openAddModal" 
          class="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-primary-600 hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500"
        >
          <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
          </svg>
          Add Purchase
        </button>
      </div>
    </div>
    
    <PurchaseList
      :purchases="purchases"
      :loading="loading"
      :error="error"
      @add-purchase="openAddModal"
      @edit-purchase="editPurchase"
      @delete-purchase="confirmDelete"
    />
    
    <PurchaseFormModal
      :show="showModal"
      :is-editing="isEditing"
      :form="purchaseForm"
      :products="products"
      :suppliers="suppliers"
      :selected-product="selectedProduct"
      :unit-cost="unitCost"
      @close="closeModal"
      @save="savePurchase"
      @update:form="updateForm"
      @product-change="onProductChange"
      @calculate-unit-cost="calculateUnitCost"
    />
    
    <DeleteConfirmationModal
      :show="showDeleteModal"
      :purchase="purchaseToDelete"
      @close="closeDeleteModal"
      @confirm="deletePurchase"
    />
  </div>
</template>

<script setup>
import { onMounted } from 'vue'
import { usePurchases } from '../composables/usePurchases'
import PurchaseList from '../components/purchases/PurchaseList.vue'
import PurchaseFormModal from '../components/purchases/PurchaseFormModal.vue'
import DeleteConfirmationModal from '../components/purchases/DeleteConfirmationModal.vue'

// Use the purchases composable
const {
  // State
  purchases,
  products,
  suppliers,
  loading,
  error,
  selectedProduct,
  showModal,
  showDeleteModal,
  isEditing,
  purchaseToDelete,
  purchaseForm,
  
  // Computed
  unitCost,
  
  // Methods
  onProductChange,
  openAddModal,
  editPurchase,
  savePurchase,
  confirmDelete,
  deletePurchase,
  calculateUnitCost,
  closeModal,
  closeDeleteModal,
  initialize
} = usePurchases()

// Helper function to update form
const updateForm = (newForm) => {
  Object.assign(purchaseForm.value, newForm)
}

// Initialize data on component mount
onMounted(async () => {
  await initialize()
})
</script> 