<template>
  <div class="bg-white shadow-lg overflow-hidden sm:rounded-xl mb-6 transition-all duration-300 hover:shadow-xl">
    <div class="px-6 py-5 border-b border-gray-100 flex justify-between items-center">
      <div>
        <h3 class="text-lg leading-6 font-medium text-gray-900">Stock Levels</h3>
        <p class="mt-1 text-sm text-gray-500">
          Current inventory levels across machines
        </p>
      </div>
      <span 
        class="inline-flex items-center px-3.5 py-1 rounded-full text-sm font-medium"
        :class="data.low_stock_count > 0 ? 'bg-red-100 text-red-800' : 'bg-green-100 text-green-800'"
      >
        <svg v-if="data.low_stock_count > 0" xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 mr-1.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
        </svg>
        <svg v-else xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 mr-1.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
        </svg>
        {{ data.low_stock_count }} items low stock
      </span>
    </div>
    
    <div>
      <ul role="list" class="divide-y divide-gray-200">
        <li v-for="(item, index) in data.items" :key="index" class="px-6 py-4 hover:bg-gray-50 transition-colors duration-150">
          <div class="flex items-center justify-between">
            <div>
              <p class="text-sm font-medium text-primary-600">{{ item.product_name }}</p>
              <p class="text-sm text-gray-500 flex items-center mt-1">
                <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 mr-1 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 7h.01M7 3h5c.512 0 1.024.195 1.414.586l7 7a2 2 0 010 2.828l-7 7a2 2 0 01-2.828 0l-7-7A1.994 1.994 0 013 12V7a4 4 0 014-4z" />
                </svg>
                {{ item.machine_name }} at {{ item.location_name }}
              </p>
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
    required: true,
    default: () => ({
      low_stock_count: 0,
      items: []
    })
  }
})

const getStockLevelClass = (quantity) => {
  if (quantity <= 0) return 'bg-red-100 text-red-800'
  if (quantity <= 3) return 'bg-yellow-100 text-yellow-800'
  return 'bg-blue-100 text-blue-800'
}
</script> 