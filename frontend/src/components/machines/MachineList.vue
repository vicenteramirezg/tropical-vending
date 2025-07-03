<template>
  <div class="space-y-6">
    <!-- Group machines by location -->
    <div v-for="(machines, locationId) in groupedMachines" :key="locationId" class="bg-white shadow-lg rounded-xl overflow-hidden">
      <div class="px-6 py-4 bg-gray-50 border-b border-gray-200 flex justify-between items-center">
        <div>
          <h2 class="text-lg font-medium text-gray-900">{{ locationNames[locationId] }}</h2>
          <p class="text-sm text-gray-500">{{ machines.length }} machines</p>
        </div>
        <button 
          @click="$emit('open-map', locationInfo[locationId])" 
          class="inline-flex items-center px-3 py-1.5 border border-gray-300 shadow-sm text-xs font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500 transition-colors duration-150"
        >
          <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 mr-1.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z" />
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 11a3 3 0 11-6 0 3 3 0 016 0z" />
          </svg>
          View on Maps
        </button>
      </div>
      
      <ul role="list" class="divide-y divide-gray-200">
        <li v-for="machine in machines" :key="machine.id" class="px-6 py-5 hover:bg-gray-50 transition-colors duration-150">
          <div class="flex items-center justify-between">
            <div>
              <div class="flex items-center">
                <p class="text-sm font-medium text-primary-600">{{ machine.name }}</p>
                <span 
                  class="ml-2 inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium"
                  :class="{
                    'bg-blue-100 text-blue-800': machine.machine_type === 'Soda',
                    'bg-green-100 text-green-800': machine.machine_type === 'Snack',
                    'bg-purple-100 text-purple-800': machine.machine_type === 'Combo'
                  }"
                >
                  {{ machine.machine_type }}
                </span>
              </div>
              <p v-if="machine.model" class="text-sm text-gray-500 mt-1">Model: {{ machine.model }}</p>
              <p v-if="machine.route" class="text-sm text-primary-600 mt-1">
                <span class="inline-flex items-center">
                  <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 mr-1 text-primary-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 20l-5.447-2.724A1 1 0 013 16.382V5.618a1 1 0 011.447-.894L9 7m0 13l6-3m-6 3V7m6 10l4.553 2.276A1 1 0 0021 18.382V7.618a1 1 0 00-.553-.894L15 4m0 13V4m0 0L9 7" />
                  </svg>
                  Route: {{ machine.route }}
                </span>
              </p>
              <p class="text-sm text-gray-500 mt-1">
                <span v-if="machine.product_count" class="text-primary-600 font-medium">{{ machine.product_count }} products</span>
                <span v-else class="text-gray-400 italic">No products</span>
              </p>
            </div>
            <div class="flex space-x-2">
              <button
                @click="$emit('edit-machine', machine)"
                class="inline-flex items-center px-3 py-1.5 border border-gray-300 shadow-sm text-xs font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500 transition-colors duration-150"
              >
                <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 mr-1" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
                </svg>
                Edit
              </button>
              <button
                @click="$emit('manage-products', machine)"
                class="inline-flex items-center px-3 py-1.5 border border-gray-300 shadow-sm text-xs font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500 transition-colors duration-150"
              >
                <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 mr-1" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 11V7a4 4 0 00-8 0v4M5 9h14l1 12H4L5 9z" />
                </svg>
                Products
              </button>
              <button
                @click="$emit('confirm-delete', machine)"
                class="inline-flex items-center px-3 py-1.5 border border-gray-300 shadow-sm text-xs font-medium rounded-md text-gray-700 bg-white hover:bg-red-50 hover:text-red-700 hover:border-red-300 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-red-500 transition-colors duration-150"
              >
                <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 mr-1" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                </svg>
                Delete
              </button>
            </div>
          </div>
        </li>
      </ul>
    </div>
  </div>
</template>

<script setup>
defineProps({
  groupedMachines: {
    type: Object,
    required: true
  },
  locationNames: {
    type: Object,
    required: true
  },
  locationInfo: {
    type: Object,
    required: true
  }
})

defineEmits(['open-map', 'edit-machine', 'manage-products', 'confirm-delete'])
</script> 