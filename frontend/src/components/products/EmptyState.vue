<template>
  <div class="bg-white shadow-lg rounded-xl overflow-hidden">
    <div class="px-6 py-8 text-center">
      <!-- Empty State Icon -->
      <svg v-if="type === 'empty'" xmlns="http://www.w3.org/2000/svg" class="h-16 w-16 mx-auto text-gray-400 mb-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M20 7l-8-4-8 4m16 0l-8 4m8-4v10l-8 4m0-10L4 7m8 4v10M4 7v10l8 4" />
      </svg>
      
      <!-- No Results Icon -->
      <svg v-else-if="type === 'no-results'" xmlns="http://www.w3.org/2000/svg" class="h-16 w-16 mx-auto text-gray-400 mb-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
      </svg>
      
      <!-- Error Icon -->
      <svg v-else-if="type === 'error'" xmlns="http://www.w3.org/2000/svg" class="h-16 w-16 mx-auto text-gray-400 mb-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
      </svg>
      
      <h3 class="text-lg leading-6 font-medium text-gray-900 mb-2">{{ title }}</h3>
      <div class="mt-2 max-w-xl text-sm text-gray-500 mx-auto mb-6">
        <p>{{ description }}</p>
        <div v-if="activeFilters.length > 0" class="mt-2 flex flex-wrap justify-center gap-2">
          <span 
            v-for="filter in activeFilters" 
            :key="filter.type"
            class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium"
            :class="getFilterBadgeClass(filter.color)"
          >
            {{ filter.label }}
          </span>
        </div>
      </div>
      <button
        v-if="showButton"
        @click="$emit('action')"
        class="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-primary-600 hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500 transition-colors duration-150"
      >
        <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 mr-1.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
        </svg>
        {{ buttonText }}
      </button>
      <button
        v-else-if="showClearFilters"
        @click="$emit('clearFilters')"
        class="inline-flex items-center px-4 py-2 border border-gray-300 shadow-sm text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500 transition-colors duration-150"
      >
        <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
        </svg>
        Clear All Filters
      </button>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  type: {
    type: String,
    default: 'empty', // 'empty', 'no-results', 'error'
    validator: (value) => ['empty', 'no-results', 'error'].includes(value)
  },
  title: {
    type: String,
    default: ''
  },
  description: {
    type: String,
    default: ''
  },
  buttonText: {
    type: String,
    default: 'Add Item'
  },
  showButton: {
    type: Boolean,
    default: false
  },
  showClearFilters: {
    type: Boolean,
    default: false
  },
  activeFilters: {
    type: Array,
    default: () => []
  }
})

const emit = defineEmits(['action', 'clearFilters'])

// Dynamic icon based on type
const iconComponent = computed(() => {
  const icons = {
    empty: 'svg',
    'no-results': 'svg',
    error: 'svg'
  }
  return icons[props.type] || 'svg'
})

// Dynamic button icon
const buttonIcon = computed(() => {
  if (props.type === 'empty') {
    return 'svg' // Plus icon for add action
  }
  return 'svg'
})

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