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
                <span class="ml-2 px-2 inline-flex text-xs leading-5 font-semibold rounded-full bg-green-100 text-green-800">
                  {{ purchase.supplier || "Unknown" }}
                </span>
                <span v-if="purchase.current_inventory" class="ml-2 px-2 inline-flex text-xs leading-5 font-semibold rounded-full bg-purple-100 text-purple-800">
                  Inventory: {{ purchase.current_inventory }}
                </span>
              </div>
              <div class="mt-1">
                <p class="text-sm text-gray-500">
                  Date: {{ formatDate(purchase.purchase_date) }}
                </p>
                <p class="text-sm text-gray-500">
                  Total: ${{ parseFloat(purchase.total_cost).toFixed(2) }} | 
                  Unit Cost: ${{ parseFloat(purchase.cost_per_unit || (purchase.total_cost / purchase.quantity)).toFixed(2) }}
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
                        @change="onProductChange"
                        class="mt-1 block w-full pl-3 pr-10 py-2 text-base border-gray-300 focus:outline-none focus:ring-primary-500 focus:border-primary-500 sm:text-sm rounded-md"
                        required
                      >
                        <option value="" disabled>Select a product</option>
                        <option v-for="product in products" :key="product.id" :value="product.id">
                          {{ product.name }} ({{ product.inventory_quantity }} in stock)
                        </option>
                      </select>
                    </div>
                    
                    <div>
                      <label for="supplier" class="block text-sm font-medium text-gray-700">Supplier</label>
                      <select
                        id="supplier"
                        name="supplier"
                        v-model="purchaseForm.supplier"
                        class="mt-1 block w-full pl-3 pr-10 py-2 text-base border-gray-300 focus:outline-none focus:ring-primary-500 focus:border-primary-500 sm:text-sm rounded-md"
                        required
                      >
                        <option value="" disabled>Select a supplier</option>
                        <option value="Sams">Sams</option>
                        <option value="Star">Star</option>
                      </select>
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
                          @change="calculateUnitCost"
                          class="mt-1 focus:ring-primary-500 focus:border-primary-500 block w-full shadow-sm sm:text-sm border-gray-300 rounded-md"
                          required
                        >
                      </div>
                      
                      <div>
                        <label for="total_cost" class="block text-sm font-medium text-gray-700">Total Cost ($)</label>
                        <input 
                          type="number" 
                          name="total_cost" 
                          id="total_cost" 
                          v-model="purchaseForm.total_cost"
                          min="0.01"
                          step="0.01"
                          @change="calculateUnitCost"
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
                    
                    <div class="grid grid-cols-2 gap-4">
                      <div class="bg-gray-50 p-3 rounded-md">
                        <div class="text-sm font-medium text-gray-700">Unit Cost:</div>
                        <div class="text-lg font-bold text-primary-600">
                          ${{ unitCost.toFixed(2) }} per unit
                        </div>
                      </div>
                      
                      <div v-if="selectedProduct" class="bg-gray-50 p-3 rounded-md">
                        <div class="text-sm font-medium text-gray-700">Current Inventory:</div>
                        <div class="text-lg font-bold text-primary-600">
                          {{ selectedProduct.inventory_quantity || 0 }} units
                        </div>
                        <div class="text-xs text-gray-500 mt-1">
                          After purchase: {{ calculateNewInventory() }} units
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
                  <p v-if="purchaseToDelete" class="text-sm text-red-500 mt-2">
                    Note: This will also reduce your inventory by {{ purchaseToDelete.quantity }} units.
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
const selectedProduct = ref(null)

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
  total_cost: 0,
  notes: ''
})

// Computed total cost
const totalCost = computed(() => {
  const quantity = parseFloat(purchaseForm.value.quantity) || 0
  const totalCost = parseFloat(purchaseForm.value.total_cost) || 0
  return totalCost
})

// Computed unit cost
const unitCost = computed(() => {
  const quantity = parseFloat(purchaseForm.value.quantity) || 0
  const totalCost = parseFloat(purchaseForm.value.total_cost) || 0
  
  if (quantity > 0) {
    return totalCost / quantity
  }
  return 0
})

// Calculate new inventory after purchase
const calculateNewInventory = () => {
  if (!selectedProduct.value) return 0
  
  const currentInventory = selectedProduct.value.inventory_quantity || 0
  const purchaseQuantity = parseInt(purchaseForm.value.quantity) || 0
  
  if (isEditing.value) {
    // Get the original purchase quantity if editing
    const originalPurchase = purchases.value.find(p => p.id === purchaseForm.value.id)
    const originalQuantity = originalPurchase ? parseInt(originalPurchase.quantity) || 0 : 0
    
    // Calculate the net change in inventory
    return currentInventory + (purchaseQuantity - originalQuantity)
  }
  
  // For new purchases, just add
  return currentInventory + purchaseQuantity
}

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
    console.log('Purchases data:', response.data)
    purchases.value = response.data.map(purchase => {
      // Ensure all the necessary fields are available
      const unitCost = purchase.cost_per_unit || 
                      (purchase.unit_cost) || 
                      (purchase.total_cost && purchase.quantity ? purchase.total_cost / purchase.quantity : 0)
      
      // Handle both purchased_at and purchase_date
      const purchaseDate = purchase.purchase_date || purchase.purchased_at
      
      return {
        ...purchase,
        purchase_date: purchaseDate,
        total_cost: purchase.total_cost || (purchase.cost_per_unit * purchase.quantity),
        cost_per_unit: unitCost
      }
    })
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

// Handle product selection change
const onProductChange = () => {
  if (purchaseForm.value.product) {
    selectedProduct.value = products.value.find(p => p.id == purchaseForm.value.product)
    
    // Pre-fill with latest cost if available
    if (selectedProduct.value && selectedProduct.value.latest_cost) {
      const latestCost = parseFloat(selectedProduct.value.latest_cost)
      if (latestCost > 0) {
        purchaseForm.value.total_cost = latestCost * purchaseForm.value.quantity
        calculateUnitCost()
      }
    }
  } else {
    selectedProduct.value = null
  }
}

// Open modal to add a new purchase
const openAddModal = () => {
  isEditing.value = false
  selectedProduct.value = null
  
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
    total_cost: 0,
    notes: ''
  }
  
  showModal.value = true
}

// Open modal to edit an existing purchase
const editPurchase = (purchase) => {
  isEditing.value = true
  
  // Ensure we have the total cost
  const totalCost = purchase.total_cost || (purchase.cost_per_unit * purchase.quantity)
  
  // Format date properly - handling both purchased_at and purchase_date
  let dateString = purchase.purchased_at || purchase.purchase_date
  // Extract just the date part (YYYY-MM-DD)
  let formattedDate = dateString ? dateString.split('T')[0] : ''
  
  // If no valid date is found, use today
  if (!formattedDate) {
    const today = new Date()
    formattedDate = today.toISOString().split('T')[0]
  }
  
  purchaseForm.value = {
    id: purchase.id,
    product: purchase.product,
    supplier: purchase.supplier || '',
    purchase_date: formattedDate,
    quantity: purchase.quantity,
    total_cost: totalCost,
    notes: purchase.notes || ''
  }
  
  // Set selected product
  if (purchase.product) {
    selectedProduct.value = products.value.find(p => p.id == purchase.product)
  }
  
  // Calculate unit cost for display
  calculateUnitCost()
  
  showModal.value = true
}

// Save the purchase (create or update)
const savePurchase = async () => {
  try {
    // Validate inputs
    const quantity = parseInt(purchaseForm.value.quantity) || 0
    const totalCost = parseFloat(purchaseForm.value.total_cost) || 0
    
    if (quantity <= 0) {
      error.value = 'Quantity must be greater than zero'
      return
    }
    
    if (totalCost <= 0) {
      error.value = 'Total cost must be greater than zero'
      return
    }
    
    // Format the date properly with time component
    const dateWithTime = `${purchaseForm.value.purchase_date}T12:00:00`
    
    // Prepare data for API
    const purchaseData = {
      product: purchaseForm.value.product,
      supplier: purchaseForm.value.supplier,
      purchased_at: dateWithTime,       // Use purchased_at which is the actual model field
      purchase_date: dateWithTime,      // Also include purchase_date as the serializer expects it
      quantity: quantity,
      total_cost: totalCost,
      notes: purchaseForm.value.notes || '',
      cost_per_unit: Math.round(unitCost.value * 100) / 100  // Round to 2 decimal places
    }
    
    console.log('Saving purchase with data:', purchaseData)
    
    let response
    if (isEditing.value) {
      response = await api.updatePurchase(purchaseForm.value.id, purchaseData)
    } else {
      response = await api.createPurchase(purchaseData)
    }
    
    console.log('Purchase saved successfully:', response.data)
    
    // Get the updated product to see the new inventory and cost
    const productResponse = await api.getProduct(purchaseForm.value.product)
    console.log('Updated product:', productResponse.data)
    
    showModal.value = false
    
    // Refresh data
    await Promise.all([fetchPurchases(), fetchProducts()])
  } catch (err) {
    console.error('Error saving purchase:', err)
    if (err.response && err.response.data) {
      console.error('Server error details:', err.response.data)
      error.value = `Failed to save purchase: ${JSON.stringify(err.response.data)}`
    } else {
      error.value = 'Failed to save purchase. Please try again.'
    }
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
    
    // Refresh data
    await Promise.all([fetchPurchases(), fetchProducts()])
  } catch (err) {
    console.error('Error deleting purchase:', err)
    error.value = 'Failed to delete purchase. Please try again.'
  }
}

// Calculate unit cost when quantity or total cost changes
const calculateUnitCost = () => {
  const quantity = parseFloat(purchaseForm.value.quantity) || 0
  const totalCost = parseFloat(purchaseForm.value.total_cost) || 0
  
  // Avoid division by zero
  if (quantity > 0) {
    // Round to 2 decimal places to match backend validation
    purchaseForm.value.cost_per_unit = Math.round((totalCost / quantity) * 100) / 100
  } else {
    purchaseForm.value.cost_per_unit = 0
  }
}

// Initialize data on component mount
onMounted(async () => {
  await Promise.all([fetchPurchases(), fetchProducts()])
})
</script> 