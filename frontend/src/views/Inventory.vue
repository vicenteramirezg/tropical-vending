<template>
  <div>
    <h1 class="text-2xl font-semibold text-gray-900 mb-6">Inventory Reports</h1>
    
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
    
    <div v-else>
      <!-- Filter Controls -->
      <InventoryFilterControls
        :filters="filters"
        :locations="locations"
        :products="products"
        @apply-filters="applyFilters"
        @update-filters="updateFilters"
      />
      
      <!-- Report Tabs -->
      <div class="mb-6">
        <div class="border-b border-gray-200">
          <nav class="-mb-px flex space-x-8" aria-label="Tabs">
            <button
              v-for="tab in tabs"
              :key="tab.id"
              @click="activeTab = tab.id"
              :class="[
                activeTab === tab.id
                  ? 'border-primary-500 text-primary-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300',
                'whitespace-nowrap py-2 px-1 border-b-2 font-medium text-sm'
              ]"
            >
              {{ tab.name }}
            </button>
          </nav>
        </div>
      </div>
      
      <!-- Current Stock Report -->
      <CurrentStockReport 
        v-show="activeTab === 'current-stock'"
        :data="currentStockData" 
        :loading="currentStockLoading"
      />
      
      <!-- Restock Summary -->
      <RestockSummary 
        v-show="activeTab === 'restock-summary'"
        :data="restockSummaryData" 
        :loading="restockSummaryLoading"
        :filters="filters"
      />
      
      <!-- Stock Coverage Estimate -->
      <StockCoverageEstimate 
        v-show="activeTab === 'stock-coverage'"
        :data="stockCoverageData" 
        :loading="stockCoverageLoading"
      />
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useInventoryReports } from '../composables/useInventoryReports'
import InventoryFilterControls from '../components/inventory/InventoryFilterControls.vue'
import CurrentStockReport from '../components/inventory/CurrentStockReport.vue'
import RestockSummary from '../components/inventory/RestockSummary.vue'
import StockCoverageEstimate from '../components/inventory/StockCoverageEstimate.vue'

// Active tab management
const activeTab = ref('current-stock')

const tabs = [
  { id: 'current-stock', name: 'Current Stock' },
  { id: 'restock-summary', name: 'Restock Summary' },
  { id: 'stock-coverage', name: 'Stock Coverage' }
]

// Use the inventory reports composable
const {
  loading,
  error,
  locations,
  products,
  filters,
  currentStockData,
  currentStockLoading,
  restockSummaryData,
  restockSummaryLoading,
  stockCoverageData,
  stockCoverageLoading,
  applyFilters,
  initialize
} = useInventoryReports()

// Handle filter updates from child components
const updateFilters = (updatedFilters) => {
  Object.assign(filters.value, updatedFilters)
}

// Initialize data on component mount
onMounted(() => {
  initialize()
})
</script> 