<template>
  <div class="bg-white p-4 sm:p-6 shadow-lg rounded-xl mb-6 border border-gray-100">
    <!-- Header with Export Button -->
    <div class="flex justify-between items-center mb-4">
      <h3 class="text-lg font-semibold text-gray-900">Analytics Filters</h3>
      <button
        type="button"
        @click="$emit('export-data')"
        class="inline-flex items-center px-3 py-1.5 border border-gray-300 text-xs font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500 transition-colors duration-150"
      >
        <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 mr-1" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
        </svg>
        Export CSV
      </button>
    </div>

    <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-5 gap-4">
      <!-- Time Range -->
      <div class="space-y-1">
        <label for="timeRange" class="block text-sm font-medium text-gray-700">Time Period</label>
        <select
          id="timeRange"
          v-model="filters.timeRange"
          class="block w-full border-gray-300 rounded-md shadow-sm focus:ring-primary-500 focus:border-primary-500 text-sm"
          @change="$emit('apply-filters')"
        >
          <option value="7">Last 7 days</option>
          <option value="30">Last 30 days</option>
          <option value="60">Last 60 days</option>
          <option value="90">Last 90 days</option>
          <option value="365">Last year</option>
        </select>
      </div>
      
      <!-- Location Filter -->
      <div class="space-y-1">
        <label for="location" class="block text-sm font-medium text-gray-700">Location</label>
        <select
          id="location"
          v-model="filters.location"
          class="block w-full border-gray-300 rounded-md shadow-sm focus:ring-primary-500 focus:border-primary-500 text-sm"
          @change="$emit('apply-filters')"
        >
          <option value="">All Locations</option>
          <option v-for="location in locations" :key="location.id" :value="location.id">
            {{ location.name }}
          </option>
        </select>
      </div>
      
      <!-- Machine Filter -->
      <div class="space-y-1">
        <label for="machine" class="block text-sm font-medium text-gray-700">Machine</label>
        <select
          id="machine"
          v-model="filters.machine"
          class="block w-full border-gray-300 rounded-md shadow-sm focus:ring-primary-500 focus:border-primary-500 text-sm"
          @change="$emit('apply-filters')"
        >
          <option value="">All Machines</option>
          <option v-for="machine in machines" :key="machine.id" :value="machine.id">
            {{ machine.name || `${machine.machine_type} ${machine.model}` }}
          </option>
        </select>
      </div>
      
      <!-- Product Filter -->
      <div class="space-y-1">
        <label for="product" class="block text-sm font-medium text-gray-700">Product</label>
        <select
          id="product"
          v-model="filters.product"
          class="block w-full border-gray-300 rounded-md shadow-sm focus:ring-primary-500 focus:border-primary-500 text-sm"
          @change="$emit('apply-filters')"
        >
          <option value="">All Products</option>
          <option v-for="product in products" :key="product.id" :value="product.id">
            {{ product.name }}
          </option>
        </select>
      </div>
      
      <!-- Apply Button -->
      <div class="flex items-end">
        <button
          type="button"
          @click="$emit('apply-filters')"
          class="w-full inline-flex items-center justify-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-primary-600 hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500 transition-colors duration-150"
        >
          <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 mr-1.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 4a1 1 0 011-1h16a1 1 0 011 1v2.586a1 1 0 01-.293.707l-6.414 6.414a1 1 0 00-.293.707V17l-4 4v-6.586a1 1 0 00-.293-.707L3.293 7.293A1 1 0 013 6.586V4z" />
          </svg>
          Apply
        </button>
      </div>
    </div>
    
    <!-- Date Range Override (Optional) -->
    <div class="mt-4 pt-4 border-t border-gray-200">
      <div class="flex items-center space-x-4">
        <label class="flex items-center">
          <input
            type="checkbox"
            v-model="showDateRange"
            class="rounded border-gray-300 text-primary-600 focus:ring-primary-500"
          />
          <span class="ml-2 text-sm text-gray-700">Custom date range</span>
        </label>
        
        <div v-if="showDateRange" class="flex items-center space-x-2">
          <input
            type="date"
            v-model="filters.startDate"
            class="border-gray-300 rounded-md shadow-sm focus:ring-primary-500 focus:border-primary-500 text-sm"
            @change="$emit('apply-filters')"
          />
          <span class="text-sm text-gray-500">to</span>
          <input
            type="date"
            v-model="filters.endDate"
            class="border-gray-300 rounded-md shadow-sm focus:ring-primary-500 focus:border-primary-500 text-sm"
            @change="$emit('apply-filters')"
          />
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'

defineProps({
  filters: {
    type: Object,
    required: true
  },
  locations: {
    type: Array,
    default: () => []
  },
  machines: {
    type: Array,
    default: () => []
  },
  products: {
    type: Array,
    default: () => []
  }
})

defineEmits(['apply-filters', 'export-data'])

const showDateRange = ref(false)
</script> 