<template>
  <div>
    <h1 class="text-2xl font-semibold text-gray-900 mb-6">Analytics</h1>
    
    <div v-if="loading" class="flex justify-center py-20">
      <div class="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-primary-500"></div>
    </div>
    
    <div v-else-if="error" class="bg-red-50 border-l-4 border-red-400 p-4 mb-6 rounded-r-lg shadow-sm">
      <div class="flex">
        <div class="flex-shrink-0">
          <svg class="h-5 w-5 text-red-400" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor">
            <path fill-rule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clip-rule="evenodd" />
          </svg>
        </div>
        <div class="ml-3">
          <p class="text-sm text-red-700">{{ error }}</p>
        </div>
      </div>
    </div>
    
    <div v-else>
      <!-- Filter Controls -->
      <div class="bg-white p-5 shadow-lg rounded-xl mb-6">
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
              class="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-primary-600 hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500 transition-colors duration-150"
            >
              <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 mr-1.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 4a1 1 0 011-1h16a1 1 0 011 1v2.586a1 1 0 01-.293.707l-6.414 6.414a1 1 0 00-.293.707V17l-4 4v-6.586a1 1 0 00-.293-.707L3.293 7.293A1 1 0 013 6.586V4z" />
              </svg>
              Apply Filters
            </button>
          </div>
        </div>
      </div>
      
      <!-- Revenue & Profit Section -->
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
              <div class="mt-2 text-3xl font-bold text-gray-900">${{ (revenueProfitData.revenue?.total || 0).toFixed(2) }}</div>
              <div class="mt-2 text-sm text-gray-500 flex items-center">
                <span 
                  :class="(revenueProfitData.revenue?.change || 0) >= 0 ? 'text-green-600' : 'text-red-600'"
                  class="flex items-center"
                >
                  <svg v-if="(revenueProfitData.revenue?.change || 0) >= 0" xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 mr-1" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6" />
                  </svg>
                  <svg v-else xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 mr-1" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 17h8m0 0V9m0 8l-8-8-4 4-6-6" />
                  </svg>
                  {{ (revenueProfitData.revenue?.change || 0) >= 0 ? '+' : '' }}{{ (revenueProfitData.revenue?.change || 0).toFixed(1) }}%
                </span>
                <span class="ml-1">vs previous period</span>
              </div>
            </div>
            
            <div class="px-6 py-5">
              <div class="text-sm font-medium text-gray-500">Total Profit</div>
              <div class="mt-2 text-3xl font-bold text-green-600">${{ (revenueProfitData.profit?.total || 0).toFixed(2) }}</div>
              <div class="mt-2 text-sm text-gray-500 flex items-center">
                <span 
                  :class="(revenueProfitData.profit?.change || 0) >= 0 ? 'text-green-600' : 'text-red-600'"
                  class="flex items-center"
                >
                  <svg v-if="(revenueProfitData.profit?.change || 0) >= 0" xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 mr-1" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6" />
                  </svg>
                  <svg v-else xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 mr-1" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 17h8m0 0V9m0 8l-8-8-4 4-6-6" />
                  </svg>
                  {{ (revenueProfitData.profit?.change || 0) >= 0 ? '+' : '' }}{{ (revenueProfitData.profit?.change || 0).toFixed(1) }}%
                </span>
                <span class="ml-1">vs previous period</span>
              </div>
            </div>
            
            <div class="px-6 py-5">
              <div class="text-sm font-medium text-gray-500">Profit Margin</div>
              <div class="mt-2 text-3xl font-bold text-gray-900">{{ (revenueProfitData.margin?.total || 0).toFixed(1) }}%</div>
              <div class="mt-2 text-sm text-gray-500 flex items-center">
                <span 
                  :class="(revenueProfitData.margin?.change || 0) >= 0 ? 'text-green-600' : 'text-red-600'"
                  class="flex items-center"
                >
                  <svg v-if="(revenueProfitData.margin?.change || 0) >= 0" xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 mr-1" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6" />
                  </svg>
                  <svg v-else xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 mr-1" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 17h8m0 0V9m0 8l-8-8-4 4-6-6" />
                  </svg>
                  {{ (revenueProfitData.margin?.change || 0) >= 0 ? '+' : '' }}{{ (revenueProfitData.margin?.change || 0).toFixed(1) }}%
                </span>
                <span class="ml-1">vs previous period</span>
              </div>
            </div>
          </div>
        </div>
      </div>
      
      <!-- Stock Levels Section -->
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
            :class="stockLevelData.low_stock_count > 0 ? 'bg-red-100 text-red-800' : 'bg-green-100 text-green-800'"
          >
            <svg v-if="stockLevelData.low_stock_count > 0" xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 mr-1.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
            </svg>
            <svg v-else xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 mr-1.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            {{ stockLevelData.low_stock_count }} items low stock
          </span>
        </div>
        
        <div>
          <ul role="list" class="divide-y divide-gray-200">
            <li v-for="(item, index) in stockLevelData.items" :key="index" class="px-6 py-4 hover:bg-gray-50 transition-colors duration-150">
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
      
      <!-- Product Demand Analysis -->
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
                <tr v-for="item in demandData.products" :key="item.product_id" class="hover:bg-gray-50 transition-colors duration-150">
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
          <div v-if="demandData.unit_counts && demandData.unit_counts.length > 0" class="mt-6 px-6">
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
          
          <div v-else-if="demandData.products && demandData.products.length > 0 && (!demandData.unit_counts || demandData.unit_counts.length === 0)" class="px-6 py-4 text-center">
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
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { api } from '../services/api'
import { getCurrentDateLocal, formatDateShort } from '../utils/dateUtils'

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
  unit_counts: [],
  products: []
})

// Computed property for sorted demand counts
const sortedDemandCounts = computed(() => {
  if (!demandData.value.unit_counts) return []
  
  return [...demandData.value.unit_counts]
    .sort((a, b) => {
      // Sort by location, then machine, then product, then date
      if (a.location_name !== b.location_name) return a.location_name.localeCompare(b.location_name)
      if (a.machine_name !== b.machine_name) return a.machine_name.localeCompare(b.machine_name)
      if (a.product_name !== b.product_name) return a.product_name.localeCompare(b.product_name)
      return new Date(b.end_date) - new Date(a.end_date) // Most recent first
    })
})

// Helper functions
const getStockLevelClass = (quantity) => {
  if (quantity <= 0) return 'bg-red-100 text-red-800'
  if (quantity <= 3) return 'bg-yellow-100 text-yellow-800'
  return 'bg-blue-100 text-blue-800'
}

const getTrendClass = (trend) => {
  if (trend === undefined || trend === null) return 'bg-gray-100 text-gray-800'
  if (trend > 10) return 'bg-green-100 text-green-800'
  if (trend < -10) return 'bg-red-100 text-red-800'
  return 'bg-gray-100 text-gray-800'
}

const formatTrend = (trend) => {
  if (trend === undefined || trend === null) return '+0.0%'
  return `${trend >= 0 ? '+' : ''}${trend.toFixed(1)}%`
}

// formatDateShort is now imported from dateUtils

// Format daily demand with 1 decimal place
const formatDailyDemand = (demand) => {
  if (demand === undefined || demand === null) return '0.0/day'
  return demand.toFixed(1) + '/day'
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
    
    // Ensure we have a properly structured object
    if (!response.data) {
      revenueProfitData.value = {
        revenue: { total: 0, change: 0 },
        profit: { total: 0, change: 0 },
        margin: { total: 0, change: 0 }
      }
      return
    }
    
    revenueProfitData.value = {
      revenue: {
        total: response.data.revenue?.total || 0,
        change: response.data.revenue?.change || 0
      },
      profit: {
        total: response.data.profit?.total || 0,
        change: response.data.profit?.change || 0
      },
      margin: {
        total: response.data.margin?.total || 0,
        change: response.data.margin?.change || 0
      }
    }
  } catch (err) {
    console.error('Error fetching revenue/profit data:', err)
    error.value = 'Failed to load revenue and profit data'
    // Set default values on error
    revenueProfitData.value = {
      revenue: { total: 0, change: 0 },
      profit: { total: 0, change: 0 },
      margin: { total: 0, change: 0 }
    }
  }
}

// Fetch Stock Levels data
const fetchStockLevelData = async () => {
  try {
    const params = {
      location: filters.value.location || undefined
    }
    
    const response = await api.getStockLevels(params)
    
    // Ensure we have a properly structured object
    if (!response.data) {
      stockLevelData.value = {
        low_stock_count: 0,
        items: []
      }
      return
    }
    
    stockLevelData.value = {
      low_stock_count: response.data.low_stock_count || 0,
      items: response.data.items || []
    }
  } catch (err) {
    console.error('Error fetching stock level data:', err)
    error.value = 'Failed to load stock level data'
    // Set default values on error
    stockLevelData.value = {
      low_stock_count: 0,
      items: []
    }
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
    console.log('Demand analysis data:', response.data)
    
    // Ensure we have a properly structured object with default values
    if (!response.data) {
      demandData.value = {
        products: [],
        unit_counts: []
      }
      return
    }
    
    // Handle both old and new response formats
    if (Array.isArray(response.data)) {
      // Old format - just products array
      demandData.value = {
        products: response.data || [],
        unit_counts: []
      }
    } else {
      // New format with both unit_counts and products
      demandData.value = {
        products: response.data.products || [],
        unit_counts: response.data.unit_counts || []
      }
      
      // Convert date strings to Date objects for better sorting
      if (demandData.value.unit_counts && demandData.value.unit_counts.length > 0) {
        demandData.value.unit_counts.forEach(count => {
          if (count.start_date) count.start_date = new Date(count.start_date)
          if (count.end_date) count.end_date = new Date(count.end_date)
        })
      }
    }
  } catch (err) {
    console.error('Error fetching demand analysis data:', err)
    error.value = 'Failed to load demand analysis data'
    // Set default values on error
    demandData.value = {
      products: [],
      unit_counts: []
    }
  }
}

// Apply filters and refresh data
const applyFilters = async () => {
  loading.value = true
  error.value = null
  
  try {
    // Set default date range if custom is selected but dates are not
    if (filters.value.dateRange === 'custom' && (!filters.value.startDate || !filters.value.endDate)) {
      const today = getCurrentDateLocal()
      const thirtyDaysAgo = new Date()
      thirtyDaysAgo.setDate(thirtyDaysAgo.getDate() - 30)
      const thirtyDaysAgoFormatted = thirtyDaysAgo.toLocaleDateString('en-CA', {timeZone: 'America/New_York'}) // YYYY-MM-DD format
      
      if (!filters.value.endDate) {
        filters.value.endDate = today
      }
      
      if (!filters.value.startDate) {
        filters.value.startDate = thirtyDaysAgoFormatted
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