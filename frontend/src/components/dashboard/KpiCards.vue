<template>
  <div class="grid grid-cols-1 gap-4 sm:gap-5 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-5 mb-8">
    <!-- Total Demand Units -->
    <div class="bg-gradient-to-br from-blue-500 to-blue-600 overflow-hidden shadow-lg rounded-xl transition-all duration-300 hover:scale-105 hover:shadow-xl">
      <div class="px-4 py-5 sm:p-6 text-white">
        <dl>
          <dt class="text-sm font-medium text-blue-100 truncate">Units Sold</dt>
          <dd class="mt-2 text-2xl sm:text-3xl font-bold">{{ formatNumber(data.summary?.total_demand_units || 0) }}</dd>
          <dd class="mt-1 text-xs text-blue-100">{{ formatNumber(data.summary?.avg_daily_demand || 0) }}/day avg</dd>
        </dl>
      </div>
    </div>
    
    <!-- Total Revenue -->
    <div class="bg-gradient-to-br from-green-500 to-green-600 overflow-hidden shadow-lg rounded-xl transition-all duration-300 hover:scale-105 hover:shadow-xl">
      <div class="px-4 py-5 sm:p-6 text-white">
        <dl>
          <dt class="text-sm font-medium text-green-100 truncate">Total Revenue</dt>
          <dd class="mt-2 text-2xl sm:text-3xl font-bold">${{ formatMoney(data.summary?.total_revenue || 0) }}</dd>
          <dd class="mt-1 text-xs text-green-100">{{ data.summary?.total_restocks || 0 }} restocks</dd>
        </dl>
      </div>
    </div>
    
    <!-- Total Profit -->
    <div class="bg-gradient-to-br from-emerald-500 to-emerald-600 overflow-hidden shadow-lg rounded-xl transition-all duration-300 hover:scale-105 hover:shadow-xl">
      <div class="px-4 py-5 sm:p-6 text-white">
        <dl>
          <dt class="text-sm font-medium text-emerald-100 truncate">Total Profit</dt>
          <dd class="mt-2 text-2xl sm:text-3xl font-bold">${{ formatMoney(data.summary?.total_profit || 0) }}</dd>
          <dd class="mt-1 text-xs text-emerald-100">{{ (data.summary?.overall_profit_margin || 0).toFixed(1) }}% margin</dd>
        </dl>
      </div>
    </div>
    
    <!-- Active Products -->
    <div class="bg-gradient-to-br from-purple-500 to-purple-600 overflow-hidden shadow-lg rounded-xl transition-all duration-300 hover:scale-105 hover:shadow-xl">
      <div class="px-4 py-5 sm:p-6 text-white">
        <dl>
          <dt class="text-sm font-medium text-purple-100 truncate">Active Products</dt>
          <dd class="mt-2 text-2xl sm:text-3xl font-bold">{{ data.summary?.unique_products || 0 }}</dd>
          <dd class="mt-1 text-xs text-purple-100">{{ data.summary?.unique_machines || 0 }} machines</dd>
        </dl>
      </div>
    </div>
    
    <!-- Performance Score -->
    <div class="bg-gradient-to-br from-orange-500 to-orange-600 overflow-hidden shadow-lg rounded-xl transition-all duration-300 hover:scale-105 hover:shadow-xl">
      <div class="px-4 py-5 sm:p-6 text-white">
        <dl>
          <dt class="text-sm font-medium text-orange-100 truncate">Locations</dt>
          <dd class="mt-2 text-2xl sm:text-3xl font-bold">{{ data.summary?.unique_locations || 0 }}</dd>
          <dd class="mt-1 text-xs text-orange-100">{{ data.low_stock_count || 0 }} low stock</dd>
        </dl>
      </div>
    </div>
  </div>

  <!-- Insights Panel -->
  <div v-if="data.insights && data.insights.length > 0" class="bg-white shadow-lg rounded-xl mb-6 overflow-hidden">
    <div class="px-6 py-4 bg-gradient-to-r from-indigo-500 to-purple-600">
      <h3 class="text-lg font-semibold text-white flex items-center">
        <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
        </svg>
        Key Insights
      </h3>
    </div>
    <div class="p-6">
      <div class="space-y-4">
        <div 
          v-for="insight in priorityInsights" 
          :key="insight.type"
          class="flex items-start p-4 rounded-lg"
          :class="getInsightClass(insight.priority)"
        >
          <div class="flex-shrink-0 mr-3">
            <div 
              class="w-8 h-8 rounded-full flex items-center justify-center text-white text-sm font-bold"
              :class="getInsightIconClass(insight.priority)"
            >
              {{ getInsightIcon(insight.priority) }}
            </div>
          </div>
          <div class="flex-1 min-w-0">
            <h4 class="text-sm font-semibold text-gray-900">{{ insight.title }}</h4>
            <p class="text-sm text-gray-600 mt-1">{{ insight.description }}</p>
          </div>
          <div class="flex-shrink-0 ml-4">
            <span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-gray-100 text-gray-800">
              {{ formatMetric(insight.metric) }}
            </span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  data: {
    type: Object,
    required: true
  }
})

// Format numbers with K, M notation
const formatNumber = (value) => {
  if (value >= 1000000) {
    return (value / 1000000).toFixed(1) + 'M'
  } else if (value >= 1000) {
    return (value / 1000).toFixed(1) + 'K'
  }
  return value.toString()
}

// Format money values
const formatMoney = (value) => {
  if (value >= 1000000) {
    return (value / 1000000).toFixed(1) + 'M'
  } else if (value >= 1000) {
    return (value / 1000).toFixed(1) + 'K'
  }
  return value.toFixed(2)
}

// Format metrics based on type
const formatMetric = (value) => {
  if (typeof value === 'number') {
    if (value >= 1000) {
      return formatNumber(value)
    } else if (value % 1 !== 0) {
      return value.toFixed(1)
    }
  }
  return value.toString()
}

// Get insights sorted by priority
const priorityInsights = computed(() => {
  if (!props.data.insights) return []
  
  const priorityOrder = { 'high': 1, 'medium': 2, 'low': 3 }
  return props.data.insights
    .slice(0, 3) // Show top 3 insights
    .sort((a, b) => priorityOrder[a.priority] - priorityOrder[b.priority])
})

// Get insight styling classes
const getInsightClass = (priority) => {
  switch (priority) {
    case 'high':
      return 'bg-red-50 border-l-4 border-red-400'
    case 'medium':
      return 'bg-yellow-50 border-l-4 border-yellow-400'
    default:
      return 'bg-blue-50 border-l-4 border-blue-400'
  }
}

const getInsightIconClass = (priority) => {
  switch (priority) {
    case 'high':
      return 'bg-red-500'
    case 'medium':
      return 'bg-yellow-500'
    default:
      return 'bg-blue-500'
  }
}

const getInsightIcon = (priority) => {
  switch (priority) {
    case 'high':
      return '!'
    case 'medium':
      return '⚠'
    default:
      return 'ℹ'
  }
}
</script> 