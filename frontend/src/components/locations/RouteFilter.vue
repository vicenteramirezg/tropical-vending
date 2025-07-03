<template>
  <div class="bg-white p-5 shadow-lg rounded-xl mb-6">
    <div class="flex flex-wrap items-center gap-4">
      <div>
        <label for="routeFilter" class="block text-sm font-medium text-gray-700 mb-1">Filter by Route</label>
        <select
          id="routeFilter"
          :value="selectedRoute"
          @change="$emit('update:selectedRoute', $event.target.value)"
          class="block w-full border-gray-300 rounded-md shadow-sm focus:ring-primary-500 focus:border-primary-500 sm:text-sm"
        >
          <option value="">All Routes</option>
          <option value="unassigned">Unassigned</option>
          <option v-for="route in availableRoutes" :key="route" :value="route">
            {{ route }}
          </option>
        </select>
      </div>
      <div class="self-end">
        <button
          type="button"
          @click="$emit('clear-filter')"
          class="inline-flex items-center px-3 py-2 border border-gray-300 shadow-sm text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500 transition-colors duration-150"
        >
          Clear Filter
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
defineProps({
  selectedRoute: {
    type: String,
    required: true
  },
  availableRoutes: {
    type: Array,
    required: true
  }
})

defineEmits(['update:selectedRoute', 'clear-filter'])
</script> 