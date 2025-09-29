<template>
  <div class="min-h-screen flex flex-col bg-gray-50">
    <div class="flex-grow container mx-auto px-4 py-8">
      <!-- Header -->
      <div class="mb-8">
        <h1 class="text-3xl font-bold text-gray-900">Analytics Dashboard</h1>
        <p class="mt-2 text-gray-600">Comprehensive insights into your vending business performance</p>
      </div>
      
      <!-- Filter Controls -->
      <FilterControls 
        :filters="filters" 
        :locations="locations"
        :machines="machines"
        :products="products"
        @apply-filters="applyFilters"
        @export-data="exportData"
      />
      
      <!-- Error Message -->
      <div v-if="error" class="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded-lg mb-6 shadow-sm">
        <div class="flex items-center">
          <svg class="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.732-.833-2.5 0L4.268 14.5c-.77.833.192 2.5 1.732 2.5z" />
          </svg>
          {{ error }}
        </div>
      </div>
      
      <!-- Loading State -->
      <LoadingSpinner v-if="loading" />
      
      <!-- Dashboard Content -->
      <div v-else class="space-y-8">
        <!-- KPI Cards with Insights -->
        <KpiCards :data="data" />
        
        <!-- Performance Charts Row -->
        <div class="grid grid-cols-1 lg:grid-cols-2 gap-8">
          <!-- Product Performance -->
          <ProductPerformance 
            :products="data.products?.top_performers || []"
          />
          
          <!-- Machine Performance -->
          <MachinePerformance 
            :machines="data.machines?.top_performers || []"
          />
        </div>
        
        <!-- Location Performance -->
        <LocationPerformance 
          v-if="data.locations?.performance && data.locations.performance.length > 0"
          :locations="data.locations.performance"
        />
        
        <!-- Legacy Components (for backward compatibility) -->
        <div class="grid grid-cols-1 lg:grid-cols-2 gap-8">
          <!-- Low Stock Items -->
          <LowStockItems 
            v-if="data.low_stock_items && data.low_stock_items.length > 0"
            :data="data" 
            :get-stock-level-class="getStockLevelClass" 
          />
          
          <!-- Revenue Summary -->
          <RevenueSummary :data="data" />
        </div>
        
        <!-- Additional Analytics Section -->
        <div class="bg-white rounded-xl shadow-lg p-6">
          <div class="flex justify-between items-center mb-6">
            <h3 class="text-lg font-semibold text-gray-900">Detailed Analytics</h3>
            <div class="flex space-x-3">
              <button
                @click="refreshAnalytics"
                :disabled="isAnyLoading"
                class="inline-flex items-center px-3 py-2 border border-gray-300 shadow-sm text-sm leading-4 font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 mr-1" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
                </svg>
                Refresh
              </button>
              <button
                @click="exportData"
                class="inline-flex items-center px-3 py-2 border border-transparent text-sm leading-4 font-medium rounded-md text-white bg-primary-600 hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500"
              >
                <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 mr-1" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                </svg>
                Export Report
              </button>
            </div>
          </div>
          
          <!-- Analytics Summary -->
          <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            <div class="text-center p-4 bg-gray-50 rounded-lg">
              <div class="text-2xl font-bold text-primary-600">
                {{ formatNumber(data.summary?.total_demand_units || 0) }}
              </div>
              <div class="text-sm text-gray-600">Total Units Sold</div>
              <div class="text-xs text-gray-500 mt-1">
                Avg: {{ formatNumber(data.summary?.avg_daily_demand || 0) }}/day
              </div>
            </div>
            
            <div class="text-center p-4 bg-gray-50 rounded-lg">
              <div class="text-2xl font-bold text-green-600">
                ${{ formatMoney(data.summary?.total_revenue || 0) }}
              </div>
              <div class="text-sm text-gray-600">Total Revenue</div>
              <div class="text-xs text-gray-500 mt-1">
                {{ data.summary?.total_restocks || 0 }} restocks
              </div>
            </div>
            
            <div class="text-center p-4 bg-gray-50 rounded-lg">
              <div class="text-2xl font-bold text-emerald-600">
                ${{ formatMoney(data.summary?.total_profit || 0) }}
              </div>
              <div class="text-sm text-gray-600">Total Profit</div>
              <div class="text-xs text-gray-500 mt-1">
                {{ (data.summary?.overall_profit_margin || 0).toFixed(1) }}% margin
              </div>
            </div>
            
            <div class="text-center p-4 bg-gray-50 rounded-lg">
              <div class="text-2xl font-bold text-purple-600">
                {{ data.summary?.unique_products || 0 }}
              </div>
              <div class="text-sm text-gray-600">Active Products</div>
              <div class="text-xs text-gray-500 mt-1">
                {{ data.summary?.unique_machines || 0 }} machines
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { onMounted } from 'vue'
import { useDashboard } from '../composables/useDashboard'
import FilterControls from '../components/dashboard/FilterControls.vue'
import KpiCards from '../components/dashboard/KpiCards.vue'
import ProductPerformance from '../components/dashboard/ProductPerformance.vue'
import MachinePerformance from '../components/dashboard/MachinePerformance.vue'
import LocationPerformance from '../components/dashboard/LocationPerformance.vue'
import LowStockItems from '../components/dashboard/LowStockItems.vue'
import RevenueSummary from '../components/dashboard/RevenueSummary.vue'
import LoadingSpinner from '../components/dashboard/LoadingSpinner.vue'

// Use the dashboard composable
const {
  loading,
  error,
  locations,
  machines,
  products,
  data,
  filters,
  loadingStates,
  isAnyLoading,
  applyFilters,
  initializeDashboard,
  refreshSection,
  exportAnalyticsData,
  getStockLevelClass
} = useDashboard()

// Format numbers with K, M notation
const formatNumber = (value) => {
  if (value >= 1000000) {
    return (value / 1000000).toFixed(1) + 'M'
  } else if (value >= 1000) {
    return (value / 1000).toFixed(1) + 'K'
  }
  return Math.round(value).toString()
}

// Format money values
const formatMoney = (value) => {
  if (value >= 1000000) {
    return (value / 1000000).toFixed(1) + 'M'
  } else if (value >= 1000) {
    return (value / 1000).toFixed(1) + 'K'
  }
  return value.toFixed(2)
}

// Export data as CSV
const exportData = async () => {
  const success = await exportAnalyticsData('csv')
  if (success) {
    // Optional: Show success message
    console.log('Export successful')
  }
}

// Refresh analytics data
const refreshAnalytics = async () => {
  await refreshSection('analytics')
}

// Initialize dashboard on mount
onMounted(() => {
  initializeDashboard()
})
</script> 