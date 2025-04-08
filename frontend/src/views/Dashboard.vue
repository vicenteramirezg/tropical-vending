<template>
  <div class="min-h-screen flex flex-col">
    <div class="flex-grow container mx-auto px-4 py-8">
      <h1 class="text-2xl font-bold text-gray-900 mb-6">Dashboard</h1>
      
      <!-- Filter Controls -->
      <div class="bg-white p-4 sm:p-5 shadow-lg rounded-xl mb-6">
        <div class="flex flex-col sm:flex-row flex-wrap items-start sm:items-center gap-4">
          <div class="w-full sm:w-auto">
            <label for="timeRange" class="block text-sm font-medium text-gray-700 mb-1">Time Period</label>
            <select
              id="timeRange"
              v-model="filters.timeRange"
              class="block w-full sm:w-48 border-gray-300 rounded-md shadow-sm focus:ring-primary-500 focus:border-primary-500 sm:text-sm"
              @change="applyFilters"
            >
              <option value="today">Today</option>
              <option value="yesterday">Yesterday</option>
              <option value="7">Last 7 days</option>
              <option value="30">Last 30 days</option>
              <option value="90">Last 90 days</option>
            </select>
          </div>
          
          <div class="w-full sm:w-auto">
            <label for="location" class="block text-sm font-medium text-gray-700 mb-1">Location</label>
            <select
              id="location"
              v-model="filters.location"
              class="block w-full sm:w-48 border-gray-300 rounded-md shadow-sm focus:ring-primary-500 focus:border-primary-500 sm:text-sm"
              @change="applyFilters"
            >
              <option value="">All Locations</option>
              <option v-for="location in locations" :key="location.id" :value="location.id">
                {{ location.name }}
              </option>
            </select>
          </div>
          
          <div class="w-full sm:w-auto">
            <label for="machineType" class="block text-sm font-medium text-gray-700 mb-1">Machine Type</label>
            <select
              id="machineType"
              v-model="filters.machineType"
              class="block w-full sm:w-48 border-gray-300 rounded-md shadow-sm focus:ring-primary-500 focus:border-primary-500 sm:text-sm"
              @change="applyFilters"
            >
              <option value="">All Types</option>
              <option value="Snack">Snack</option>
              <option value="Soda">Soda</option>
              <option value="Combo">Combo</option>
            </select>
          </div>
          
          <div class="w-full sm:w-auto mt-2 sm:mt-0">
            <button
              type="button"
              @click="applyFilters"
              class="w-full sm:w-auto inline-flex items-center justify-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-primary-600 hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500 transition-colors duration-150"
            >
              <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 mr-1.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 4a1 1 0 011-1h16a1 1 0 011 1v2.586a1 1 0 01-.293.707l-6.414 6.414a1 1 0 00-.293.707V17l-4 4v-6.586a1 1 0 00-.293-.707L3.293 7.293A1 1 0 013 6.586V4z" />
              </svg>
              Apply Filters
            </button>
          </div>
        </div>
      </div>
      
      <div v-if="loading" class="flex justify-center py-20">
        <div class="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-primary-500"></div>
      </div>
      
      <div v-else>
        <!-- KPI Cards -->
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
        
        <!-- Low Stock Items -->
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
        
        <!-- Revenue & Profit Summary -->
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
      </div>
    </div>
    
    <!-- Footer -->
    <AppFooter />
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { api } from '../services/api'
import AppFooter from '../components/AppFooter.vue'

const loading = ref(true)
const error = ref(null)
const locations = ref([])
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

const filters = ref({
  timeRange: '30',
  location: '',
  machineType: ''
})

// Get stock level CSS class based on quantity
const getStockLevelClass = (quantity) => {
  if (quantity <= 0) return 'bg-red-100 text-red-800'
  if (quantity <= 3) return 'bg-yellow-100 text-yellow-800'
  return 'bg-blue-100 text-blue-800'
}

// Fetch locations for the dropdown
const fetchLocations = async () => {
  try {
    const response = await api.getLocations()
    locations.value = response.data
  } catch (err) {
    console.error('Error fetching locations:', err)
  }
}

// Apply filters and refresh dashboard data
const applyFilters = async () => {
  loading.value = true
  try {
    const params = {
      days: filters.value.timeRange,
      location: filters.value.location || undefined,
      machine_type: filters.value.machineType || undefined
    }
    
    const response = await api.getDashboardData(params)
    data.value = response.data
  } catch (err) {
    console.error('Error fetching dashboard data:', err)
    error.value = 'Failed to load dashboard data'
  } finally {
    loading.value = false
  }
}

onMounted(async () => {
  await fetchLocations()
  await applyFilters()
})
</script> 