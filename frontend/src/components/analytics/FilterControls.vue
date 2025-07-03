<template>
  <div class="bg-white p-5 shadow-lg rounded-xl mb-6">
    <div class="flex flex-wrap items-center gap-4">
      <div>
        <label for="dateRange" class="block text-sm font-medium text-gray-700 mb-1">Date Range</label>
        <select
          id="dateRange"
          :value="filters.dateRange"
          @change="updateDateRange"
          class="block w-full border-gray-300 rounded-md shadow-sm focus:ring-primary-500 focus:border-primary-500 sm:text-sm"
        >
          <option value="7">Last 7 days</option>
          <option value="30">Last 30 days</option>
          <option value="90">Last 90 days</option>
          <option value="365">Last 12 months</option>
          <option value="custom">Custom range</option>
        </select>
      </div>
      
      <div v-if="filters.dateRange === 'custom'" class="flex space-x-2">
        <div>
          <label for="startDate" class="block text-sm font-medium text-gray-700 mb-1">Start Date</label>
          <input
            type="date"
            id="startDate"
            :value="filters.startDate"
            @input="updateStartDate"
            class="block w-full border-gray-300 rounded-md shadow-sm focus:ring-primary-500 focus:border-primary-500 sm:text-sm"
          >
        </div>
        <div>
          <label for="endDate" class="block text-sm font-medium text-gray-700 mb-1">End Date</label>
          <input
            type="date"
            id="endDate"
            :value="filters.endDate"
            @input="updateEndDate"
            class="block w-full border-gray-300 rounded-md shadow-sm focus:ring-primary-500 focus:border-primary-500 sm:text-sm"
          >
        </div>
      </div>
      
      <div>
        <label for="location" class="block text-sm font-medium text-gray-700 mb-1">Location</label>
        <select
          id="location"
          :value="filters.location"
          @change="updateLocation"
          class="block w-full border-gray-300 rounded-md shadow-sm focus:ring-primary-500 focus:border-primary-500 sm:text-sm"
        >
          <option value="">All Locations</option>
          <option v-for="location in locations" :key="location.id" :value="location.id">
            {{ location.name }}
          </option>
        </select>
      </div>
      
      <div class="self-end ml-auto mt-4">
        <button
          type="button"
          @click="$emit('apply-filters')"
          class="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-primary-600 hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500 transition-colors duration-150"
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

const emit = defineEmits(['apply-filters', 'update-filters'])

const updateDateRange = (event) => {
  emit('update-filters', { dateRange: event.target.value })
}

const updateStartDate = (event) => {
  emit('update-filters', { startDate: event.target.value })
}

const updateEndDate = (event) => {
  emit('update-filters', { endDate: event.target.value })
}

const updateLocation = (event) => {
  emit('update-filters', { location: event.target.value })
}
</script> 