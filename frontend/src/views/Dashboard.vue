<template>
  <div class="min-h-screen flex flex-col">
    <div class="flex-grow container mx-auto px-4 py-8">
      <h1 class="text-2xl font-bold text-gray-900 mb-6">Dashboard</h1>
      
      <!-- Filter Controls -->
      <FilterControls 
        :filters="filters" 
        :locations="locations" 
        @apply-filters="applyFilters" 
      />
      
      <!-- Error Message -->
      <div v-if="error" class="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-6">
        {{ error }}
      </div>
      
      <!-- Loading State -->
      <LoadingSpinner v-if="loading" />
      
      <!-- Dashboard Content -->
      <div v-else>
        <!-- KPI Cards -->
        <KpiCards :data="data" />
        
        <!-- Low Stock Items -->
        <LowStockItems :data="data" :get-stock-level-class="getStockLevelClass" />
        
        <!-- Revenue & Profit Summary -->
        <RevenueSummary :data="data" />
      </div>
    </div>
    
    <!-- Footer -->
    <AppFooter />
  </div>
</template>

<script setup>
import { onMounted } from 'vue'
import { useDashboard } from '../composables/useDashboard'
import AppFooter from '../components/AppFooter.vue'
import FilterControls from '../components/dashboard/FilterControls.vue'
import KpiCards from '../components/dashboard/KpiCards.vue'
import LowStockItems from '../components/dashboard/LowStockItems.vue'
import RevenueSummary from '../components/dashboard/RevenueSummary.vue'
import LoadingSpinner from '../components/dashboard/LoadingSpinner.vue'

// Use the dashboard composable
const {
  loading,
  error,
  locations,
  data,
  filters,
  applyFilters,
  initializeDashboard,
  getStockLevelClass
} = useDashboard()

// Initialize dashboard on mount
onMounted(() => {
  initializeDashboard()
})
</script> 