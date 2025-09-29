<template>
  <div class="bg-white shadow-lg rounded-xl mb-6 overflow-hidden">
    <div class="px-6 py-5 border-b border-gray-200">
      <div class="flex justify-between items-center">
        <div>
          <h3 class="text-lg leading-6 font-semibold text-gray-900">Location Performance</h3>
          <p class="mt-1 text-sm text-gray-500">
            Revenue and demand by location
          </p>
        </div>
        <div class="flex space-x-2">
          <button
            @click="viewMode = 'revenue'"
            :class="[
              'px-3 py-1.5 text-xs font-medium rounded-md transition-colors',
              viewMode === 'revenue' 
                ? 'bg-primary-100 text-primary-800' 
                : 'text-gray-600 hover:text-gray-900'
            ]"
          >
            Revenue
          </button>
          <button
            @click="viewMode = 'demand'"
            :class="[
              'px-3 py-1.5 text-xs font-medium rounded-md transition-colors',
              viewMode === 'demand' 
                ? 'bg-primary-100 text-primary-800' 
                : 'text-gray-600 hover:text-gray-900'
            ]"
          >
            Demand
          </button>
          <button
            @click="viewMode = 'efficiency'"
            :class="[
              'px-3 py-1.5 text-xs font-medium rounded-md transition-colors',
              viewMode === 'efficiency' 
                ? 'bg-primary-100 text-primary-800' 
                : 'text-gray-600 hover:text-gray-900'
            ]"
          >
            Per Machine
          </button>
        </div>
      </div>
    </div>
    
    <div class="p-6">
      <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        <div
          v-for="(location, index) in sortedLocations"
          :key="location.location_id"
          class="relative bg-gradient-to-br from-gray-50 to-white border border-gray-200 rounded-lg p-4 hover:shadow-md transition-all duration-200"
        >
          <!-- Rank Badge -->
          <div class="absolute -top-2 -left-2 w-6 h-6 bg-primary-600 text-white rounded-full flex items-center justify-center text-xs font-bold">
            {{ index + 1 }}
          </div>
          
          <!-- Location Header -->
          <div class="mb-4">
            <h4 class="text-lg font-semibold text-gray-900">{{ location.location_name }}</h4>
            <p class="text-sm text-gray-500">
              {{ location.machine_count }} machines • {{ location.product_count }} products
            </p>
          </div>
          
          <!-- Performance Metrics -->
          <div class="space-y-3">
            <!-- Primary Metric (based on view mode) -->
            <div class="text-center py-3 bg-white rounded-lg border">
              <div class="text-2xl font-bold" :class="getPrimaryColor(index)">
                {{ formatPrimaryMetric(location) }}
              </div>
              <div class="text-xs text-gray-600">{{ getPrimaryLabel() }}</div>
            </div>
            
            <!-- Secondary Metrics -->
            <div class="grid grid-cols-2 gap-2 text-center">
              <div class="p-2 bg-green-50 rounded">
                <div class="text-sm font-semibold text-green-800">
                  ${{ formatMoney(location.total_revenue) }}
                </div>
                <div class="text-xs text-green-600">Revenue</div>
              </div>
              <div class="p-2 bg-blue-50 rounded">
                <div class="text-sm font-semibold text-blue-800">
                  {{ formatNumber(location.total_demand) }}
                </div>
                <div class="text-xs text-blue-600">Demand</div>
              </div>
            </div>
            
            <div class="grid grid-cols-2 gap-2 text-center">
              <div class="p-2 bg-purple-50 rounded">
                <div class="text-sm font-semibold text-purple-800">
                  ${{ formatMoney(location.total_profit) }}
                </div>
                <div class="text-xs text-purple-600">Profit</div>
              </div>
              <div class="p-2 bg-orange-50 rounded">
                <div class="text-sm font-semibold text-orange-800">
                  {{ location.restock_count }}
                </div>
                <div class="text-xs text-orange-600">Restocks</div>
              </div>
            </div>
          </div>
          
          <!-- Performance Bar -->
          <div class="mt-4">
            <div class="flex justify-between items-center mb-1">
              <span class="text-xs text-gray-600">Performance</span>
              <span class="text-xs font-medium text-gray-900">
                {{ getPerformanceScore(location).toFixed(1) }}%
              </span>
            </div>
            <div class="w-full bg-gray-200 rounded-full h-2">
              <div
                class="h-2 rounded-full transition-all duration-500"
                :class="getPerformanceColor(location)"
                :style="{ width: `${Math.min(100, getPerformanceScore(location))}%` }"
              ></div>
            </div>
          </div>
        </div>
      </div>
    </div>
    
    <!-- Summary Statistics -->
    <div class="bg-gray-50 px-6 py-4 border-t">
      <div class="grid grid-cols-2 md:grid-cols-4 gap-4 text-center">
        <div>
          <div class="text-lg font-semibold text-gray-900">{{ locations.length }}</div>
          <div class="text-sm text-gray-500">Locations</div>
        </div>
        <div>
          <div class="text-lg font-semibold text-green-600">
            ${{ formatMoney(totalRevenue) }}
          </div>
          <div class="text-sm text-gray-500">Total Revenue</div>
        </div>
        <div>
          <div class="text-lg font-semibold text-blue-600">
            {{ totalMachines }}
          </div>
          <div class="text-sm text-gray-500">Total Machines</div>
        </div>
        <div>
          <div class="text-lg font-semibold text-purple-600">
            {{ topLocationCount }}
          </div>
          <div class="text-sm text-gray-500">Top Performers</div>
        </div>
      </div>
    </div>
    
    <!-- Empty State -->
    <div v-if="!locations || locations.length === 0" class="text-center py-12">
      <svg xmlns="http://www.w3.org/2000/svg" class="h-12 w-12 mx-auto text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z" />
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 11a3 3 0 11-6 0 3 3 0 016 0z" />
      </svg>
      <h3 class="mt-2 text-sm font-medium text-gray-900">No location data</h3>
      <p class="mt-1 text-sm text-gray-500">No analytics data available for the selected time period.</p>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'

const props = defineProps({
  locations: {
    type: Array,
    default: () => []
  }
})

const viewMode = ref('revenue')

// Sort locations based on view mode
const sortedLocations = computed(() => {
  if (!props.locations || props.locations.length === 0) return []
  
  const locationsCopy = [...props.locations]
  
  switch (viewMode.value) {
    case 'revenue':
      return locationsCopy.sort((a, b) => b.total_revenue - a.total_revenue)
    case 'demand':
      return locationsCopy.sort((a, b) => b.total_demand - a.total_demand)
    case 'efficiency':
      return locationsCopy.sort((a, b) => b.avg_revenue_per_machine - a.avg_revenue_per_machine)
    default:
      return locationsCopy
  }
})

// Calculate summary statistics
const totalRevenue = computed(() => {
  return props.locations?.reduce((sum, location) => sum + location.total_revenue, 0) || 0
})

const totalMachines = computed(() => {
  return props.locations?.reduce((sum, location) => sum + location.machine_count, 0) || 0
})

const avgRevenue = computed(() => {
  if (!props.locations || props.locations.length === 0) return 0
  return totalRevenue.value / props.locations.length
})

const topLocationCount = computed(() => {
  return props.locations?.filter(location => location.total_revenue > avgRevenue.value).length || 0
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

// Get primary metric based on view mode
const formatPrimaryMetric = (location) => {
  switch (viewMode.value) {
    case 'revenue':
      return '$' + formatMoney(location.total_revenue)
    case 'demand':
      return formatNumber(location.total_demand)
    case 'efficiency':
      return '$' + formatMoney(location.avg_revenue_per_machine || 0)
    default:
      return '$' + formatMoney(location.total_revenue)
  }
}

// Get primary label
const getPrimaryLabel = () => {
  switch (viewMode.value) {
    case 'revenue':
      return 'Total Revenue'
    case 'demand':
      return 'Total Demand'
    case 'efficiency':
      return 'Revenue/Machine'
    default:
      return 'Total Revenue'
  }
}

// Get primary color based on rank
const getPrimaryColor = (index) => {
  if (index === 0) return 'text-yellow-600' // Gold
  if (index === 1) return 'text-gray-600'   // Silver
  if (index === 2) return 'text-orange-600' // Bronze
  return 'text-primary-600'
}

// Calculate performance score (relative to max)
const getPerformanceScore = (location) => {
  const maxRevenue = Math.max(...(props.locations?.map(l => l.total_revenue) || [1]))
  return (location.total_revenue / maxRevenue) * 100
}

// Get performance color
const getPerformanceColor = (location) => {
  const score = getPerformanceScore(location)
  if (score >= 80) return 'bg-green-500'
  if (score >= 60) return 'bg-yellow-500'
  if (score >= 40) return 'bg-orange-500'
  return 'bg-red-500'
}
</script>
