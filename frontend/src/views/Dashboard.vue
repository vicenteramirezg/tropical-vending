<template>
  <div>
    <h1 class="text-2xl font-semibold text-gray-900 mb-6">Dashboard</h1>
    
    <div v-if="loading" class="flex justify-center">
      <div class="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-primary-500"></div>
    </div>
    
    <div v-else>
      <!-- KPI Cards -->
      <div class="grid grid-cols-1 gap-5 sm:grid-cols-2 lg:grid-cols-4 mb-6">
        <div class="bg-white overflow-hidden shadow rounded-lg">
          <div class="px-4 py-5 sm:p-6">
            <dl>
              <dt class="text-sm font-medium text-gray-500 truncate">Total Locations</dt>
              <dd class="mt-1 text-3xl font-semibold text-gray-900">{{ data.locations }}</dd>
            </dl>
          </div>
        </div>
        
        <div class="bg-white overflow-hidden shadow rounded-lg">
          <div class="px-4 py-5 sm:p-6">
            <dl>
              <dt class="text-sm font-medium text-gray-500 truncate">Total Machines</dt>
              <dd class="mt-1 text-3xl font-semibold text-gray-900">{{ data.machines }}</dd>
            </dl>
          </div>
        </div>
        
        <div class="bg-white overflow-hidden shadow rounded-lg">
          <div class="px-4 py-5 sm:p-6">
            <dl>
              <dt class="text-sm font-medium text-gray-500 truncate">Total Products</dt>
              <dd class="mt-1 text-3xl font-semibold text-gray-900">{{ data.products }}</dd>
            </dl>
          </div>
        </div>
        
        <div class="bg-white overflow-hidden shadow rounded-lg">
          <div class="px-4 py-5 sm:p-6">
            <dl>
              <dt class="text-sm font-medium text-gray-500 truncate">Recent Restocks</dt>
              <dd class="mt-1 text-3xl font-semibold text-gray-900">{{ data.recent_restocks }}</dd>
            </dl>
          </div>
        </div>
      </div>
      
      <!-- Low Stock Items -->
      <div class="bg-white shadow overflow-hidden sm:rounded-lg mb-6">
        <div class="px-4 py-5 sm:px-6 flex justify-between items-center">
          <div>
            <h3 class="text-lg leading-6 font-medium text-gray-900">Low Stock Items</h3>
            <p class="mt-1 max-w-2xl text-sm text-gray-500">
              Products with stock level below threshold
            </p>
          </div>
          <span 
            class="inline-flex items-center px-3 py-0.5 rounded-full text-sm font-medium"
            :class="data.low_stock_count > 0 ? 'bg-red-100 text-red-800' : 'bg-green-100 text-green-800'"
          >
            {{ data.low_stock_count }} items
          </span>
        </div>
        
        <div class="border-t border-gray-200">
          <div v-if="data.low_stock_items.length === 0" class="px-4 py-5 text-center text-gray-500">
            No low stock items - everything is well stocked!
          </div>
          <ul v-else role="list" class="divide-y divide-gray-200">
            <li v-for="(item, index) in data.low_stock_items" :key="index" class="px-4 py-4 sm:px-6">
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
      
      <!-- Revenue & Profit Summary -->
      <div class="bg-white shadow overflow-hidden sm:rounded-lg">
        <div class="px-4 py-5 sm:px-6">
          <h3 class="text-lg leading-6 font-medium text-gray-900">Revenue & Profit</h3>
          <p class="mt-1 max-w-2xl text-sm text-gray-500">
            Last 30 days performance
          </p>
        </div>
        
        <div class="border-t border-gray-200">
          <div class="grid grid-cols-1 md:grid-cols-3 divide-y md:divide-y-0 md:divide-x divide-gray-200">
            <div class="px-4 py-5 sm:px-6">
              <div class="text-sm font-medium text-gray-500">Total Revenue</div>
              <div class="mt-1 text-3xl font-semibold text-gray-900">${{ data.revenue_total.toFixed(2) }}</div>
            </div>
            <div class="px-4 py-5 sm:px-6">
              <div class="text-sm font-medium text-gray-500">Total Profit</div>
              <div class="mt-1 text-3xl font-semibold text-green-600">${{ data.profit_total.toFixed(2) }}</div>
            </div>
            <div class="px-4 py-5 sm:px-6">
              <div class="text-sm font-medium text-gray-500">Profit Margin</div>
              <div class="mt-1 text-3xl font-semibold text-gray-900">{{ data.profit_margin.toFixed(1) }}%</div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { api } from '../services/api'

const loading = ref(true)
const error = ref(null)
const data = ref({
  locations: 0,
  machines: 0,
  products: 0,
  low_stock_items: [],
  low_stock_count: 0,
  recent_restocks: 0,
  revenue_total: 0,
  profit_total: 0,
  profit_margin: 0
})

// Get stock level CSS class based on quantity
const getStockLevelClass = (quantity) => {
  if (quantity <= 0) return 'bg-red-100 text-red-800'
  if (quantity <= 3) return 'bg-yellow-100 text-yellow-800'
  return 'bg-blue-100 text-blue-800'
}

onMounted(async () => {
  try {
    const response = await api.getDashboardData()
    data.value = response.data
  } catch (err) {
    console.error('Error fetching dashboard data:', err)
    error.value = 'Failed to load dashboard data'
  } finally {
    loading.value = false
  }
})
</script> 