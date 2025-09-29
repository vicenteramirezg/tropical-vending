<template>
  <div class="bg-white shadow-lg rounded-xl mb-6 overflow-hidden">
    <div class="px-6 py-5 border-b border-gray-200">
      <div class="flex justify-between items-center">
        <div>
          <h3 class="text-lg leading-6 font-semibold text-gray-900">Machine Performance</h3>
          <p class="mt-1 text-sm text-gray-500">
            Machine efficiency and revenue generation
          </p>
        </div>
        <div class="flex space-x-2">
          <button
            @click="viewMode = 'efficiency'"
            :class="[
              'px-3 py-1.5 text-xs font-medium rounded-md transition-colors',
              viewMode === 'efficiency' 
                ? 'bg-primary-100 text-primary-800' 
                : 'text-gray-600 hover:text-gray-900'
            ]"
          >
            Efficiency
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
        </div>
      </div>
    </div>
    
    <div class="overflow-hidden">
      <div class="overflow-x-auto">
        <table class="min-w-full divide-y divide-gray-200">
          <thead class="bg-gray-50">
            <tr>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Machine</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Location</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Demand</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Revenue</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Profit</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Efficiency</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Products</th>
            </tr>
          </thead>
          <tbody class="bg-white divide-y divide-gray-200">
            <tr
              v-for="(machine, index) in sortedMachines"
              :key="machine.machine_id"
              class="hover:bg-gray-50 transition-colors duration-150"
            >
              <td class="px-6 py-4 whitespace-nowrap">
                <div class="flex items-center">
                  <div class="flex-shrink-0 w-8 h-8 bg-blue-100 rounded-full flex items-center justify-center">
                    <span class="text-xs font-semibold text-blue-800">{{ index + 1 }}</span>
                  </div>
                  <div class="ml-3">
                    <div class="text-sm font-semibold text-gray-900">{{ machine.machine_name }}</div>
                    <div class="text-xs text-gray-500">{{ machine.machine_type }} {{ machine.machine_model }}</div>
                  </div>
                </div>
              </td>
              <td class="px-6 py-4 whitespace-nowrap">
                <div class="text-sm text-gray-900">{{ machine.location_name }}</div>
              </td>
              <td class="px-6 py-4 whitespace-nowrap">
                <div class="text-sm font-semibold text-gray-900">{{ formatNumber(machine.total_demand) }}</div>
                <div class="text-xs text-gray-500">{{ formatNumber(machine.avg_demand_per_restock || 0) }}/restock</div>
              </td>
              <td class="px-6 py-4 whitespace-nowrap">
                <div class="text-sm font-semibold text-gray-900">${{ formatMoney(machine.total_revenue) }}</div>
                <div class="text-xs text-gray-500">{{ machine.restock_count }} restocks</div>
              </td>
              <td class="px-6 py-4 whitespace-nowrap">
                <div class="text-sm font-semibold text-gray-900">${{ formatMoney(machine.total_profit) }}</div>
                <div class="text-xs text-gray-500">
                  {{ machine.total_revenue > 0 ? ((machine.total_profit / machine.total_revenue) * 100).toFixed(1) : 0 }}% margin
                </div>
              </td>
              <td class="px-6 py-4 whitespace-nowrap">
                <div class="flex items-center">
                  <div class="flex-shrink-0">
                    <div
                      class="w-8 h-8 rounded-full flex items-center justify-center text-xs font-semibold text-white"
                      :class="getEfficiencyColor(machine.efficiency_score)"
                    >
                      {{ getEfficiencyGrade(machine.efficiency_score) }}
                    </div>
                  </div>
                  <div class="ml-2">
                    <div class="text-sm font-semibold text-gray-900">${{ formatMoney(machine.efficiency_score || 0) }}</div>
                    <div class="text-xs text-gray-500">per restock</div>
                  </div>
                </div>
              </td>
              <td class="px-6 py-4 whitespace-nowrap">
                <span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-gray-100 text-gray-800">
                  {{ machine.product_count }} products
                </span>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
    
    <!-- Performance Summary -->
    <div class="bg-gray-50 px-6 py-4">
      <div class="grid grid-cols-1 md:grid-cols-4 gap-4 text-center">
        <div>
          <div class="text-lg font-semibold text-gray-900">{{ machines.length }}</div>
          <div class="text-sm text-gray-500">Total Machines</div>
        </div>
        <div>
          <div class="text-lg font-semibold text-green-600">
            ${{ formatMoney(totalRevenue) }}
          </div>
          <div class="text-sm text-gray-500">Total Revenue</div>
        </div>
        <div>
          <div class="text-lg font-semibold text-blue-600">
            ${{ formatMoney(avgEfficiency) }}
          </div>
          <div class="text-sm text-gray-500">Avg Efficiency</div>
        </div>
        <div>
          <div class="text-lg font-semibold text-purple-600">
            {{ topMachineCount }}
          </div>
          <div class="text-sm text-gray-500">High Performers</div>
        </div>
      </div>
    </div>
    
    <!-- Empty State -->
    <div v-if="!machines || machines.length === 0" class="text-center py-12">
      <svg xmlns="http://www.w3.org/2000/svg" class="h-12 w-12 mx-auto text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19.428 15.428a2 2 0 00-1.022-.547l-2.387-.477a6 6 0 00-3.86.517l-.318.158a6 6 0 01-3.86.517L6.05 15.21a2 2 0 00-1.806.547M8 4h8l-1 1v5.172a2 2 0 00.586 1.414l5 5c1.26 1.26.367 3.414-1.415 3.414H4.828c-1.782 0-2.674-2.154-1.414-3.414l5-5A2 2 0 009 7.172V5L8 4z" />
      </svg>
      <h3 class="mt-2 text-sm font-medium text-gray-900">No machine data</h3>
      <p class="mt-1 text-sm text-gray-500">No analytics data available for the selected time period.</p>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'

const props = defineProps({
  machines: {
    type: Array,
    default: () => []
  }
})

const viewMode = ref('efficiency')

// Sort machines based on view mode
const sortedMachines = computed(() => {
  if (!props.machines || props.machines.length === 0) return []
  
  const machinesCopy = [...props.machines]
  
  switch (viewMode.value) {
    case 'efficiency':
      return machinesCopy.sort((a, b) => (b.efficiency_score || 0) - (a.efficiency_score || 0))
    case 'demand':
      return machinesCopy.sort((a, b) => b.total_demand - a.total_demand)
    case 'revenue':
      return machinesCopy.sort((a, b) => b.total_revenue - a.total_revenue)
    default:
      return machinesCopy
  }
})

// Calculate summary statistics
const totalRevenue = computed(() => {
  return props.machines?.reduce((sum, machine) => sum + machine.total_revenue, 0) || 0
})

const avgEfficiency = computed(() => {
  if (!props.machines || props.machines.length === 0) return 0
  const validMachines = props.machines.filter(m => m.efficiency_score > 0)
  if (validMachines.length === 0) return 0
  return validMachines.reduce((sum, machine) => sum + machine.efficiency_score, 0) / validMachines.length
})

const topMachineCount = computed(() => {
  return props.machines?.filter(machine => machine.efficiency_score > avgEfficiency.value).length || 0
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

// Get efficiency color based on score
const getEfficiencyColor = (score) => {
  if (score >= 1000) return 'bg-green-500'
  if (score >= 500) return 'bg-yellow-500'
  if (score >= 100) return 'bg-orange-500'
  return 'bg-red-500'
}

// Get efficiency grade
const getEfficiencyGrade = (score) => {
  if (score >= 1000) return 'A+'
  if (score >= 500) return 'A'
  if (score >= 300) return 'B'
  if (score >= 150) return 'C'
  if (score >= 50) return 'D'
  return 'F'
}
</script>
