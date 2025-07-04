<template>
  <div class="demand-analysis">
    <div class="flex justify-between items-center mb-6">
      <h1 class="text-2xl font-semibold text-gray-900">Demand Analysis</h1>
      <div class="flex space-x-4">
        <select v-model="selectedMachine" @change="fetchData" class="form-select">
          <option value="">All Machines</option>
          <option v-for="machine in machines" :key="machine.id" :value="machine.id">
            {{ machine.name }} - {{ machine.location_name }}
          </option>
        </select>
        <select v-model="selectedProduct" @change="fetchData" class="form-select">
          <option value="">All Products</option>
          <option v-for="product in products" :key="product.id" :value="product.id">
            {{ product.name }}
          </option>
        </select>
        <select v-model="selectedDays" @change="fetchData" class="form-select">
          <option value="7">Last 7 Days</option>
          <option value="30">Last 30 Days</option>
          <option value="60">Last 60 Days</option>
          <option value="90">Last 90 Days</option>
        </select>
      </div>
    </div>

    <!-- Summary Cards -->
    <div class="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
      <div class="bg-white p-6 rounded-lg shadow">
        <h3 class="text-lg font-medium text-gray-900 mb-2">Total Products Tracked</h3>
        <p class="text-3xl font-bold text-blue-600">{{ summary.totalProducts }}</p>
      </div>
      <div class="bg-white p-6 rounded-lg shadow">
        <h3 class="text-lg font-medium text-gray-900 mb-2">Total Machines</h3>
        <p class="text-3xl font-bold text-green-600">{{ summary.totalMachines }}</p>
      </div>
      <div class="bg-white p-6 rounded-lg shadow">
        <h3 class="text-lg font-medium text-gray-900 mb-2">Average Daily Demand</h3>
        <p class="text-3xl font-bold text-purple-600">{{ summary.avgDailyDemand.toFixed(2) }}</p>
      </div>
    </div>

    <!-- Demand Summary Table -->
    <div class="bg-white rounded-lg shadow overflow-hidden">
      <div class="px-6 py-4 border-b border-gray-200">
        <h3 class="text-lg font-medium text-gray-900">Demand Summary</h3>
      </div>
      
      <div v-if="loading" class="p-6 text-center">
        <div class="spinner-border animate-spin inline-block w-8 h-8 border-4 rounded-full text-blue-600"></div>
        <p class="mt-2 text-gray-600">Loading demand data...</p>
      </div>
      
      <div v-else-if="error" class="p-6 text-center text-red-600">
        <p>{{ error }}</p>
        <button @click="fetchData" class="mt-2 bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700">
          Retry
        </button>
      </div>
      
      <div v-else-if="demandData.length === 0" class="p-6 text-center text-gray-500">
        <p>No demand data available for the selected criteria.</p>
      </div>
      
      <div v-else class="overflow-x-auto">
        <table class="min-w-full divide-y divide-gray-200">
          <thead class="bg-gray-50">
            <tr>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Machine
              </th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Product
              </th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Avg Daily Demand
              </th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Total Records
              </th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Last Updated
              </th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Actions
              </th>
            </tr>
          </thead>
          <tbody class="bg-white divide-y divide-gray-200">
            <tr v-for="item in demandData" :key="`${item.machine_id}-${item.product_id}`" class="hover:bg-gray-50">
              <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                {{ item.machine_name }}
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                {{ item.product_name }}
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                <span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium"
                      :class="getDemandLevelClass(item.average_daily_demand)">
                  {{ item.average_daily_demand.toFixed(2) }} units/day
                </span>
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                {{ item.total_records }}
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                {{ formatDate(item.last_calculated) }}
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                <button @click="viewDetails(item)" class="text-blue-600 hover:text-blue-800">
                  View Details
                </button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- Demand Details Modal -->
    <div v-if="showDetailsModal" class="fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full z-50">
      <div class="relative top-20 mx-auto p-5 border w-11/12 md:w-3/4 lg:w-1/2 shadow-lg rounded-md bg-white">
        <div class="flex justify-between items-center mb-4">
          <h3 class="text-lg font-medium text-gray-900">
            Demand Details: {{ selectedDemandItem?.product_name }} in {{ selectedDemandItem?.machine_name }}
          </h3>
          <button @click="closeDetails" class="text-gray-400 hover:text-gray-600">
            <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
            </svg>
          </button>
        </div>
        
        <div v-if="detailsLoading" class="text-center p-4">
          <div class="spinner-border animate-spin inline-block w-8 h-8 border-4 rounded-full text-blue-600"></div>
          <p class="mt-2 text-gray-600">Loading detailed data...</p>
        </div>
        
        <div v-else-if="demandDetails.length > 0" class="max-h-96 overflow-y-auto">
          <div class="space-y-4">
            <div v-for="detail in demandDetails" :key="detail.id" class="border rounded-lg p-4">
              <div class="flex justify-between items-start mb-2">
                <div>
                  <p class="font-medium text-gray-900">{{ formatDate(detail.current_visit_date) }}</p>
                  <p class="text-sm text-gray-600">{{ detail.days_between_visits }} days since last visit</p>
                </div>
                <div class="text-right">
                  <p class="text-lg font-semibold text-blue-600">{{ detail.daily_demand.toFixed(2) }} units/day</p>
                  <p class="text-sm text-gray-600">{{ detail.total_consumption }} units consumed</p>
                </div>
              </div>
              
              <div class="grid grid-cols-2 gap-4 text-sm">
                <div>
                  <p class="text-gray-600">Stock Before Restock:</p>
                  <p class="font-medium">{{ detail.current_stock_before_restock }} units</p>
                </div>
                <div>
                  <p class="text-gray-600">Stock After Previous Restock:</p>
                  <p class="font-medium">{{ detail.previous_stock_after_restock }} units</p>
                </div>
              </div>
            </div>
          </div>
        </div>
        
        <div v-else class="text-center p-4 text-gray-500">
          <p>No detailed demand data available.</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { api } from '../services/api'

// Reactive data
const loading = ref(false)
const error = ref(null)
const demandData = ref([])
const machines = ref([])
const products = ref([])
const selectedMachine = ref('')
const selectedProduct = ref('')
const selectedDays = ref('30')

// Details modal
const showDetailsModal = ref(false)
const selectedDemandItem = ref(null)
const demandDetails = ref([])
const detailsLoading = ref(false)

// Computed properties
const summary = computed(() => {
  const totalProducts = new Set(demandData.value.map(item => item.product_id)).size
  const totalMachines = new Set(demandData.value.map(item => item.machine_id)).size
  const avgDailyDemand = demandData.value.length > 0 
    ? demandData.value.reduce((sum, item) => sum + item.average_daily_demand, 0) / demandData.value.length
    : 0
  
  return {
    totalProducts,
    totalMachines,
    avgDailyDemand
  }
})

// Methods
const fetchData = async () => {
  loading.value = true
  error.value = null
  
  try {
    const params = {
      days: selectedDays.value
    }
    
    if (selectedMachine.value) {
      params.machine_id = selectedMachine.value
    }
    
    if (selectedProduct.value) {
      params.product_id = selectedProduct.value
    }
    
         const response = await api.getDemandSummary(params)
    demandData.value = response.data
  } catch (err) {
    console.error('Error fetching demand data:', err)
    error.value = 'Failed to load demand data. Please try again.'
  } finally {
    loading.value = false
  }
}

 const fetchMachines = async () => {
   try {
     const response = await api.getMachines()
     machines.value = response.data
   } catch (err) {
     console.error('Error fetching machines:', err)
   }
 }
 
 const fetchProducts = async () => {
   try {
     const response = await api.getProducts()
     products.value = response.data
   } catch (err) {
     console.error('Error fetching products:', err)
   }
 }

const getDemandLevelClass = (demand) => {
  if (demand >= 5) return 'bg-red-100 text-red-800'
  if (demand >= 2) return 'bg-yellow-100 text-yellow-800'
  if (demand >= 1) return 'bg-green-100 text-green-800'
  return 'bg-gray-100 text-gray-800'
}

const formatDate = (dateString) => {
  const date = new Date(dateString)
  return date.toLocaleDateString() + ' ' + date.toLocaleTimeString()
}

const viewDetails = async (item) => {
  selectedDemandItem.value = item
  showDetailsModal.value = true
  detailsLoading.value = true
  
     try {
     const response = await api.getDemandTracking({
       machine_id: item.machine_id,
       product_id: item.product_id
     })
     demandDetails.value = response.data
  } catch (err) {
    console.error('Error fetching demand details:', err)
  } finally {
    detailsLoading.value = false
  }
}

const closeDetails = () => {
  showDetailsModal.value = false
  selectedDemandItem.value = null
  demandDetails.value = []
}

// Lifecycle
onMounted(async () => {
  await Promise.all([fetchMachines(), fetchProducts()])
  await fetchData()
})
</script>

<style scoped>
.form-select {
  @apply border border-gray-300 rounded-md px-3 py-2 bg-white text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500;
}

.spinner-border {
  border-color: transparent;
  border-top-color: currentColor;
  border-right-color: currentColor;
}
</style>