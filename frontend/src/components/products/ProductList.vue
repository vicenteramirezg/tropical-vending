<template>
  <div class="bg-white shadow-lg rounded-xl overflow-hidden">
    <ul role="list" class="divide-y divide-gray-200">
      <li v-for="product in products" :key="product.id" class="px-4 sm:px-6 py-4 sm:py-5 hover:bg-gray-50 transition-colors duration-150">
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
                <span class="px-2 inline-flex text-xs leading-5 font-semibold rounded-full" :class="getProductTypeBadgeClass(product.product_type)">
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
              @click="$emit('edit', product)"
              class="w-full sm:w-auto inline-flex items-center justify-center px-3 py-1.5 border border-gray-300 shadow-sm text-xs font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500 transition-colors duration-150"
            >
              <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 mr-1" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
              </svg>
              Edit
            </button>
            <button
              @click="$emit('viewCostHistory', product)"
              class="w-full sm:w-auto inline-flex items-center justify-center px-3 py-1.5 border border-gray-300 shadow-sm text-xs font-medium rounded-md text-gray-700 bg-white hover:bg-indigo-50 hover:text-indigo-700 hover:border-indigo-300 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 transition-colors duration-150"
            >
              <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 mr-1" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
              </svg>
              Cost History
            </button>
            <button
              @click="$emit('delete', product)"
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
</template>

<script setup>
const props = defineProps({
  products: {
    type: Array,
    required: true
  }
})

const emit = defineEmits(['edit', 'viewCostHistory', 'delete'])

// Handle image loading error
const handleImageError = (event, product) => {
  console.error('Image load error:', event.target.src)
  
  // Just log the error for debugging without changing the image
  if (product) {
    console.warn(`Failed to load image for product: ${product.name}`, product.image_url)
  }
}

// Get CSS classes for product type badges
const getProductTypeBadgeClass = (productType) => {
  return productType === 'Soda' ? 'bg-blue-100 text-blue-800' : 'bg-green-100 text-green-800'
}
</script> 