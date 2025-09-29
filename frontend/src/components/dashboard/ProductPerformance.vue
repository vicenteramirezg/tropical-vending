<template>
  <div class="bg-white shadow-lg rounded-xl mb-6 overflow-hidden">
    <div class="px-6 py-5 border-b border-gray-200">
      <div class="flex justify-between items-center">
        <div>
          <h3 class="text-lg leading-6 font-semibold text-gray-900">Top Product Performance</h3>
          <p class="mt-1 text-sm text-gray-500">
            Products ranked by demand and profitability
          </p>
        </div>
        <div class="flex space-x-2">
          <button
            @click="viewMode = 'demand'"
            :class="[
              'px-3 py-1.5 text-xs font-medium rounded-md transition-colors',
              viewMode === 'demand' 
                ? 'bg-primary-100 text-primary-800' 
                : 'text-gray-600 hover:text-gray-900'
            ]"
          >
            By Demand
          </button>
          <button
            @click="viewMode = 'revenue'"
            :class="[
              'px-3 py-1.5 text-xs font-medium rounded-md transition-colors',
              viewMode === 'revenue' 
                ? 'bg-primary-100 text-primary-800' 
                : 'text-gray-600 hover:text-gray-900'
            ]"
          >
            By Revenue
          </button>
          <button
            @click="viewMode = 'margin'"
            :class="[
              'px-3 py-1.5 text-xs font-medium rounded-md transition-colors',
              viewMode === 'margin' 
                ? 'bg-primary-100 text-primary-800' 
                : 'text-gray-600 hover:text-gray-900'
            ]"
          >
            By Margin
          </button>
        </div>
      </div>
    </div>
    
    <div class="overflow-hidden">
      <div class="overflow-x-auto">
        <table class="min-w-full divide-y divide-gray-200">
          <thead class="bg-gray-50">
            <tr>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Product</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Demand</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Revenue</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Profit</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Margin</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Coverage</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Trend</th>
            </tr>
          </thead>
          <tbody class="bg-white divide-y divide-gray-200">
            <tr
              v-for="(product, index) in sortedProducts"
              :key="product.product_id"
              class="hover:bg-gray-50 transition-colors duration-150"
            >
              <td class="px-6 py-4 whitespace-nowrap">
                <div class="flex items-center">
                  <div class="flex-shrink-0 w-8 h-8 bg-primary-100 rounded-full flex items-center justify-center">
                    <span class="text-xs font-semibold text-primary-800">{{ index + 1 }}</span>
                  </div>
                  <div class="ml-3">
                    <div class="text-sm font-semibold text-gray-900">{{ product.product_name }}</div>
                    <div class="text-xs text-gray-500">{{ product.machines_count }} machines • {{ product.locations_count }} locations</div>
                  </div>
                </div>
              </td>
              <td class="px-6 py-4 whitespace-nowrap">
                <div class="text-sm font-semibold text-gray-900">{{ formatNumber(product.total_demand) }}</div>
                <div class="text-xs text-gray-500">{{ product.restock_count }} restocks</div>
              </td>
              <td class="px-6 py-4 whitespace-nowrap">
                <div class="text-sm font-semibold text-gray-900">${{ formatMoney(product.total_revenue) }}</div>
                <div class="text-xs text-gray-500">${{ formatMoney(product.avg_revenue_per_restock || 0) }}/restock</div>
              </td>
              <td class="px-6 py-4 whitespace-nowrap">
                <div class="text-sm font-semibold text-gray-900">${{ formatMoney(product.total_profit) }}</div>
                <div class="text-xs text-gray-500">{{ formatNumber(product.avg_demand_per_restock || 0) }} units/restock</div>
              </td>
              <td class="px-6 py-4 whitespace-nowrap">
                <div class="flex items-center">
                  <span
                    class="text-sm font-semibold"
                    :class="getMarginColor(product.profit_margin)"
                  >
                    {{ (product.profit_margin || 0).toFixed(1) }}%
                  </span>
                </div>
              </td>
              <td class="px-6 py-4 whitespace-nowrap">
                <div class="flex items-center">
                  <div class="w-16 bg-gray-200 rounded-full h-2 mr-2">
                    <div
                      class="h-2 rounded-full"
                      :class="getVelocityColor(product.velocity_score)"
                      :style="{ width: `${Math.min(100, (product.velocity_score || 0) * 20)}%` }"
                    ></div>
                  </div>
                  <span class="text-xs text-gray-600">{{ (product.velocity_score || 0).toFixed(2) }}</span>
                </div>
              </td>
              <td class="px-6 py-4 whitespace-nowrap">
                <span
                  class="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium"
                  :class="getTrendClass(product.performance_trend)"
                >
                  <span class="mr-1">{{ getTrendIcon(product.performance_trend) }}</span>
                  {{ product.performance_trend }}
                </span>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
    
    <!-- Empty State -->
    <div v-if="!products || products.length === 0" class="text-center py-12">
      <svg xmlns="http://www.w3.org/2000/svg" class="h-12 w-12 mx-auto text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M20 7l-8-4-8 4m16 0l-8 4m8-4v10l-8 4m0-10L4 7m8 4v10M4 7v10l8 4" />
      </svg>
      <h3 class="mt-2 text-sm font-medium text-gray-900">No product data</h3>
      <p class="mt-1 text-sm text-gray-500">No analytics data available for the selected time period.</p>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'

const props = defineProps({
  products: {
    type: Array,
    default: () => []
  }
})

const viewMode = ref('demand')

// Sort products based on view mode
const sortedProducts = computed(() => {
  if (!props.products || props.products.length === 0) return []
  
  const productsCopy = [...props.products]
  
  switch (viewMode.value) {
    case 'demand':
      return productsCopy.sort((a, b) => b.total_demand - a.total_demand)
    case 'revenue':
      return productsCopy.sort((a, b) => b.total_revenue - a.total_revenue)
    case 'margin':
      return productsCopy.sort((a, b) => b.profit_margin - a.profit_margin)
    default:
      return productsCopy
  }
})

// Format numbers with K, M notation
const formatNumber = (value) => {
  if (value >= 1000000) {
    return (value / 1000000).toFixed(1) + 'M'
  } else if (value >= 1000) {
    return (value / 1000).toFixed(1) + 'K'
  }
  return Math.round(value).toString()
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

// Get color for profit margin
const getMarginColor = (margin) => {
  if (margin >= 50) return 'text-green-600'
  if (margin >= 25) return 'text-yellow-600'
  if (margin >= 0) return 'text-gray-600'
  return 'text-red-600'
}

// Get color for velocity score
const getVelocityColor = (score) => {
  if (score >= 2) return 'bg-green-500'
  if (score >= 1) return 'bg-yellow-500'
  return 'bg-red-500'
}

// Get trend styling classes
const getTrendClass = (trend) => {
  switch (trend) {
    case 'improving':
      return 'bg-green-100 text-green-800'
    case 'declining':
      return 'bg-red-100 text-red-800'
    default:
      return 'bg-gray-100 text-gray-800'
  }
}

// Get trend icons
const getTrendIcon = (trend) => {
  switch (trend) {
    case 'improving':
      return '📈'
    case 'declining':
      return '📉'
    default:
      return '➡️'
  }
}
</script>
