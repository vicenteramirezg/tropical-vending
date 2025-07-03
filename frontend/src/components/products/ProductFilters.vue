<template>
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
      <div v-if="hasActiveFilters" class="sm:w-auto">
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
    <div v-if="showFilterSummary" class="mt-3 text-sm text-gray-600">
      <div class="flex flex-wrap items-center gap-2">
        <span>Showing {{ filteredCount }} of {{ totalCount }} products</span>
        <span 
          v-for="filter in activeFilters" 
          :key="filter.type"
          class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium"
          :class="getFilterBadgeClass(filter.color)"
        >
          {{ filter.label }}
          <button 
            @click="removeFilter(filter.type)"
            class="ml-1 text-current hover:text-opacity-75 focus:outline-none"
          >
            <svg class="h-3 w-3" fill="currentColor" viewBox="0 0 20 20">
              <path fill-rule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" clip-rule="evenodd" />
            </svg>
          </button>
        </span>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  searchQuery: {
    type: String,
    required: true
  },
  selectedProductType: {
    type: String,
    required: true
  },
  hasActiveFilters: {
    type: Boolean,
    default: false
  },
  activeFilters: {
    type: Array,
    default: () => []
  },
  filteredCount: {
    type: Number,
    default: 0
  },
  totalCount: {
    type: Number,
    default: 0
  }
})

const emit = defineEmits([
  'update:searchQuery',
  'update:selectedProductType',
  'clearSearch',
  'clearAllFilters',
  'removeFilter'
])

// Computed properties for v-model
const searchQuery = computed({
  get: () => props.searchQuery,
  set: (value) => emit('update:searchQuery', value)
})

const selectedProductType = computed({
  get: () => props.selectedProductType,
  set: (value) => emit('update:selectedProductType', value)
})

// Show filter summary when filters are active and counts differ
const showFilterSummary = computed(() => {
  return props.hasActiveFilters && props.filteredCount !== props.totalCount
})

// Clear search function
const clearSearch = () => {
  emit('clearSearch')
}

// Clear all filters function
const clearAllFilters = () => {
  emit('clearAllFilters')
}

// Remove specific filter
const removeFilter = (filterType) => {
  emit('removeFilter', filterType)
}

// Get CSS classes for filter badges
const getFilterBadgeClass = (color) => {
  const classes = {
    blue: 'bg-blue-100 text-blue-800',
    green: 'bg-green-100 text-green-800',
    purple: 'bg-purple-100 text-purple-800',
    red: 'bg-red-100 text-red-800'
  }
  return classes[color] || 'bg-gray-100 text-gray-800'
}
</script> 