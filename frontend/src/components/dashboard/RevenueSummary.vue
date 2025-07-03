<template>
  <div class="bg-white shadow-lg overflow-hidden sm:rounded-xl transition-all duration-300 hover:shadow-xl">
    <div class="px-6 py-5 border-b border-gray-100">
      <h3 class="text-lg leading-6 font-medium text-gray-900">Revenue & Profit</h3>
      <p class="mt-1 text-sm text-gray-500">
        Last 30 days performance
      </p>
    </div>
    
    <div>
      <div class="grid grid-cols-1 md:grid-cols-3 divide-y md:divide-y-0 md:divide-x divide-gray-200">
        <div class="px-6 py-5">
          <div class="text-sm font-medium text-gray-500">Total Revenue</div>
          <div class="mt-2 text-3xl font-bold text-gray-900">${{ (data.revenue_total || 0).toFixed(2) }}</div>
        </div>
        <div class="px-6 py-5">
          <div class="text-sm font-medium text-gray-500">Total Profit</div>
          <div class="mt-2 text-3xl font-bold text-green-600">${{ (data.profit_total || 0).toFixed(2) }}</div>
        </div>
        <div class="px-6 py-5">
          <div class="text-sm font-medium text-gray-500">Profit Margin</div>
          <div class="mt-2 text-3xl font-bold text-gray-900">{{ (data.profit_margin || 0).toFixed(1) }}%</div>
        </div>
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