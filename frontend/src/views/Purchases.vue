<template>
  <div>
    <div class="flex justify-between items-center mb-6">
      <h1 class="text-2xl font-semibold text-gray-900">Wholesale Purchases</h1>
      <button 
        @click="openAddModal" 
        class="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-primary-600 hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500"
      >
        Add Purchase
      </button>
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