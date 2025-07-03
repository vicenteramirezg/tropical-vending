<template>
  <div class="bg-white shadow-lg overflow-hidden sm:rounded-xl mb-6 transition-all duration-300 hover:shadow-xl">
    <div class="px-6 py-5 border-b border-gray-100">
      <h3 class="text-lg leading-6 font-medium text-gray-900">Revenue & Profit</h3>
      <p class="mt-1 text-sm text-gray-500">
        Financial performance for the selected period
      </p>
    </div>
    
    <div>
      <div class="grid grid-cols-1 md:grid-cols-3 divide-y md:divide-y-0 md:divide-x divide-gray-200">
        <div class="px-6 py-5">
          <div class="text-sm font-medium text-gray-500">Total Revenue</div>
          <div class="mt-2 text-3xl font-bold text-gray-900">${{ (data.revenue?.total || 0).toFixed(2) }}</div>
          <div class="mt-2 text-sm text-gray-500 flex items-center">
            <span 
              :class="(data.revenue?.change || 0) >= 0 ? 'text-green-600' : 'text-red-600'"
              class="flex items-center"
            >
              <svg v-if="(data.revenue?.change || 0) >= 0" xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 mr-1" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6" />
              </svg>
              <svg v-else xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 mr-1" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 17h8m0 0V9m0 8l-8-8-4 4-6-6" />
              </svg>
              {{ (data.revenue?.change || 0) >= 0 ? '+' : '' }}{{ (data.revenue?.change || 0).toFixed(1) }}%
            </span>
            <span class="ml-1">vs previous period</span>
          </div>
        </div>
        
        <div class="px-6 py-5">
          <div class="text-sm font-medium text-gray-500">Total Profit</div>
          <div class="mt-2 text-3xl font-bold text-green-600">${{ (data.profit?.total || 0).toFixed(2) }}</div>
          <div class="mt-2 text-sm text-gray-500 flex items-center">
            <span 
              :class="(data.profit?.change || 0) >= 0 ? 'text-green-600' : 'text-red-600'"
              class="flex items-center"
            >
              <svg v-if="(data.profit?.change || 0) >= 0" xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 mr-1" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6" />
              </svg>
              <svg v-else xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 mr-1" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 17h8m0 0V9m0 8l-8-8-4 4-6-6" />
              </svg>
              {{ (data.profit?.change || 0) >= 0 ? '+' : '' }}{{ (data.profit?.change || 0).toFixed(1) }}%
            </span>
            <span class="ml-1">vs previous period</span>
          </div>
        </div>
        
        <div class="px-6 py-5">
          <div class="text-sm font-medium text-gray-500">Profit Margin</div>
          <div class="mt-2 text-3xl font-bold text-gray-900">{{ (data.margin?.total || 0).toFixed(1) }}%</div>
          <div class="mt-2 text-sm text-gray-500 flex items-center">
            <span 
              :class="(data.margin?.change || 0) >= 0 ? 'text-green-600' : 'text-red-600'"
              class="flex items-center"
            >
              <svg v-if="(data.margin?.change || 0) >= 0" xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 mr-1" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6" />
              </svg>
              <svg v-else xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 mr-1" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 17h8m0 0V9m0 8l-8-8-4 4-6-6" />
              </svg>
              {{ (data.margin?.change || 0) >= 0 ? '+' : '' }}{{ (data.margin?.change || 0).toFixed(1) }}%
            </span>
            <span class="ml-1">vs previous period</span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
defineProps({
  data: {
    type: Object,
    required: true,
    default: () => ({
      revenue: { total: 0, change: 0 },
      profit: { total: 0, change: 0 },
      margin: { total: 0, change: 0 }
    })
  }
})
</script> 