<template>
  <div>
    <h1 class="text-2xl font-semibold text-gray-900 mb-6">Analytics</h1>
    
    <div v-if="loading" class="flex justify-center">
      <div class="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-primary-500"></div>
    </div>
    
    <div v-else-if="error" class="bg-red-50 border-l-4 border-red-400 p-4 mb-4">
      <div class="flex">
        <div class="flex-shrink-0">
          <span class="text-red-400">⚠</span>
        </div>
        <div class="ml-3">
          <p class="text-sm text-red-700">{{ error }}</p>
        </div>
      </div>
    </div>
    
    <div v-else>
      <!-- Filter Controls -->
      <div class="bg-white p-4 shadow rounded-lg mb-6">
        <div class="flex flex-wrap items-center gap-4">
          <div>
            <label for="dateRange" class="block text-sm font-medium text-gray-700 mb-1">Date Range</label>
            <select
              id="dateRange"
              v-model="filters.dateRange"
              class="block w-full border-gray-300 rounded-md shadow-sm focus:ring-primary-500 focus:border-primary-500 sm:text-sm"
              @change="applyFilters"
            >
              <option value="7">Last 7 days</option>
              <option value="30">Last 30 days</option>
              <option value="90">Last 90 days</option>
              <option value="365">Last 12 months</option>
              <option value="custom">Custom range</option>
            </select>
          </div>
          
          <div v-if="filters.dateRange === 'custom'" class="flex space-x-2">
            <div>
              <label for="startDate" class="block text-sm font-medium text-gray-700 mb-1">Start Date</label>
              <input
                type="date"
                id="startDate"
                v-model="filters.startDate"
                class="block w-full border-gray-300 rounded-md shadow-sm focus:ring-primary-500 focus:border-primary-500 sm:text-sm"
              >
            </div>
            <div>
              <label for="endDate" class="block text-sm font-medium text-gray-700 mb-1">End Date</label>
              <input
                type="date"
                id="endDate"
                v-model="filters.endDate"
                class="block w-full border-gray-300 rounded-md shadow-sm focus:ring-primary-500 focus:border-primary-500 sm:text-sm"
              >
            </div>
          </div>
          
          <div>
            <label for="location" class="block text-sm font-medium text-gray-700 mb-1">Location</label>
            <select
              id="location"
              v-model="filters.location"
              class="block w-full border-gray-300 rounded-md shadow-sm focus:ring-primary-500 focus:border-primary-500 sm:text-sm"
              @change="applyFilters"
            >
              <option value="">All Locations</option>
              <option v-for="location in locations" :key="location.id" :value="location.id">
                {{ location.name }}
              </option>
            </select>
          </div>
          
          <div class="self-end ml-auto mt-4">
            <button
              type="button"
              @click="applyFilters"
              class="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-primary-600 hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500"
            >
              Apply Filters
            </button>
          </div>
        </div>
      </div>
      
      <!-- Revenue & Profit Section -->
      <div class="bg-white shadow overflow-hidden sm:rounded-lg mb-6">
        <div class="px-4 py-5 sm:px-6">
          <h3 class="text-lg leading-6 font-medium text-gray-900">Revenue & Profit</h3>
          <p class="mt-1 max-w-2xl text-sm text-gray-500">
            Financial performance for the selected period
          </p>
        </div>
        
        <div class="border-t border-gray-200">
          <div class="grid grid-cols-1 md:grid-cols-3 divide-y md:divide-y-0 md:divide-x divide-gray-200">
            <div class="px-4 py-5 sm:px-6">
              <div class="text-sm font-medium text-gray-500">Total Revenue</div>
              <div class="mt-1 text-3xl font-semibold text-gray-900">${{ revenueProfitData.revenue.total.toFixed(2) }}</div>
              <div class="mt-1 text-sm text-gray-500">
                <span :class="revenueProfitData.revenue.change >= 0 ? 'text-green-600' : 'text-red-600'">
                  {{ revenueProfitData.revenue.change >= 0 ? '+' : '' }}{{ revenueProfitData.revenue.change.toFixed(1) }}%
                </span>
                vs previous period
              </div>
            </div>
            
            <div class="px-4 py-5 sm:px-6">
              <div class="text-sm font-medium text-gray-500">Total Profit</div>
              <div class="mt-1 text-3xl font-semibold text-green-600">${{ revenueProfitData.profit.total.toFixed(2) }}</div>
              <div class="mt-1 text-sm text-gray-500">
                <span :class="revenueProfitData.profit.change >= 0 ? 'text-green-600' : 'text-red-600'">
                  {{ revenueProfitData.profit.change >= 0 ? '+' : '' }}{{ revenueProfitData.profit.change.toFixed(1) }}%
                </span>
                vs previous period
              </div>
            </div>
            
            <div class="px-4 py-5 sm:px-6">
              <div class="text-sm font-medium text-gray-500">Profit Margin</div>
              <div class="mt-1 text-3xl font-semibold text-gray-900">{{ revenueProfitData.margin.total.toFixed(1) }}%</div>
              <div class="mt-1 text-sm text-gray-500">
                <span :class="revenueProfitData.margin.change >= 0 ? 'text-green-600' : 'text-red-600'">
                  {{ revenueProfitData.margin.change >= 0 ? '+' : '' }}{{ revenueProfitData.margin.change.toFixed(1) }}%
                </span>
                vs previous period
              </div>
            </div>
          </div>
        </div>
      </div>
      
      <!-- Stock Levels Section -->
      <div class="bg-white shadow overflow-hidden sm:rounded-lg mb-6">
        <div class="px-4 py-5 sm:px-6 flex justify-between items-center">
          <div>
            <h3 class="text-lg leading-6 font-medium text-gray-900">Stock Levels</h3>
            <p class="mt-1 max-w-2xl text-sm text-gray-500">
              Current inventory levels across machines
            </p>
          </div>
          <span 
            class="inline-flex items-center px-3 py-0.5 rounded-full text-sm font-medium"
            :class="stockLevelData.low_stock_count > 0 ? 'bg-red-100 text-red-800' : 'bg-green-100 text-green-800'"
          >
            {{ stockLevelData.low_stock_count }} items low stock
          </span>
        </div>
        
        <div class="border-t border-gray-200">
          <ul role="list" class="divide-y divide-gray-200">
            <li v-for="(item, index) in stockLevelData.items" :key="index" class="px-4 py-4 sm:px-6">
              <div class="flex items-center justify-between">
                <div>
                  <p class="text-sm font-medium text-primary-600 truncate">{{ item.product_name }}</p>
                  <p class="text-sm text-gray-500">{{ item.machine_name }} at {{ item.location_name }}</p>
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
      
      <!-- Product Demand Analysis -->
      <div class="bg-white shadow overflow-hidden sm:rounded-lg">
        <div class="px-4 py-5 sm:px-6">
          <h3 class="text-lg leading-6 font-medium text-gray-900">Product Demand Analysis</h3>
          <p class="mt-1 max-w-2xl text-sm text-gray-500">
            Sales performance by product
          </p>
        </div>
        
        <div class="border-t border-gray-200">
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
                <tr v-for="item in demandData.products" :key="item.product_id">
                  <td class="px-6 py-4 whitespace-nowrap">
                    <div class="text-sm font-medium text-gray-900">{{ item.product_name }}</div>
                  </td>
                  <td class="px-6 py-4 whitespace-nowrap text-center">
                    <div class="text-sm text-gray-900">{{ item.units_sold }}</div>
                  </td>
                  <td class="px-6 py-4 whitespace-nowrap text-center">
                    <div class="text-sm text-gray-900">${{ item.revenue.toFixed(2) }}</div>
                  </td>
                  <td class="px-6 py-4 whitespace-nowrap text-center">
                    <div class="text-sm text-gray-900">${{ item.profit.toFixed(2) }}</div>
                  </td>
                  <td class="px-6 py-4 whitespace-nowrap text-center">
                    <span 
                      class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium"
                      :class="getTrendClass(item.trend)"
                    >
                      {{ formatTrend(item.trend) }}
                    </span>
                  </td>
                </tr>
              </tbody>
            </table>
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
const locations = ref([])

// Filter states
const filters = ref({
  dateRange: '30',
  startDate: '',
  endDate: '',
  location: ''
})

// Data states
const revenueProfitData = ref({
  revenue: { total: 0, change: 0 },
  profit: { total: 0, change: 0 },
  margin: { total: 0, change: 0 }
})

const stockLevelData = ref({
  low_stock_count: 0,
  items: []
})

const demandData = ref({
  products: []
})

// Helper functions
const getStockLevelClass = (quantity) => {
  if (quantity <= 0) return 'bg-red-100 text-red-800'
  if (quantity <= 3) return 'bg-yellow-100 text-yellow-800'
  return 'bg-blue-100 text-blue-800'
}

const getTrendClass = (trend) => {
  if (trend > 10) return 'bg-green-100 text-green-800'
  if (trend < -10) return 'bg-red-100 text-red-800'
  return 'bg-gray-100 text-gray-800'
}

const formatTrend = (trend) => {
  return `${trend >= 0 ? '+' : ''}${trend.toFixed(1)}%`
}

// Fetch all locations
const fetchLocations = async () => {
  try {
    const response = await api.getLocations()
    locations.value = response.data
  } catch (err) {
    console.error('Error fetching locations:', err)
  }
}

// Fetch Revenue & Profit data
const fetchRevenueProfitData = async () => {
  try {
    const params = {
      days: filters.value.dateRange !== 'custom' ? filters.value.dateRange : undefined,
      start_date: filters.value.dateRange === 'custom' ? filters.value.startDate : undefined,
      end_date: filters.value.dateRange === 'custom' ? filters.value.endDate : undefined,
      location: filters.value.location || undefined
    }
    
    const response = await api.getRevenueProfitData(params)
    revenueProfitData.value = response.data
  } catch (err) {
    console.error('Error fetching revenue/profit data:', err)
    error.value = 'Failed to load revenue and profit data'
  }
}

// Fetch Stock Levels data
const fetchStockLevelData = async () => {
  try {
    const params = {
      location: filters.value.location || undefined
    }
    
    const response = await api.getStockLevels(params)
    stockLevelData.value = response.data
  } catch (err) {
    console.error('Error fetching stock level data:', err)
    error.value = 'Failed to load stock level data'
  }
}

// Fetch Demand Analysis data
const fetchDemandData = async () => {
  try {
    const params = {
      days: filters.value.dateRange !== 'custom' ? filters.value.dateRange : undefined,
      start_date: filters.value.dateRange === 'custom' ? filters.value.startDate : undefined,
      end_date: filters.value.dateRange === 'custom' ? filters.value.endDate : undefined,
      location: filters.value.location || undefined
    }
    
    const response = await api.getDemandAnalysis(params)
    demandData.value = response.data
  } catch (err) {
    console.error('Error fetching demand analysis data:', err)
    error.value = 'Failed to load demand analysis data'
  }
}

// Apply filters and refresh data
const applyFilters = async () => {
  loading.value = true
  error.value = null
  
  try {
    // Set default date range if custom is selected but dates are not
    if (filters.value.dateRange === 'custom' && (!filters.value.startDate || !filters.value.endDate)) {
      const today = new Date()
      const thirtyDaysAgo = new Date(today)
      thirtyDaysAgo.setDate(today.getDate() - 30)
      
      if (!filters.value.endDate) {
        filters.value.endDate = today.toISOString().split('T')[0]
      }
      
      if (!filters.value.startDate) {
        filters.value.startDate = thirtyDaysAgo.toISOString().split('T')[0]
      }
    }
    
    await Promise.all([
      fetchRevenueProfitData(),
      fetchStockLevelData(),
      fetchDemandData()
    ])
  } catch (err) {
    console.error('Error refreshing data:', err)
    error.value = 'Failed to refresh analytics data'
  } finally {
    loading.value = false
  }
}

// Initialize data on component mount
onMounted(async () => {
  try {
    await fetchLocations()
    await applyFilters()
  } catch (err) {
    console.error('Error initializing analytics:', err)
    error.value = 'Failed to load analytics data'
  } finally {
    loading.value = false
  }
})
</script> 