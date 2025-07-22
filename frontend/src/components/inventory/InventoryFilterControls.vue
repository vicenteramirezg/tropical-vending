<template>
  <div class="bg-white shadow rounded-lg p-6 mb-6">
    <h3 class="text-lg font-medium text-gray-900 mb-4">Filter Options</h3>
    
    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
      <!-- Location Filter -->
      <div>
        <label for="location" class="block text-sm font-medium text-gray-700 mb-1">
          Location
        </label>
        <select
          id="location"
          v-model="localFilters.location"
          class="block w-full rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500 sm:text-sm"
        >
          <option value="">All Locations</option>
          <option v-for="location in locations" :key="location.id" :value="location.id">
            {{ location.name }}
          </option>
        </select>
      </div>

      <!-- Product Filter -->
      <div>
        <label for="product" class="block text-sm font-medium text-gray-700 mb-1">
          Product
        </label>
        <select
          id="product"
          v-model="localFilters.product"
          class="block w-full rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500 sm:text-sm"
        >
          <option value="">All Products</option>
          <option v-for="product in products" :key="product.id" :value="product.id">
            {{ product.name }}
          </option>
        </select>
      </div>

      <!-- Time Period Filter -->
      <div>
        <label for="timePeriod" class="block text-sm font-medium text-gray-700 mb-1">
          Time Period
        </label>
        <select
          id="timePeriod"
          v-model="timePeriod"
          @change="handleTimePeriodChange"
          class="block w-full rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500 sm:text-sm"
        >
          <option value="7">Past 7 days</option>
          <option value="14">Past 2 weeks</option>
          <option value="30">Past month</option>
          <option value="90">Past 3 months</option>
          <option value="custom">Custom range</option>
        </select>
      </div>

      <!-- Analysis Days Filter (for Stock Coverage) -->
      <div>
        <label for="analysisDays" class="block text-sm font-medium text-gray-700 mb-1">
          Analysis Period
        </label>
        <select
          id="analysisDays"
          v-model="localFilters.analysisDays"
          class="block w-full rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500 sm:text-sm"
        >
          <option value="7">7 days</option>
          <option value="14">2 weeks</option>
          <option value="30">30 days</option>
          <option value="60">60 days</option>
          <option value="90">90 days</option>
        </select>
      </div>
    </div>

    <!-- Custom Date Range (shown when custom is selected) -->
    <div v-if="timePeriod === 'custom'" class="mt-4 grid grid-cols-1 md:grid-cols-2 gap-4">
      <div>
        <label for="startDate" class="block text-sm font-medium text-gray-700 mb-1">
          Start Date
        </label>
        <input
          id="startDate"
          type="date"
          v-model="localFilters.startDate"
          class="block w-full rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500 sm:text-sm"
        >
      </div>
      <div>
        <label for="endDate" class="block text-sm font-medium text-gray-700 mb-1">
          End Date
        </label>
        <input
          id="endDate"
          type="date"
          v-model="localFilters.endDate"
          class="block w-full rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500 sm:text-sm"
        >
      </div>
    </div>

    <!-- Action Buttons -->
    <div class="mt-6 flex justify-end space-x-3">
      <button
        @click="clearFilters"
        class="inline-flex items-center px-4 py-2 border border-gray-300 shadow-sm text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500"
      >
        Clear Filters
      </button>
      <button
        @click="applyFilters"
        class="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-primary-600 hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500"
      >
        Apply Filters
      </button>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, watch } from 'vue'

const props = defineProps({
  filters: {
    type: Object,
    required: true
  },
  locations: {
    type: Array,
    default: () => []
  },
  products: {
    type: Array,
    default: () => []
  }
})

const emit = defineEmits(['apply-filters', 'update-filters'])

// Local filters to manage form state
const localFilters = reactive({
  location: props.filters.location || '',
  product: props.filters.product || '',
  startDate: props.filters.startDate || '',
  endDate: props.filters.endDate || '',
  days: props.filters.days || '7',
  analysisDays: props.filters.analysisDays || '30'
})

// Time period selection
const timePeriod = ref(props.filters.days || '7')

// Handle time period change
const handleTimePeriodChange = () => {
  if (timePeriod.value !== 'custom') {
    localFilters.days = timePeriod.value
    localFilters.startDate = ''
    localFilters.endDate = ''
  } else {
    localFilters.days = ''
    // Set default custom range (last 7 days)
    const today = new Date()
    const weekAgo = new Date(today)
    weekAgo.setDate(today.getDate() - 7)
    
    localFilters.endDate = today.toISOString().split('T')[0]
    localFilters.startDate = weekAgo.toISOString().split('T')[0]
  }
}

// Apply filters
const applyFilters = () => {
  // Update parent filters
  Object.assign(props.filters, localFilters)
  emit('apply-filters')
}

// Clear filters
const clearFilters = () => {
  localFilters.location = ''
  localFilters.product = ''
  localFilters.startDate = ''
  localFilters.endDate = ''
  localFilters.days = '7'
  localFilters.analysisDays = '30'
  timePeriod.value = '7'
  
  // Update parent filters
  Object.assign(props.filters, localFilters)
  emit('apply-filters')
}

// Watch for external filter changes
watch(() => props.filters, (newFilters) => {
  Object.assign(localFilters, newFilters)
  timePeriod.value = newFilters.days || (newFilters.startDate && newFilters.endDate ? 'custom' : '7')
}, { deep: true })
</script> 