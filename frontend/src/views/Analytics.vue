<template>
  <div>
    <h1 class="text-2xl font-semibold text-gray-900 mb-6">Analytics</h1>
    
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
      <FilterControls
        :filters="filters"
        :locations="locations"
        :machines="machines"
        :products="products"
        :loading-machines="loadingStates.machines"
        :loading-products="loadingStates.products"
        @apply-filters="applyFilters"
        @update-filters="updateFilters"
        @location-changed="handleLocationChange"
        @machine-changed="handleMachineChange"
      />
      
      <!-- Revenue & Profit Section -->
      <RevenueProfit :data="revenueProfitData" />
      
      <!-- Stock Levels Section -->
      <StockLevels :data="stockLevelData" />
      
      <!-- Product Demand Analysis -->
      <DemandAnalysis
        :data="demandData"
        :format-date-short="formatDateShort"
        :format-daily-demand="formatDailyDemand"
        :format-trend="formatTrend"
        :get-trend-class="getTrendClass"
      />
    </div>
  </div>
</template>

<script setup>
import { onMounted } from 'vue'
import { useAnalytics } from '../composables/useAnalytics'
import FilterControls from '../components/analytics/FilterControls.vue'
import RevenueProfit from '../components/analytics/RevenueProfit.vue'
import StockLevels from '../components/analytics/StockLevels.vue'
import DemandAnalysis from '../components/analytics/DemandAnalysis.vue'

// Use the analytics composable
const {
  loading,
  error,
  locations,
  machines,
  products,
  filters,
  revenueProfitData,
  stockLevelData,
  demandData,
  loadingStates,
  formatDateShort,
  formatDailyDemand,
  formatTrend,
  getTrendClass,
  applyFilters,
  initialize,
  fetchMachines,
  fetchProducts
} = useAnalytics()

// Handle filter updates from child components
const updateFilters = (updatedFilters) => {
  Object.assign(filters.value, updatedFilters)
}

// Handle location change - fetch machines for selected location
const handleLocationChange = async (locationId) => {
  if (locationId) {
    await fetchMachines(locationId)
  } else {
    machines.value = []
    products.value = []
  }
}

// Handle machine change - fetch products for selected machine
const handleMachineChange = async (machineId) => {
  if (machineId) {
    await fetchProducts(machineId)
  } else {
    products.value = []
  }
}

// Initialize data on component mount
onMounted(() => {
  initialize()
})
</script> 