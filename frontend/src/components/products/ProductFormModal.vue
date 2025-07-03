<template>
  <div v-if="show" class="fixed inset-0 overflow-y-auto z-50" aria-labelledby="modal-title" role="dialog" aria-modal="true">
    <div class="flex items-end justify-center min-h-screen pt-4 px-4 pb-20 text-center sm:block sm:p-0">
      <div class="fixed inset-0 bg-gray-500 bg-opacity-75 transition-opacity" aria-hidden="true" @click="$emit('close')"></div>
      
      <span class="hidden sm:inline-block sm:align-middle sm:h-screen" aria-hidden="true">&#8203;</span>
      
      <div class="inline-block align-bottom bg-white rounded-xl text-left overflow-hidden shadow-xl transform transition-all sm:my-8 sm:align-middle sm:max-w-lg sm:w-full">
        <form @submit.prevent="handleSubmit">
          <div class="bg-white px-4 pt-5 pb-4 sm:p-6 sm:pb-4">
            <div class="sm:flex sm:items-start">
              <div class="mt-3 text-center sm:mt-0 sm:text-left w-full">
                <h3 class="text-lg leading-6 font-medium text-gray-900" id="modal-title">
                  {{ isEditing ? 'Edit Product' : 'Add New Product' }}
                </h3>
                <div class="mt-4 space-y-4">
                  <div>
                    <label for="name" class="block text-sm font-medium text-gray-700">Product Name</label>
                    <input 
                      type="text" 
                      name="name" 
                      id="name" 
                      v-model="formData.name"
                      class="mt-1 focus:ring-primary-500 focus:border-primary-500 block w-full shadow-sm sm:text-sm border-gray-300 rounded-md"
                      required
                    >
                  </div>
                  <div>
                    <label for="product_type" class="block text-sm font-medium text-gray-700">Product Type</label>
                    <select 
                      id="product_type" 
                      name="product_type" 
                      v-model="formData.product_type"
                      class="mt-1 block w-full pl-3 pr-10 py-2 text-base border-gray-300 focus:outline-none focus:ring-primary-500 focus:border-primary-500 sm:text-sm rounded-md"
                      required
                    >
                      <option value="Soda">Soda</option>
                      <option value="Snack">Snack</option>
                    </select>
                  </div>
                  <div class="grid grid-cols-2 gap-4">
                    <div>
                      <label for="cost_price" class="block text-sm font-medium text-gray-700">Cost ($)</label>
                      <input 
                        type="number" 
                        name="cost_price" 
                        id="cost_price" 
                        v-model="formData.cost_price"
                        min="0"
                        step="0.01"
                        class="mt-1 focus:ring-primary-500 focus:border-primary-500 block w-full shadow-sm sm:text-sm border-gray-300 rounded-md"
                        required
                      >
                    </div>
                    <div>
                      <label for="inventory_quantity" class="block text-sm font-medium text-gray-700">Inventory</label>
                      <input 
                        type="number" 
                        name="inventory_quantity" 
                        id="inventory_quantity" 
                        v-model="formData.inventory_quantity"
                        min="0"
                        step="1"
                        class="mt-1 focus:ring-primary-500 focus:border-primary-500 block w-full shadow-sm sm:text-sm border-gray-300 rounded-md"
                      >
                    </div>
                  </div>
                  <div>
                    <label for="description" class="block text-sm font-medium text-gray-700">Description</label>
                    <textarea 
                      id="description" 
                      name="description" 
                      rows="3" 
                      v-model="formData.description"
                      class="shadow-sm focus:ring-primary-500 focus:border-primary-500 mt-1 block w-full sm:text-sm border border-gray-300 rounded-md"
                    ></textarea>
                  </div>
                  <div>
                    <label for="image_url" class="block text-sm font-medium text-gray-700">Image URL</label>
                    <input 
                      type="url" 
                      name="image_url" 
                      id="image_url" 
                      v-model="formData.image_url"
                      placeholder="https://example.com/image.jpg"
                      class="mt-1 focus:ring-primary-500 focus:border-primary-500 block w-full shadow-sm sm:text-sm border-gray-300 rounded-md"
                    >
                  </div>
                  <div v-if="isEditing && product" class="mt-4 bg-gray-50 p-3 rounded-md">
                    <h4 class="text-sm font-medium text-gray-700 mb-2">Additional Information:</h4>
                    <div class="grid grid-cols-2 gap-2">
                      <div>
                        <span class="text-xs text-gray-500">Latest Unit Cost:</span>
                        <p class="text-sm font-medium text-primary-600">${{ product.latest_cost || '0.00' }}</p>
                      </div>
                      <div>
                        <span class="text-xs text-gray-500">Average Cost:</span>
                        <p class="text-sm font-medium text-primary-600">${{ product.average_cost || '0.00' }}</p>
                      </div>
                    </div>
                  </div>
                  
                  <div v-if="formData.image_url" class="mt-3">
                    <h4 class="text-sm font-medium text-gray-700 mb-2">Image Preview:</h4>
                    <div class="h-32 w-32 rounded-lg overflow-hidden bg-gray-100 shadow-sm">
                      <img :src="formData.image_url" class="h-full w-full object-cover" @error="handleImageError">
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
          <div class="bg-gray-50 px-4 py-3 sm:px-6 sm:flex sm:flex-row-reverse">
            <button 
              type="submit"
              :disabled="loading"
              class="w-full inline-flex justify-center rounded-md border border-transparent shadow-sm px-4 py-2 bg-primary-600 text-base font-medium text-white hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500 sm:ml-3 sm:w-auto sm:text-sm transition-colors duration-150 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              <svg v-if="loading" class="animate-spin -ml-1 mr-2 h-4 w-4 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
              </svg>
              {{ loading ? 'Saving...' : (isEditing ? 'Update' : 'Add') }}
            </button>
            <button 
              type="button"
              @click="$emit('close')"
              :disabled="loading"
              class="mt-3 w-full inline-flex justify-center rounded-md border border-gray-300 shadow-sm px-4 py-2 bg-white text-base font-medium text-gray-700 hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500 sm:mt-0 sm:ml-3 sm:w-auto sm:text-sm transition-colors duration-150 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              Cancel
            </button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch } from 'vue'

const props = defineProps({
  show: {
    type: Boolean,
    default: false
  },
  product: {
    type: Object,
    default: null
  },
  loading: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits(['close', 'save'])

// Form data
const formData = ref({
  id: null,
  name: '',
  product_type: 'Soda',
  description: '',
  cost_price: 0,
  inventory_quantity: 0,
  image_url: ''
})

// Computed property to check if we're editing
const isEditing = computed(() => Boolean(props.product?.id))

// Watch for product changes to populate form
watch(() => props.product, (newProduct) => {
  if (newProduct) {
    formData.value = {
      id: newProduct.id,
      name: newProduct.name,
      product_type: newProduct.product_type || 'Soda',
      description: newProduct.description || '',
      cost_price: newProduct.cost_price,
      inventory_quantity: newProduct.inventory_quantity || 0,
      image_url: newProduct.image_url || ''
    }
  } else {
    // Reset form for new product
    formData.value = {
      id: null,
      name: '',
      product_type: 'Soda',
      description: '',
      cost_price: 0,
      inventory_quantity: 0,
      image_url: ''
    }
  }
}, { immediate: true })

// Handle form submission
const handleSubmit = () => {
  emit('save', { ...formData.value })
}

// Handle image loading error
const handleImageError = (event) => {
  console.error('Image load error:', event.target.src)
}
</script> 