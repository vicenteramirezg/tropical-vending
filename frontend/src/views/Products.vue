<template>
  <div>
    <div class="flex justify-between items-center mb-6">
      <h1 class="text-2xl font-semibold text-gray-900">Products</h1>
      <button 
        @click="openAddModal" 
        class="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-primary-600 hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500 transition-colors duration-150"
      >
        <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 mr-1.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
        </svg>
        Add Product
      </button>
    </div>

    <!-- Search and Filter Section -->
    <div class="mb-6">
      <div class="flex flex-col sm:flex-row gap-4">
        <!-- Search Input -->
        <div class="flex-1 max-w-md">
          <div class="relative">
            <div class="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
              <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
              </svg>
            </div>
            <input 
              type="text" 
              v-model="searchQuery"
              placeholder="Search products by name..."
              class="block w-full pl-10 pr-3 py-2 border border-gray-300 rounded-md leading-5 bg-white placeholder-gray-500 focus:outline-none focus:placeholder-gray-400 focus:ring-1 focus:ring-primary-500 focus:border-primary-500 sm:text-sm"
            >
            <div v-if="searchQuery" class="absolute inset-y-0 right-0 pr-3 flex items-center">
              <button 
                @click="clearSearch"
                class="text-gray-400 hover:text-gray-600 focus:outline-none"
              >
                <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
            </div>
          </div>
        </div>

        <!-- Product Type Filter -->
        <div class="sm:w-48">
          <div class="relative">
            <select 
              v-model="selectedProductType"
              class="block w-full pl-3 pr-10 py-2 text-base border border-gray-300 focus:outline-none focus:ring-primary-500 focus:border-primary-500 sm:text-sm rounded-md bg-white"
            >
              <option value="">All Product Types</option>
              <option value="Soda">Soda</option>
              <option value="Snack">Snack</option>
            </select>
            <div class="absolute inset-y-0 right-0 pr-3 flex items-center pointer-events-none">
              <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 4a1 1 0 011-1h16a1 1 0 011 1v2.586a1 1 0 01-.293.707l-6.414 6.414a1 1 0 00-.293.707V17l-4 4v-6.586a1 1 0 00-.293-.707L3.293 7.293A1 1 0 013 6.586V4z" />
              </svg>
            </div>
          </div>
        </div>

        <!-- Clear Filters Button -->
        <div v-if="searchQuery || selectedProductType" class="sm:w-auto">
          <button
            @click="clearAllFilters"
            class="w-full sm:w-auto inline-flex items-center justify-center px-4 py-2 border border-gray-300 shadow-sm text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500 transition-colors duration-150"
          >
            <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
            </svg>
            Clear Filters
          </button>
        </div>
      </div>

      <!-- Filter Results Summary -->
      <div v-if="(searchQuery || selectedProductType) && filteredProducts.length !== products.length" class="mt-3 text-sm text-gray-600">
        <div class="flex flex-wrap items-center gap-2">
          <span>Showing {{ filteredProducts.length }} of {{ products.length }} products</span>
          <span v-if="searchQuery" class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-800">
            Name: "{{ searchQuery }}"
          </span>
          <span v-if="selectedProductType" class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800">
            Type: {{ selectedProductType }}
          </span>
        </div>
      </div>
    </div>
    
    <div v-if="loading" class="flex justify-center py-20">
      <div class="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-primary-500"></div>
    </div>
    
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
    
    <div v-else-if="filteredProducts.length === 0 && (searchQuery || selectedProductType)" class="bg-white shadow-lg rounded-xl overflow-hidden">
      <div class="px-6 py-8 text-center">
        <svg xmlns="http://www.w3.org/2000/svg" class="h-16 w-16 mx-auto text-gray-400 mb-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
        </svg>
        <h3 class="text-lg leading-6 font-medium text-gray-900 mb-2">No products found</h3>
        <div class="mt-2 max-w-xl text-sm text-gray-500 mx-auto mb-6">
          <p>No products match your current filters.</p>
          <div class="mt-2 flex flex-wrap justify-center gap-2">
            <span v-if="searchQuery" class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-800">
              Name: "{{ searchQuery }}"
            </span>
            <span v-if="selectedProductType" class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800">
              Type: {{ selectedProductType }}
            </span>
          </div>
        </div>
        <button
          @click="clearAllFilters"
          class="inline-flex items-center px-4 py-2 border border-gray-300 shadow-sm text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500 transition-colors duration-150"
        >
          <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
          </svg>
          Clear All Filters
        </button>
      </div>
    </div>
    
    <div v-else-if="products.length === 0" class="bg-white shadow-lg rounded-xl overflow-hidden">
      <div class="px-6 py-8 text-center">
        <svg xmlns="http://www.w3.org/2000/svg" class="h-16 w-16 mx-auto text-gray-400 mb-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M20 7l-8-4-8 4m16 0l-8 4m8-4v10l-8 4m0-10L4 7m8 4v10M4 7v10l8 4" />
        </svg>
        <h3 class="text-lg leading-6 font-medium text-gray-900 mb-2">No products found</h3>
        <div class="mt-2 max-w-xl text-sm text-gray-500 mx-auto mb-6">
          <p>Get started by adding your first product.</p>
        </div>
        <button
          @click="openAddModal"
          class="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-primary-600 hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500 transition-colors duration-150"
        >
          <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 mr-1.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
          </svg>
          Add Product
        </button>
      </div>
    </div>
    
    <div v-else class="bg-white shadow-lg rounded-xl overflow-hidden">
      <ul role="list" class="divide-y divide-gray-200">
        <li v-for="product in filteredProducts" :key="product.id" class="px-4 sm:px-6 py-4 sm:py-5 hover:bg-gray-50 transition-colors duration-150">
          <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
            <div class="flex items-start sm:items-center">
              <div class="relative flex-shrink-0 h-14 w-14 bg-gray-100 rounded-lg overflow-hidden shadow-sm">
                <img 
                  v-if="product.image_url" 
                  :src="product.image_url" 
                  :alt="product.name" 
                  class="h-full w-full object-cover"
                  @error="handleImageError($event, product)"
                >
                <div v-else class="h-full w-full flex items-center justify-center text-gray-400">
                  <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
                  </svg>
                </div>
                <!-- Inventory badge -->
                <div class="absolute -top-2 -right-2 h-6 w-6 flex items-center justify-center bg-purple-500 text-white text-xs font-bold rounded-full shadow-md">
                  {{ product.inventory_quantity || 0 }}
                </div>
              </div>
              <div class="ml-4">
                <p class="text-sm font-medium text-primary-600">{{ product.name }}</p>
                <div class="flex flex-wrap gap-2 mt-1">
                  <p class="text-sm text-gray-500 flex items-center">
                    <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 mr-1 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                    </svg>
                    ${{ product.cost_price.toFixed(2) }}
                  </p>
                  <span class="px-2 inline-flex text-xs leading-5 font-semibold rounded-full" :class="product.product_type === 'Soda' ? 'bg-blue-100 text-blue-800' : 'bg-green-100 text-green-800'">
                    {{ product.product_type }}
                  </span>
                  <span class="px-2 inline-flex text-xs leading-5 font-semibold rounded-full bg-purple-100 text-purple-800">
                    <svg xmlns="http://www.w3.org/2000/svg" class="h-3.5 w-3.5 mr-0.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M20 7l-8-4-8 4m16 0l-8 4m8-4v10l-8 4m0-10L4 7m8 4v10M4 7v10l8 4" />
                    </svg>
                    {{ product.inventory_quantity || 0 }} in stock
                  </span>
                </div>
              </div>
            </div>
            <div class="flex flex-wrap gap-2 sm:flex-nowrap">
              <button
                @click="editProduct(product)"
                class="w-full sm:w-auto inline-flex items-center justify-center px-3 py-1.5 border border-gray-300 shadow-sm text-xs font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500 transition-colors duration-150"
              >
                <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 mr-1" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
                </svg>
                Edit
              </button>
              <button
                @click="viewCostHistory(product)"
                class="w-full sm:w-auto inline-flex items-center justify-center px-3 py-1.5 border border-gray-300 shadow-sm text-xs font-medium rounded-md text-gray-700 bg-white hover:bg-indigo-50 hover:text-indigo-700 hover:border-indigo-300 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 transition-colors duration-150"
              >
                <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 mr-1" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
                </svg>
                Cost History
              </button>
              <button
                @click="confirmDelete(product)"
                class="w-full sm:w-auto inline-flex items-center justify-center px-3 py-1.5 border border-gray-300 shadow-sm text-xs font-medium rounded-md text-gray-700 bg-white hover:bg-red-50 hover:text-red-700 hover:border-red-300 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-red-500 transition-colors duration-150"
              >
                <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 mr-1" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                </svg>
                Delete
              </button>
            </div>
          </div>
        </li>
      </ul>
    </div>
    
    <!-- Add/Edit Modal -->
    <div v-if="showModal" class="fixed inset-0 overflow-y-auto z-50" aria-labelledby="modal-title" role="dialog" aria-modal="true">
      <div class="flex items-end justify-center min-h-screen pt-4 px-4 pb-20 text-center sm:block sm:p-0">
        <div class="fixed inset-0 bg-gray-500 bg-opacity-75 transition-opacity" aria-hidden="true" @click="showModal = false"></div>
        
        <span class="hidden sm:inline-block sm:align-middle sm:h-screen" aria-hidden="true">&#8203;</span>
        
        <div class="inline-block align-bottom bg-white rounded-xl text-left overflow-hidden shadow-xl transform transition-all sm:my-8 sm:align-middle sm:max-w-lg sm:w-full">
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
                      <label for="product_type" class="block text-sm font-medium text-gray-700">Product Type</label>
                      <select 
                        id="product_type" 
                        name="product_type" 
                        v-model="productForm.product_type"
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
                          v-model="productForm.cost_price"
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
                          v-model="productForm.inventory_quantity"
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
                        v-model="productForm.description"
                        class="shadow-sm focus:ring-primary-500 focus:border-primary-500 mt-1 block w-full sm:text-sm border border-gray-300 rounded-md"
                      ></textarea>
                    </div>
                    <div>
                      <label for="image_url" class="block text-sm font-medium text-gray-700">Image URL</label>
                      <input 
                        type="url" 
                        name="image_url" 
                        id="image_url" 
                        v-model="productForm.image_url"
                        placeholder="https://example.com/image.jpg"
                        class="mt-1 focus:ring-primary-500 focus:border-primary-500 block w-full shadow-sm sm:text-sm border-gray-300 rounded-md"
                      >
                    </div>
                    <div v-if="isEditing" class="mt-4 bg-gray-50 p-3 rounded-md">
                      <h4 class="text-sm font-medium text-gray-700 mb-2">Additional Information:</h4>
                      <div class="grid grid-cols-2 gap-2">
                        <div>
                          <span class="text-xs text-gray-500">Latest Unit Cost:</span>
                          <p class="text-sm font-medium text-primary-600">${{ productForm.id ? (products.find(p => p.id === productForm.id)?.latest_cost || '0.00') : '0.00' }}</p>
                        </div>
                        <div>
                          <span class="text-xs text-gray-500">Average Cost:</span>
                          <p class="text-sm font-medium text-primary-600">${{ productForm.id ? (products.find(p => p.id === productForm.id)?.average_cost || '0.00') : '0.00' }}</p>
                        </div>
                      </div>
                    </div>
                    
                    <div v-if="productForm.image_url" class="mt-3">
                      <h4 class="text-sm font-medium text-gray-700 mb-2">Image Preview:</h4>
                      <div class="h-32 w-32 rounded-lg overflow-hidden bg-gray-100 shadow-sm">
                        <img :src="productForm.image_url" class="h-full w-full object-cover" @error="handleImageError($event)">
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
            <div class="bg-gray-50 px-4 py-3 sm:px-6 sm:flex sm:flex-row-reverse">
              <button 
                type="submit"
                class="w-full inline-flex justify-center rounded-md border border-transparent shadow-sm px-4 py-2 bg-primary-600 text-base font-medium text-white hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500 sm:ml-3 sm:w-auto sm:text-sm transition-colors duration-150"
              >
                {{ isEditing ? 'Update' : 'Add' }}
              </button>
              <button 
                type="button"
                @click="showModal = false"
                class="mt-3 w-full inline-flex justify-center rounded-md border border-gray-300 shadow-sm px-4 py-2 bg-white text-base font-medium text-gray-700 hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500 sm:mt-0 sm:ml-3 sm:w-auto sm:text-sm transition-colors duration-150"
              >
                Cancel
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
    
    <!-- Delete Confirmation Modal -->
    <div v-if="showDeleteModal" class="fixed inset-0 overflow-y-auto z-50" aria-labelledby="modal-title" role="dialog" aria-modal="true">
      <div class="flex items-end justify-center min-h-screen pt-4 px-4 pb-20 text-center sm:block sm:p-0">
        <div class="fixed inset-0 bg-gray-500 bg-opacity-75 transition-opacity" aria-hidden="true" @click="showDeleteModal = false"></div>
        
        <span class="hidden sm:inline-block sm:align-middle sm:h-screen" aria-hidden="true">&#8203;</span>
        
        <div class="inline-block align-bottom bg-white rounded-xl text-left overflow-hidden shadow-xl transform transition-all sm:my-8 sm:align-middle sm:max-w-lg sm:w-full">
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
              class="w-full inline-flex justify-center rounded-md border border-transparent shadow-sm px-4 py-2 bg-red-600 text-base font-medium text-white hover:bg-red-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-red-500 sm:ml-3 sm:w-auto sm:text-sm transition-colors duration-150"
            >
              Delete
            </button>
            <button 
              type="button"
              @click="showDeleteModal = false"
              class="mt-3 w-full inline-flex justify-center rounded-md border border-gray-300 shadow-sm px-4 py-2 bg-white text-base font-medium text-gray-700 hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500 sm:mt-0 sm:ml-3 sm:w-auto sm:text-sm transition-colors duration-150"
            >
              Cancel
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Add Cost History Modal -->
    <div v-if="showCostHistoryModal" class="fixed inset-0 overflow-y-auto z-50" aria-labelledby="modal-title" role="dialog" aria-modal="true">
      <div class="flex items-end justify-center min-h-screen pt-4 px-4 pb-20 text-center sm:block sm:p-0">
        <div class="fixed inset-0 bg-gray-500 bg-opacity-75 transition-opacity" aria-hidden="true" @click="showCostHistoryModal = false"></div>
        
        <span class="hidden sm:inline-block sm:align-middle sm:h-screen" aria-hidden="true">&#8203;</span>
        
        <div class="inline-block align-bottom bg-white rounded-xl text-left overflow-hidden shadow-xl transform transition-all sm:my-8 sm:align-middle sm:max-w-3xl sm:w-full">
          <div class="bg-white px-4 pt-5 pb-4 sm:p-6 sm:pb-4">
            <div class="sm:flex sm:items-start">
              <div class="mt-3 text-center sm:mt-0 sm:text-left w-full">
                <h3 class="text-lg leading-6 font-medium text-gray-900" id="modal-title">
                  Cost History for {{ selectedProduct?.name || 'Product' }}
                </h3>
                
                <div class="mt-4">
                  <div v-if="loadingCostHistory" class="flex justify-center py-10">
                    <div class="animate-spin rounded-full h-10 w-10 border-t-2 border-b-2 border-primary-500"></div>
                  </div>
                  
                  <div v-else-if="costHistoryError" class="bg-red-50 border-l-4 border-red-400 p-4 rounded-r-lg shadow-sm">
                    <div class="flex">
                      <div class="flex-shrink-0">
                        <svg class="h-5 w-5 text-red-400" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor">
                          <path fill-rule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clip-rule="evenodd" />
                        </svg>
                      </div>
                      <div class="ml-3">
                        <p class="text-sm text-red-700">{{ costHistoryError }}</p>
                      </div>
                    </div>
                  </div>
                  
                  <div v-else-if="costHistory.length === 0" class="py-8 text-center">
                    <svg xmlns="http://www.w3.org/2000/svg" class="h-12 w-12 mx-auto text-gray-400 mb-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                    </svg>
                    <h3 class="text-base font-medium text-gray-900">No cost history found</h3>
                    <p class="mt-1 text-sm text-gray-500">This product has no recorded cost history.</p>
                  </div>
                  
                  <div v-else>
                    <div class="overflow-x-auto">
                      <table class="min-w-full divide-y divide-gray-200">
                        <thead class="bg-gray-50">
                          <tr>
                            <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Date</th>
                            <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Quantity</th>
                            <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Unit Cost</th>
                            <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Total Cost</th>
                            <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Supplier</th>
                            <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Notes</th>
                          </tr>
                        </thead>
                        <tbody class="bg-white divide-y divide-gray-200">
                          <tr v-for="entry in costHistory" :key="entry.id">
                            <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                              {{ formatDate(entry.date) }}
                            </td>
                            <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                              {{ entry.quantity }}
                            </td>
                            <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                              ${{ Number(entry.unit_cost).toFixed(2) }}
                            </td>
                            <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                              ${{ Number(entry.total_cost).toFixed(2) }}
                            </td>
                            <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                              {{ entry.supplier }}
                            </td>
                            <td class="px-6 py-4 text-sm text-gray-500">
                              {{ entry.purchase_notes }}
                            </td>
                          </tr>
                        </tbody>
                      </table>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
          <div class="bg-gray-50 px-4 py-3 sm:px-6 sm:flex sm:flex-row-reverse">
            <button 
              type="button"
              @click="showCostHistoryModal = false"
              class="w-full inline-flex justify-center rounded-md border border-gray-300 shadow-sm px-4 py-2 bg-white text-base font-medium text-gray-700 hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500 sm:ml-3 sm:w-auto sm:text-sm transition-colors duration-150"
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
import { api, getImageUrl } from '../services/api'
import { formatDate } from '../utils/dateUtils'

const products = ref([])
const loading = ref(true)
const error = ref(null)
const searchQuery = ref('')
const selectedProductType = ref('')

// Modal states
const showModal = ref(false)
const showDeleteModal = ref(false)
const isEditing = ref(false)
const productToDelete = ref(null)
const showCostHistoryModal = ref(false)
const costHistory = ref([])
const loadingCostHistory = ref(false)
const costHistoryError = ref(null)
const selectedProduct = ref(null)

// Form for creating/editing a product
const productForm = ref({
  id: null,
  name: '',
  product_type: 'Soda',
  description: '',
  cost_price: 0,
  inventory_quantity: 0,
  image_url: ''
})

// Computed property for filtered products
const filteredProducts = computed(() => {
  let filtered = products.value

  // Filter by search query
  if (searchQuery.value.trim()) {
    const query = searchQuery.value.toLowerCase().trim()
    filtered = filtered.filter(product => 
      product.name.toLowerCase().includes(query)
    )
  }

  // Filter by product type
  if (selectedProductType.value) {
    filtered = filtered.filter(product => 
      product.product_type === selectedProductType.value
    )
  }

  return filtered
})

// Clear search function
const clearSearch = () => {
  searchQuery.value = ''
}

// Clear all filters function
const clearAllFilters = () => {
  searchQuery.value = ''
  selectedProductType.value = ''
}

// Handle image loading error
const handleImageError = (event, product) => {
  console.error('Image load error:', event.target.src)
  
  // Just log the error for debugging without changing the image
  if (product) {
    console.warn(`Failed to load image for product: ${product.name}`, product.image_url)
  }
}

// Fetch all products
const fetchProducts = async () => {
  loading.value = true
  try {
    const response = await api.getProducts()
    products.value = response.data
    
    // Log product data for debugging
    console.log('Products loaded:', products.value.length)
    products.value.forEach(product => {
      if (!product.image_url) {
        console.warn('Product missing image URL:', product.name)
      }
    })
  } catch (err) {
    console.error('Error fetching products:', err)
    error.value = 'Failed to load products. Please try again later.'
  } finally {
    loading.value = false
  }
}

// Open modal to add a new product
const openAddModal = () => {
  isEditing.value = false
  productForm.value = {
    id: null,
    name: '',
    product_type: 'Soda',
    description: '',
    cost_price: 0,
    inventory_quantity: 0,
    image_url: ''
  }
  showModal.value = true
}

// Open modal to edit an existing product
const editProduct = (product) => {
  isEditing.value = true
  productForm.value = {
    id: product.id,
    name: product.name,
    product_type: product.product_type || 'Soda',
    description: product.description || '',
    cost_price: product.cost_price,
    inventory_quantity: product.inventory_quantity || 0,
    image_url: product.image_url || ''
  }
  
  showModal.value = true
}

// Save the product (create or update)
const saveProduct = async () => {
  try {
    console.log('Product form data before saving:', JSON.stringify(productForm.value))
    
    if (isEditing.value) {
      const response = await api.updateProduct(productForm.value.id, productForm.value)
      console.log('Product updated successfully:', response.data)
    } else {
      console.log('Sending product data:', JSON.stringify(productForm.value))
      const response = await api.createProduct(productForm.value)
      console.log('Product created successfully:', response.data)
    }
    
    showModal.value = false
    await fetchProducts()
  } catch (err) {
    console.error('Error saving product:', err)
    console.error('Error details:', err.response?.data || err.message)
    error.value = err.response?.data?.detail || 'Failed to save product. Please try again.'
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

// Function to view cost history
const viewCostHistory = async (product) => {
  selectedProduct.value = product
  showCostHistoryModal.value = true
  loadingCostHistory.value = true
  costHistoryError.value = null
  costHistory.value = []
  
  try {
    const response = await api.getProductCostHistory(product.id)
    costHistory.value = response.data
  } catch (err) {
    console.error('Error fetching cost history:', err)
    costHistoryError.value = 'Failed to load cost history. Please try again later.'
  } finally {
    loadingCostHistory.value = false
  }
}

// Initialize data on component mount
onMounted(fetchProducts)
</script> 