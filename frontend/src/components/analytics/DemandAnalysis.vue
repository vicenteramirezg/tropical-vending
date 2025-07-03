<template>
  <div class="bg-white shadow-lg overflow-hidden sm:rounded-xl transition-all duration-300 hover:shadow-xl">
    <div class="px-6 py-5 border-b border-gray-100">
      <h3 class="text-lg leading-6 font-medium text-gray-900">Product Demand Analysis</h3>
      <p class="mt-1 text-sm text-gray-500">
        Sales performance and demand tracking based on restock data
      </p>
    </div>
    
    <div>
      <!-- Product Demand Summary -->
      <div class="overflow-x-auto">
        <table class="min-w-full divide-y divide-gray-200">
          <thead class="bg-gray-50">
            <tr>
              <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Product
              </th>
              <th scope="col" class="px-6 py-3 text-center text-xs font-medium text-gray-500 uppercase tracking-wider">
                Units Sold
              </th>
              <th scope="col" class="px-6 py-3 text-center text-xs font-medium text-gray-500 uppercase tracking-wider">
                Revenue
              </th>
              <th scope="col" class="px-6 py-3 text-center text-xs font-medium text-gray-500 uppercase tracking-wider">
                Profit
              </th>
              <th scope="col" class="px-6 py-3 text-center text-xs font-medium text-gray-500 uppercase tracking-wider">
                Trend
              </th>
            </tr>
          </thead>
          <tbody class="bg-white divide-y divide-gray-200">
            <tr v-for="item in data.products" :key="item.product_id" class="hover:bg-gray-50 transition-colors duration-150">
              <td class="px-6 py-4 whitespace-nowrap">
                <div class="text-sm font-medium text-gray-900">{{ item.product_name }}</div>
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-center">
                <div class="text-sm text-gray-900">{{ item.units_sold }}</div>
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-center">
                <div class="text-sm text-gray-900">${{ (item.revenue || 0).toFixed(2) }}</div>
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-center">
                <div class="text-sm text-gray-900">${{ (item.profit || 0).toFixed(2) }}</div>
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-center">
                <span 
                  class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium"
                  :class="getTrendClass(item.trend || 0)"
                >
                  <svg v-if="(item.trend || 0) > 0" xmlns="http://www.w3.org/2000/svg" class="h-3 w-3 mr-1" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6" />
                  </svg>
                  <svg v-else-if="(item.trend || 0) < 0" xmlns="http://www.w3.org/2000/svg" class="h-3 w-3 mr-1" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 17h8m0 0V9m0 8l-8-8-4 4-6-6" />
                  </svg>
                  <svg v-else xmlns="http://www.w3.org/2000/svg" class="h-3 w-3 mr-1" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M18 12H6" />
                  </svg>
                  {{ formatTrend(item.trend || 0) }}
                </span>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
      
      <!-- Detailed Demand Analysis -->
      <div v-if="data.unit_counts && data.unit_counts.length > 0" class="mt-6 px-6">
        <h4 class="text-base font-medium text-gray-700 mb-3">Detailed Demand By Machine & Product</h4>
        
        <div class="border rounded-lg shadow-sm overflow-hidden">
          <table class="min-w-full divide-y divide-gray-200">
            <thead class="bg-gray-50">
              <tr>
                <th scope="col" class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                  Location
                </th>
                <th scope="col" class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                  Machine
                </th>
                <th scope="col" class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                  Product
                </th>
                <th scope="col" class="px-4 py-3 text-center text-xs font-medium text-gray-500 uppercase">
                  Period
                </th>
                <th scope="col" class="px-4 py-3 text-center text-xs font-medium text-gray-500 uppercase">
                  Units Sold
                </th>
                <th scope="col" class="px-4 py-3 text-center text-xs font-medium text-gray-500 uppercase">
                  Daily Demand
                </th>
                <th scope="col" class="px-4 py-3 text-center text-xs font-medium text-gray-500 uppercase">
                  Revenue
                </th>
              </tr>
            </thead>
            <tbody class="bg-white divide-y divide-gray-200">
              <tr v-for="(count, index) in sortedDemandCounts" :key="index" class="hover:bg-gray-50">
                <td class="px-4 py-3 text-sm text-gray-900">
                  {{ count.location_name }}
                </td>
                <td class="px-4 py-3 text-sm text-gray-900">
                  {{ count.machine_name }}
                </td>
                <td class="px-4 py-3 text-sm text-gray-900">
                  {{ count.product_name }}
                </td>
                <td class="px-4 py-3 text-sm text-gray-500 text-center">
                  {{ formatDateShort(count.start_date) }} - {{ formatDateShort(count.end_date) }}
                  <div class="text-xs text-gray-400">({{ count.days_between }} days)</div>
                </td>
                <td class="px-4 py-3 text-sm text-gray-900 text-center font-medium">
                  {{ count.units_sold }}
                </td>
                <td class="px-4 py-3 text-sm text-gray-900 text-center">
                  {{ formatDailyDemand(count.daily_demand) }}
                </td>
                <td class="px-4 py-3 text-sm text-gray-900 text-center">
                  ${{ (count.revenue || 0).toFixed(2) }}
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
      
      <div v-else-if="data.products && data.products.length > 0 && (!data.unit_counts || data.unit_counts.length === 0)" class="px-6 py-4 text-center">
        <p class="text-sm text-gray-500">
          No detailed demand data is available for the selected period.
          <br>Need at least two restock visits to the same machine to calculate demand.
        </p>
      </div>
      
      <div v-else class="px-6 py-4 text-center">
        <p class="text-sm text-gray-500">
          No demand data available. Record restock visits to track product demand.
        </p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  data: {
    type: Object,
    required: true,
    default: () => ({
      products: [],
      unit_counts: []
    })
  },
  formatDateShort: {
    type: Function,
    required: true
  },
  formatDailyDemand: {
    type: Function,
    required: true
  },
  formatTrend: {
    type: Function,
    required: true
  },
  getTrendClass: {
    type: Function,
    required: true
  }
})

// Computed property for sorted demand counts
const sortedDemandCounts = computed(() => {
  if (!props.data.unit_counts) return []
  
  return [...props.data.unit_counts]
    .sort((a, b) => {
      // Sort by location, then machine, then product, then date
      if (a.location_name !== b.location_name) return a.location_name.localeCompare(b.location_name)
      if (a.machine_name !== b.machine_name) return a.machine_name.localeCompare(b.machine_name)
      if (a.product_name !== b.product_name) return a.product_name.localeCompare(b.product_name)
      return new Date(b.end_date) - new Date(a.end_date) // Most recent first
    })
})
</script> 