<template>
  <div class="bg-white p-4 sm:p-5 shadow-lg rounded-xl mb-6">
    <div class="flex flex-col sm:flex-row flex-wrap items-start sm:items-center gap-4">
      <div class="w-full sm:w-auto">
        <label for="timeRange" class="block text-sm font-medium text-gray-700 mb-1">Time Period</label>
        <select
          id="timeRange"
          v-model="filters.timeRange"
          class="block w-full sm:w-48 border-gray-300 rounded-md shadow-sm focus:ring-primary-500 focus:border-primary-500 sm:text-sm"
          @change="$emit('apply-filters')"
        >
          <option value="today">Today</option>
          <option value="yesterday">Yesterday</option>
          <option value="7">Last 7 days</option>
          <option value="30">Last 30 days</option>
          <option value="90">Last 90 days</option>
        </select>
      </div>
      
      <div class="w-full sm:w-auto">
        <label for="location" class="block text-sm font-medium text-gray-700 mb-1">Location</label>
        <select
          id="location"
          v-model="filters.location"
          class="block w-full sm:w-48 border-gray-300 rounded-md shadow-sm focus:ring-primary-500 focus:border-primary-500 sm:text-sm"
          @change="$emit('apply-filters')"
        >
          <option value="">All Locations</option>
          <option v-for="location in locations" :key="location.id" :value="location.id">
            {{ location.name }}
          </option>
        </select>
      </div>
      
      <div class="w-full sm:w-auto">
        <label for="machineType" class="block text-sm font-medium text-gray-700 mb-1">Machine Type</label>
        <select
          id="machineType"
          v-model="filters.machineType"
          class="block w-full sm:w-48 border-gray-300 rounded-md shadow-sm focus:ring-primary-500 focus:border-primary-500 sm:text-sm"
          @change="$emit('apply-filters')"
        >
          <option value="">All Types</option>
          <option value="Snack">Snack</option>
          <option value="Soda">Soda</option>
          <option value="Combo">Combo</option>
        </select>
      </div>
      
      <div class="w-full sm:w-auto mt-2 sm:mt-0">
        <button
          type="button"
          @click="$emit('apply-filters')"
          class="w-full sm:w-auto inline-flex items-center justify-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-primary-600 hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500 transition-colors duration-150"
        >
          <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 mr-1.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 4a1 1 0 011-1h16a1 1 0 011 1v2.586a1 1 0 01-.293.707l-6.414 6.414a1 1 0 00-.293.707V17l-4 4v-6.586a1 1 0 00-.293-.707L3.293 7.293A1 1 0 013 6.586V4z" />
          </svg>
          Apply Filters
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
defineProps({
  filters: {
    type: Object,
    required: true
  },
  locations: {
    type: Array,
    required: true
  }
})

defineEmits(['apply-filters'])
</script> 