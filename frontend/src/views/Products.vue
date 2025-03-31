<template>
  <div>
    <div class="flex justify-between items-center mb-6">
      <h1 class="text-2xl font-semibold text-gray-900">Products</h1>
      <button 
        @click="openAddModal" 
        class="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-primary-600 hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500"
      >
        Add Product
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
    
    <div v-else-if="products.length === 0" class="bg-white shadow overflow-hidden sm:rounded-lg">
      <div class="px-4 py-5 sm:p-6 text-center">
        <h3 class="text-lg leading-6 font-medium text-gray-900">No products found</h3>
        <div class="mt-2 max-w-xl text-sm text-gray-500">
          <p>Get started by adding your first product.</p>
        </div>
        <div class="mt-5">
          <button
            @click="openAddModal"
            class="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-primary-600 hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500"
          >
            Add Product
          </button>
        </div>
      </div>
    </div>
    
    <div v-else class="bg-white shadow overflow-hidden sm:rounded-lg">
      <ul role="list" class="divide-y divide-gray-200">
        <li v-for="product in products" :key="product.id" class="px-4 py-4 sm:px-6">
          <div class="flex items-center justify-between">
            <div class="flex items-center">
              <div class="flex-shrink-0 h-12 w-12 bg-gray-200 rounded-md overflow-hidden">
                <img 
                  v-if="product.image" 
                  :src="getImageUrl(product.image)" 
                  :alt="product.name" 
                  class="h-full w-full object-cover"
                >
                <div v-else class="h-full w-full flex items-center justify-center text-gray-500">
                  No image
                </div>
              </div>
              <div class="ml-4">
                <p class="text-sm font-medium text-primary-600">{{ product.name }}</p>
                <div class="flex space-x-4 mt-1">
                  <p class="text-sm text-gray-500">
                    Cost: ${{ product.cost_price.toFixed(2) }}
                  </p>
                  <p class="text-sm text-gray-500">
                    SKU: {{ product.sku }}
                  </p>
                </div>
              </div>
            </div>
            <div class="flex space-x-2">
              <button
                @click="editProduct(product)"
                class="inline-flex items-center px-2.5 py-1.5 border border-gray-300 shadow-sm text-xs font-medium rounded text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500"
              >
                Edit
              </button>
              <button
                @click="confirmDelete(product)"
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
          <form @submit.prevent="saveProduct">
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
                        v-model="productForm.name"
                        class="mt-1 focus:ring-primary-500 focus:border-primary-500 block w-full shadow-sm sm:text-sm border-gray-300 rounded-md"
                        required
                      >
                    </div>
                    <div>
                      <label for="sku" class="block text-sm font-medium text-gray-700">SKU</label>
                      <input 
                        type="text" 
                        name="sku" 
                        id="sku" 
                        v-model="productForm.sku"
                        class="mt-1 focus:ring-primary-500 focus:border-primary-500 block w-full shadow-sm sm:text-sm border-gray-300 rounded-md"
                        required
                      >
                    </div>
                    <div>
                      <label for="cost_price" class="block text-sm font-medium text-gray-700">Cost Price ($)</label>
                      <input 
                        type="number" 
                        name="cost_price" 
                        id="cost_price" 
                        v-model="productForm.cost_price"
                        min="0"
                        step="0.01"
                        class="mt-1 focus:ring-primary-500 focus:border-primary-500 block w-full shadow-sm sm:text-sm border-gray-300 rounded-md"
                        required
                      >
                    </div>
                    <div>
                      <label for="description" class="block text-sm font-medium text-gray-700">Description</label>
                      <textarea 
                        id="description" 
                        name="description" 
                        rows="3" 
                        v-model="productForm.description"
                        class="shadow-sm focus:ring-primary-500 focus:border-primary-500 mt-1 block w-full sm:text-sm border border-gray-300 rounded-md"
                      ></textarea>
                    </div>
                    <div>
                      <label class="block text-sm font-medium text-gray-700">Product Image</label>
                      <div class="mt-1 flex items-center">
                        <div v-if="imagePreview" class="h-32 w-32 rounded-md overflow-hidden bg-gray-100">
                          <img :src="imagePreview" class="h-full w-full object-cover">
                        </div>
                        <div v-else class="h-32 w-32 rounded-md border-2 border-dashed border-gray-300 flex justify-center items-center">
                          <span class="text-gray-500 text-sm">No image</span>
                        </div>
                        <button
                          type="button"
                          @click="$refs.fileInput.click()"
                          class="ml-5 bg-white py-2 px-3 border border-gray-300 rounded-md shadow-sm text-sm leading-4 font-medium text-gray-700 hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500"
                        >
                          {{ imagePreview ? 'Change' : 'Upload' }}
                        </button>
                        <input 
                          ref="fileInput" 
                          type="file" 
                          class="hidden" 
                          @change="onFileChange" 
                          accept="image/*"
                        >
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
                  Delete Product
                </h3>
                <div class="mt-2">
                  <p class="text-sm text-gray-500">
                    Are you sure you want to delete <span class="font-medium">{{ productToDelete?.name }}</span>? This action cannot be undone.
                  </p>
                </div>
              </div>
            </div>
          </div>
          <div class="bg-gray-50 px-4 py-3 sm:px-6 sm:flex sm:flex-row-reverse">
            <button 
              type="button"
              @click="deleteProduct"
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
import { api, getImageUrl } from '../services/api'

const products = ref([])
const loading = ref(true)
const error = ref(null)

// Modal states
const showModal = ref(false)
const showDeleteModal = ref(false)
const isEditing = ref(false)
const productToDelete = ref(null)
const imagePreview = ref(null)

// Form for creating/editing a product
const productForm = ref({
  id: null,
  name: '',
  sku: '',
  description: '',
  cost_price: 0,
  image: null
})

// File input reference
const fileInput = ref(null)

// Fetch all products
const fetchProducts = async () => {
  loading.value = true
  try {
    const response = await api.getProducts()
    products.value = response.data
  } catch (err) {
    console.error('Error fetching products:', err)
    error.value = 'Failed to load products. Please try again later.'
  } finally {
    loading.value = false
  }
}

// Handle file upload
const onFileChange = (event) => {
  const file = event.target.files[0]
  if (!file) return
  
  productForm.value.image = file
  
  // Create a preview
  const reader = new FileReader()
  reader.onload = (e) => {
    imagePreview.value = e.target.result
  }
  reader.readAsDataURL(file)
}

// Open modal to add a new product
const openAddModal = () => {
  isEditing.value = false
  productForm.value = {
    id: null,
    name: '',
    sku: '',
    description: '',
    cost_price: 0,
    image: null
  }
  imagePreview.value = null
  showModal.value = true
}

// Open modal to edit an existing product
const editProduct = (product) => {
  isEditing.value = true
  productForm.value = {
    id: product.id,
    name: product.name,
    sku: product.sku,
    description: product.description || '',
    cost_price: product.cost_price,
    image: null // Don't set image when editing, only if user uploads a new one
  }
  
  // Set preview if product has an image
  imagePreview.value = product.image ? getImageUrl(product.image) : null
  
  showModal.value = true
}

// Save the product (create or update)
const saveProduct = async () => {
  try {
    if (isEditing.value) {
      await api.updateProduct(productForm.value.id, productForm.value)
    } else {
      await api.createProduct(productForm.value)
    }
    
    showModal.value = false
    await fetchProducts()
  } catch (err) {
    console.error('Error saving product:', err)
    error.value = 'Failed to save product. Please try again.'
  }
}

// Show delete confirmation modal
const confirmDelete = (product) => {
  productToDelete.value = product
  showDeleteModal.value = true
}

// Delete the product
const deleteProduct = async () => {
  if (!productToDelete.value) return
  
  try {
    await api.deleteProduct(productToDelete.value.id)
    showDeleteModal.value = false
    await fetchProducts()
  } catch (err) {
    console.error('Error deleting product:', err)
    error.value = 'Failed to delete product. Please try again.'
  }
}

// Initialize data on component mount
onMounted(fetchProducts)
</script> 