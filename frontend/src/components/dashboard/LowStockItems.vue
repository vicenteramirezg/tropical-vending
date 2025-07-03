<template>
  <div class="bg-white shadow-lg overflow-hidden sm:rounded-xl mb-8 transition-all duration-300 hover:shadow-xl">
    <div class="px-6 py-5 border-b border-gray-100 flex justify-between items-center">
      <div>
        <h3 class="text-lg leading-6 font-medium text-gray-900">Low Stock Items</h3>
        <p class="mt-1 text-sm text-gray-500">
          Products with stock level below threshold
        </p>
      </div>
      <span 
        class="inline-flex items-center px-3.5 py-1 rounded-full text-sm font-medium"
        :class="data.low_stock_count > 0 ? 'bg-red-100 text-red-800' : 'bg-green-100 text-green-800'"
      >
        {{ data.low_stock_count }} items
      </span>
    </div>
    
    <div>
      <div v-if="data.low_stock_items.length === 0" class="px-6 py-8 text-center text-gray-500">
        <svg xmlns="http://www.w3.org/2000/svg" class="h-12 w-12 mx-auto text-green-400 mb-3" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
        </svg>
        <p class="text-lg font-medium">No low stock items - everything is well stocked!</p>
      </div>
      <ul v-else role="list" class="divide-y divide-gray-200">
        <li v-for="(item, index) in data.low_stock_items" :key="index" class="px-6 py-4 hover:bg-gray-50 transition-colors duration-150">
          <div class="flex items-center justify-between">
            <div>
              <p class="text-sm font-medium text-primary-600 truncate">{{ item.product }}</p>
              <p class="text-sm text-gray-500">{{ item.machine }} ({{ item.location }})</p>
            </div>
            <div>
              <span 
                class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium"
                :class="getStockLevelClass(item.current_stock)"
              >
                Stock: {{ item.current_stock }}
              </span>
            </div>
          </div>
        </li>
      </ul>
    </div>
  </div>
</template>

<script setup>
defineProps({
  data: {
    type: Object,
    required: true
  },
  getStockLevelClass: {
    type: Function,
    required: true
  }
})
</script> 