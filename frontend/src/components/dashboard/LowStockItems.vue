<template>
  <div class="bg-white shadow-lg overflow-hidden sm:rounded-xl mb-8 transition-all duration-300 hover:shadow-xl">
    <div class="px-6 py-5 border-b border-gray-100 flex justify-between items-center">
      <div>
        <h3 class="text-lg leading-6 font-medium text-gray-900">Low Stock Items</h3>
        <p class="mt-1 text-sm text-gray-500">
          Products with stock level below threshold
          <span v-if="data.low_stock_items.length > 0" class="text-gray-400">
            ({{ startIndex + 1 }}-{{ endIndex }} of {{ data.low_stock_items.length }})
          </span>
        </p>
      </div>
      <div class="flex items-center space-x-3">
        <span 
          class="inline-flex items-center px-3.5 py-1 rounded-full text-sm font-medium"
          :class="data.low_stock_count > 0 ? 'bg-red-100 text-red-800' : 'bg-green-100 text-green-800'"
        >
          {{ data.low_stock_count }} items
        </span>
        <router-link 
          to="/inventory" 
          class="inline-flex items-center px-3 py-1.5 border border-transparent text-xs font-medium rounded-md text-primary-600 bg-primary-100 hover:bg-primary-200 transition-colors duration-150"
        >
          <svg class="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"></path>
          </svg>
          Full Report
        </router-link>
      </div>
    </div>
    
    <div>
      <div v-if="data.low_stock_items.length === 0" class="px-6 py-8 text-center text-gray-500">
        <svg xmlns="http://www.w3.org/2000/svg" class="h-12 w-12 mx-auto text-green-400 mb-3" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
        </svg>
        <p class="text-lg font-medium">No low stock items - everything is well stocked!</p>
      </div>
      
      <div v-else>
        <!-- Items List -->
        <ul role="list" class="divide-y divide-gray-200">
          <li v-for="(item, index) in paginatedItems" :key="index" class="px-6 py-4 hover:bg-gray-50 transition-colors duration-150">
            <div class="flex items-center justify-between">
              <div class="flex-1 min-w-0">
                <div class="flex items-center">
                  <div class="flex-shrink-0">
                    <div class="w-2 h-2 rounded-full" :class="getStockIndicatorColor(item.current_stock)"></div>
                  </div>
                  <div class="ml-3 min-w-0 flex-1">
                    <p class="text-sm font-medium text-primary-600 truncate">{{ item.product }}</p>
                    <p class="text-sm text-gray-500 truncate">{{ item.machine }} • {{ item.location }}</p>
                  </div>
                </div>
              </div>
              <div class="flex items-center space-x-2">
                <div class="text-right">
                  <div class="text-sm font-medium text-gray-900">${{ (item.price || 0).toFixed(2) }}</div>
                  <div class="text-xs text-gray-500">Price</div>
                </div>
                <span 
                  class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium"
                  :class="getStockLevelClass(item.current_stock)"
                >
                  {{ item.current_stock }}
                </span>
              </div>
            </div>
          </li>
        </ul>
        
        <!-- Pagination Controls -->
        <div v-if="totalPages > 1" class="bg-gray-50 px-6 py-3 border-t border-gray-200">
          <div class="flex items-center justify-between">
            <div class="flex items-center space-x-2">
              <span class="text-sm text-gray-700">
                Page {{ currentPage }} of {{ totalPages }}
              </span>
              <select
                v-model="itemsPerPage"
                @change="currentPage = 1"
                class="text-sm border-gray-300 rounded-md focus:ring-primary-500 focus:border-primary-500"
              >
                <option value="5">5 per page</option>
                <option value="10">10 per page</option>
                <option value="15">15 per page</option>
                <option value="20">20 per page</option>
              </select>
            </div>
            
            <nav class="flex items-center space-x-1">
              <button
                @click="currentPage = 1"
                :disabled="currentPage === 1"
                class="inline-flex items-center px-2 py-1 text-xs font-medium text-gray-500 bg-white border border-gray-300 rounded-md hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                First
              </button>
              <button
                @click="currentPage--"
                :disabled="currentPage === 1"
                class="inline-flex items-center px-2 py-1 text-xs font-medium text-gray-500 bg-white border border-gray-300 rounded-md hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                <svg class="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7" />
                </svg>
                Prev
              </button>
              
              <!-- Page Numbers -->
              <div class="flex space-x-1">
                <button
                  v-for="page in visiblePages"
                  :key="page"
                  @click="currentPage = page"
                  :class="[
                    'inline-flex items-center px-3 py-1 text-xs font-medium rounded-md',
                    page === currentPage
                      ? 'text-white bg-primary-600 border border-primary-600'
                      : 'text-gray-700 bg-white border border-gray-300 hover:bg-gray-50'
                  ]"
                >
                  {{ page }}
                </button>
              </div>
              
              <button
                @click="currentPage++"
                :disabled="currentPage === totalPages"
                class="inline-flex items-center px-2 py-1 text-xs font-medium text-gray-500 bg-white border border-gray-300 rounded-md hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                Next
                <svg class="w-3 h-3 ml-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" />
                </svg>
              </button>
              <button
                @click="currentPage = totalPages"
                :disabled="currentPage === totalPages"
                class="inline-flex items-center px-2 py-1 text-xs font-medium text-gray-500 bg-white border border-gray-300 rounded-md hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                Last
              </button>
            </nav>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch } from 'vue'

const props = defineProps({
  data: {
    type: Object,
    required: true
  },
  getStockLevelClass: {
    type: Function,
    required: true
  }
})

// Pagination state
const currentPage = ref(1)
const itemsPerPage = ref(10)

// Reset to first page when data changes
watch(() => props.data.low_stock_items, () => {
  currentPage.value = 1
})

// Computed properties for pagination
const totalPages = computed(() => {
  return Math.ceil((props.data.low_stock_items?.length || 0) / itemsPerPage.value)
})

const startIndex = computed(() => {
  return (currentPage.value - 1) * itemsPerPage.value
})

const endIndex = computed(() => {
  return Math.min(startIndex.value + itemsPerPage.value, props.data.low_stock_items?.length || 0)
})

const paginatedItems = computed(() => {
  if (!props.data.low_stock_items) return []
  return props.data.low_stock_items.slice(startIndex.value, endIndex.value)
})

// Visible page numbers (show max 5 pages around current page)
const visiblePages = computed(() => {
  const total = totalPages.value
  const current = currentPage.value
  const delta = 2
  
  const range = []
  const rangeWithDots = []
  
  for (let i = Math.max(2, current - delta); i <= Math.min(total - 1, current + delta); i++) {
    range.push(i)
  }
  
  if (current - delta > 2) {
    rangeWithDots.push(1, '...')
  } else {
    rangeWithDots.push(1)
  }
  
  rangeWithDots.push(...range)
  
  if (current + delta < total - 1) {
    rangeWithDots.push('...', total)
  } else if (total > 1) {
    rangeWithDots.push(total)
  }
  
  return rangeWithDots.filter((item, index, arr) => {
    // Remove duplicate 1s and totals
    if (item === 1 && index > 0 && arr[index - 1] === 1) return false
    if (item === total && index < arr.length - 1 && arr[index + 1] === total) return false
    return true
  }).slice(0, 7) // Limit to 7 items max
})

// Stock indicator color (small dot)
const getStockIndicatorColor = (quantity) => {
  if (quantity <= 0) return 'bg-red-500'
  if (quantity <= 3) return 'bg-yellow-500'
  return 'bg-blue-500'
}
</script> 