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
    
    <div v-else-if="purchases.length === 0" class="bg-white shadow overflow-hidden sm:rounded-lg">
      <div class="px-4 py-5 sm:p-6 text-center">
        <h3 class="text-lg leading-6 font-medium text-gray-900">No purchases found</h3>
        <div class="mt-2 max-w-xl text-sm text-gray-500">
          <p>Get started by recording your first wholesale purchase.</p>
        </div>
        <div class="mt-5">
          <button
            @click="openAddModal"
            class="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-primary-600 hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500"
          >
            Add Purchase
          </button>
        </div>
      </div>
    </div>
    
    <div v-else class="bg-white shadow overflow-hidden sm:rounded-lg">
      <ul role="list" class="divide-y divide-gray-200">
        <li v-for="purchase in purchases" :key="purchase.id" class="px-4 py-4 sm:px-6">
          <div class="flex items-center justify-between">
            <div>
              <div class="flex items-center">
                <p class="text-sm font-medium text-primary-600">
                  {{ purchase.product_name }}
                </p>
                <span class="ml-2 px-2 inline-flex text-xs leading-5 font-semibold rounded-full bg-blue-100 text-blue-800">
                  {{ purchase.quantity }} units
                </span>
              </div>
              <div class="mt-1">
                <p class="text-sm text-gray-500">
                  Date: {{ formatDate(purchase.purchase_date) }} | Supplier: {{ purchase.supplier }}
                </p>
                <p class="text-sm text-gray-500">
                  Cost: ${{ purchase.cost_per_unit.toFixed(2) }} per unit | Total: ${{ (purchase.cost_per_unit * purchase.quantity).toFixed(2) }}
                </p>
              </div>
            </div>
            <div class="flex space-x-2">
              <button
                @click="editPurchase(purchase)"
                class="inline-flex items-center px-2.5 py-1.5 border border-gray-300 shadow-sm text-xs font-medium rounded text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500"
              >
                Edit
              </button>
              <button
                @click="confirmDelete(purchase)"
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
          <form @submit.prevent="savePurchase">
            <div class="bg-white px-4 pt-5 pb-4 sm:p-6 sm:pb-4">
              <div class="sm:flex sm:items-start">
                <div class="mt-3 text-center sm:mt-0 sm:text-left w-full">
                  <h3 class="text-lg leading-6 font-medium text-gray-900" id="modal-title">
                    {{ isEditing ? 'Edit Purchase' : 'Add New Purchase' }}
                  </h3>
                  <div class="mt-4 space-y-4">
                    <div>
                      <label for="product" class="block text-sm font-medium text-gray-700">Product</label>
                      <select
                        id="product"
                        name="product"
                        v-model="purchaseForm.product"
                        class="mt-1 block w-full pl-3 pr-10 py-2 text-base border-gray-300 focus:outline-none focus:ring-primary-500 focus:border-primary-500 sm:text-sm rounded-md"
                        required
                      >
                        <option value="" disabled>Select a product</option>
                        <option v-for="product in products" :key="product.id" :value="product.id">
                          {{ product.name }}
                        </option>
                      </select>
                    </div>
                    
                    <div>
                      <label for="supplier" class="block text-sm font-medium text-gray-700">Supplier</label>
                      <input 
                        type="text" 
                        name="supplier" 
                        id="supplier" 
                        v-model="purchaseForm.supplier"
                        class="mt-1 focus:ring-primary-500 focus:border-primary-500 block w-full shadow-sm sm:text-sm border-gray-300 rounded-md"
                        required
                      >
                    </div>
                    
                    <div>
                      <label for="purchase_date" class="block text-sm font-medium text-gray-700">Purchase Date</label>
                      <input 
                        type="date" 
                        name="purchase_date" 
                        id="purchase_date" 
                        v-model="purchaseForm.purchase_date"
                        class="mt-1 focus:ring-primary-500 focus:border-primary-500 block w-full shadow-sm sm:text-sm border-gray-300 rounded-md"
                        required
                      >
                    </div>
                    
                    <div class="grid grid-cols-2 gap-4">
                      <div>
                        <label for="quantity" class="block text-sm font-medium text-gray-700">Quantity</label>
                        <input 
                          type="number" 
                          name="quantity" 
                          id="quantity" 
                          v-model="purchaseForm.quantity"
                          min="1"
                          class="mt-1 focus:ring-primary-500 focus:border-primary-500 block w-full shadow-sm sm:text-sm border-gray-300 rounded-md"
                          required
                        >
                      </div>
                      
                      <div>
                        <label for="cost_per_unit" class="block text-sm font-medium text-gray-700">Cost Per Unit ($)</label>
                        <input 
                          type="number" 
                          name="cost_per_unit" 
                          id="cost_per_unit" 
                          v-model="purchaseForm.cost_per_unit"
                          min="0.01"
                          step="0.01"
                          class="mt-1 focus:ring-primary-500 focus:border-primary-500 block w-full shadow-sm sm:text-sm border-gray-300 rounded-md"
                          required
                        >
                      </div>
                    </div>
                    
                    <div>
                      <label for="notes" class="block text-sm font-medium text-gray-700">Notes</label>
                      <textarea 
                        id="notes" 
                        name="notes" 
                        rows="3" 
                        v-model="purchaseForm.notes"
                        class="shadow-sm focus:ring-primary-500 focus:border-primary-500 mt-1 block w-full sm:text-sm border border-gray-300 rounded-md"
                      ></textarea>
                    </div>
                    
                    <div class="bg-gray-50 p-3 rounded-md">
                      <div class="text-sm font-medium text-gray-700">Total Cost:</div>
                      <div class="text-lg font-bold text-primary-600">
                        ${{ totalCost.toFixed(2) }}
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
                  Delete Purchase
                </h3>
                <div class="mt-2">
                  <p class="text-sm text-gray-500">
                    Are you sure you want to delete this purchase record? This action cannot be undone.
                  </p>
                </div>
              </div>
            </div>
          </div>
          <div class="bg-gray-50 px-4 py-3 sm:px-6 sm:flex sm:flex-row-reverse">
            <button 
              type="button"
              @click="deletePurchase"
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

const purchases = ref([])
const products = ref([])
const loading = ref(true)
const error = ref(null)

// Modal states
const showModal = ref(false)
const showDeleteModal = ref(false)
const isEditing = ref(false)
const purchaseToDelete = ref(null)

// Form for creating/editing a purchase
const purchaseForm = ref({
  id: null,
  product: '',
  supplier: '',
  purchase_date: '',
  quantity: 1,
  cost_per_unit: 0,
  notes: ''
})

// Computed total cost
const totalCost = computed(() => {
  const quantity = parseFloat(purchaseForm.value.quantity) || 0
  const costPerUnit = parseFloat(purchaseForm.value.cost_per_unit) || 0
  return quantity * costPerUnit
})

// Format date for display
const formatDate = (dateString) => {
  if (!dateString) return ''
  const date = new Date(dateString)
  return date.toLocaleDateString()
}

// Fetch all purchases
const fetchPurchases = async () => {
  loading.value = true
  try {
    const response = await api.getPurchases()
    purchases.value = response.data
  } catch (err) {
    console.error('Error fetching purchases:', err)
    error.value = 'Failed to load purchases. Please try again later.'
  } finally {
    loading.value = false
  }
}

// Fetch all products
const fetchProducts = async () => {
  try {
    const response = await api.getProducts()
    products.value = response.data
  } catch (err) {
    console.error('Error fetching products:', err)
  }
}

// Open modal to add a new purchase
const openAddModal = () => {
  isEditing.value = false
  
  // Set default purchase date to today
  const today = new Date()
  const year = today.getFullYear()
  const month = String(today.getMonth() + 1).padStart(2, '0')
  const day = String(today.getDate()).padStart(2, '0')
  
  purchaseForm.value = {
    id: null,
    product: '',
    supplier: '',
    purchase_date: `${year}-${month}-${day}`,
    quantity: 1,
    cost_per_unit: 0,
    notes: ''
  }
  
  showModal.value = true
}

// Open modal to edit an existing purchase
const editPurchase = (purchase) => {
  isEditing.value = true
  purchaseForm.value = {
    id: purchase.id,
    product: purchase.product,
    supplier: purchase.supplier,
    purchase_date: purchase.purchase_date.split('T')[0], // Extract just the date part
    quantity: purchase.quantity,
    cost_per_unit: purchase.cost_per_unit,
    notes: purchase.notes || ''
  }
  
  showModal.value = true
}

// Save the purchase (create or update)
const savePurchase = async () => {
  try {
    if (isEditing.value) {
      await api.updatePurchase(purchaseForm.value.id, purchaseForm.value)
    } else {
      await api.createPurchase(purchaseForm.value)
    }
    
    showModal.value = false
    await fetchPurchases()
  } catch (err) {
    console.error('Error saving purchase:', err)
    error.value = 'Failed to save purchase. Please try again.'
  }
}

// Show delete confirmation modal
const confirmDelete = (purchase) => {
  purchaseToDelete.value = purchase
  showDeleteModal.value = true
}

// Delete the purchase
const deletePurchase = async () => {
  if (!purchaseToDelete.value) return
  
  try {
    await api.deletePurchase(purchaseToDelete.value.id)
    showDeleteModal.value = false
    await fetchPurchases()
  } catch (err) {
    console.error('Error deleting purchase:', err)
    error.value = 'Failed to delete purchase. Please try again.'
  }
}

// Initialize data on component mount
onMounted(async () => {
  await Promise.all([fetchPurchases(), fetchProducts()])
})
</script> 