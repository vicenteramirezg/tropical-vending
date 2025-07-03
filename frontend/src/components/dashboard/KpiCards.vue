<template>
  <div class="grid grid-cols-1 gap-4 sm:gap-5 sm:grid-cols-2 lg:grid-cols-4 mb-8">
    <div class="bg-gradient-to-br from-white to-gray-50 overflow-hidden shadow-lg rounded-xl transition-transform duration-300 hover:scale-105 hover:shadow-xl">
      <div class="px-4 py-5 sm:p-6">
        <dl>
          <dt class="text-sm font-medium text-gray-500 truncate">Total Locations</dt>
          <dd class="mt-2 text-2xl sm:text-3xl font-bold text-primary-600">{{ data.locations }}</dd>
        </dl>
      </div>
    </div>
    
    <div class="bg-gradient-to-br from-white to-gray-50 overflow-hidden shadow-lg rounded-xl transition-transform duration-300 hover:scale-105 hover:shadow-xl">
      <div class="px-4 py-5 sm:p-6">
        <dl>
          <dt class="text-sm font-medium text-gray-500 truncate">Total Machines</dt>
          <dd class="mt-2 text-2xl sm:text-3xl font-bold text-primary-600">{{ data.machines }}</dd>
        </dl>
      </div>
    </div>
    
    <div class="bg-gradient-to-br from-white to-gray-50 overflow-hidden shadow-lg rounded-xl transition-transform duration-300 hover:scale-105 hover:shadow-xl">
      <div class="px-4 py-5 sm:p-6">
        <dl>
          <dt class="text-sm font-medium text-gray-500 truncate">Total Products</dt>
          <dd class="mt-2 text-2xl sm:text-3xl font-bold text-primary-600">{{ data.products }}</dd>
        </dl>
      </div>
    </div>
    
    <div class="bg-gradient-to-br from-white to-gray-50 overflow-hidden shadow-lg rounded-xl transition-transform duration-300 hover:scale-105 hover:shadow-xl">
      <div class="px-4 py-5 sm:p-6">
        <dl>
          <dt class="text-sm font-medium text-gray-500 truncate">Recent Restocks</dt>
          <dd class="mt-2 text-2xl sm:text-3xl font-bold text-primary-600">{{ data.recent_restocks }}</dd>
        </dl>
      </div>
    </div>
  </div>
</template>

<script setup>
defineProps({
  data: {
    type: Object,
    required: true
  }
})
</script> 