<template>
  <div v-if="show" class="fixed inset-0 overflow-y-auto z-50" aria-labelledby="modal-title" role="dialog" aria-modal="true">
    <div class="flex items-end justify-center min-h-screen pt-4 px-4 pb-20 text-center sm:block sm:p-0">
      <div class="fixed inset-0 bg-gray-500 bg-opacity-75 transition-opacity" aria-hidden="true" @click="$emit('close')"></div>
      
      <span class="hidden sm:inline-block sm:align-middle sm:h-screen" aria-hidden="true">&#8203;</span>
      
      <div class="inline-block align-bottom bg-white rounded-xl text-left overflow-hidden shadow-xl transform transition-all sm:my-8 sm:align-middle sm:max-w-3xl sm:w-full">
        <div class="bg-white px-4 pt-5 pb-4 sm:p-6 sm:pb-4">
          <div class="sm:flex sm:items-start">
            <div class="mt-3 text-center sm:mt-0 sm:text-left w-full">
              <h3 class="text-lg leading-6 font-medium text-gray-900" id="modal-title">
                Cost History for {{ product?.name || 'Product' }}
              </h3>
              
              <div class="mt-4">
                <div v-if="loading" class="flex justify-center py-10">
                  <div class="animate-spin rounded-full h-10 w-10 border-t-2 border-b-2 border-primary-500"></div>
                </div>
                
                <div v-else-if="error" class="bg-red-50 border-l-4 border-red-400 p-4 rounded-r-lg shadow-sm">
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
                
                <div v-else-if="costHistory.length === 0" class="py-8 text-center">
                  <svg xmlns="http://www.w3.org/2000/svg" class="h-12 w-12 mx-auto text-gray-400 mb-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                  </svg>
                  <h3 class="text-base font-medium text-gray-900">No cost history found</h3>
                  <p class="mt-1 text-sm text-gray-500">This product has no recorded cost history.</p>
                </div>
                
                <div v-else>
                  <div class="overflow-x-auto">
                    <table class="min-w-full divide-y divide-gray-200">
                      <thead class="bg-gray-50">
                        <tr>
                          <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Date</th>
                          <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Quantity</th>
                          <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Unit Cost</th>
                          <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Total Cost</th>
                          <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Supplier</th>
                          <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Notes</th>
                        </tr>
                      </thead>
                      <tbody class="bg-white divide-y divide-gray-200">
                        <tr v-for="entry in costHistory" :key="entry.id" class="hover:bg-gray-50">
                          <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                            {{ formatDate(entry.date) }}
                          </td>
                          <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                            {{ entry.quantity }}
                          </td>
                          <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                            ${{ Number(entry.unit_cost).toFixed(2) }}
                          </td>
                          <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                            ${{ Number(entry.total_cost).toFixed(2) }}
                          </td>
                          <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                            {{ entry.supplier || 'N/A' }}
                          </td>
                          <td class="px-6 py-4 text-sm text-gray-500">
                            {{ entry.purchase_notes || 'N/A' }}
                          </td>
                        </tr>
                      </tbody>
                    </table>
                  </div>
                  
                  <!-- Summary Stats -->
                  <div v-if="costHistory.length > 0" class="mt-6 bg-gray-50 rounded-lg p-4">
                    <h4 class="text-sm font-medium text-gray-700 mb-3">Summary Statistics</h4>
                    <div class="grid grid-cols-2 md:grid-cols-4 gap-4">
                      <div class="text-center">
                        <p class="text-lg font-semibold text-primary-600">${{ averageUnitCost }}</p>
                        <p class="text-xs text-gray-500">Average Unit Cost</p>
                      </div>
                      <div class="text-center">
                        <p class="text-lg font-semibold text-green-600">${{ lowestUnitCost }}</p>
                        <p class="text-xs text-gray-500">Lowest Unit Cost</p>
                      </div>
                      <div class="text-center">
                        <p class="text-lg font-semibold text-red-600">${{ highestUnitCost }}</p>
                        <p class="text-xs text-gray-500">Highest Unit Cost</p>
                      </div>
                      <div class="text-center">
                        <p class="text-lg font-semibold text-blue-600">{{ totalQuantity }}</p>
                        <p class="text-xs text-gray-500">Total Quantity</p>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
        <div class="bg-gray-50 px-4 py-3 sm:px-6 sm:flex sm:flex-row-reverse">
          <button 
            type="button"
            @click="$emit('close')"
            class="w-full inline-flex justify-center rounded-md border border-gray-300 shadow-sm px-4 py-2 bg-white text-base font-medium text-gray-700 hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500 sm:ml-3 sm:w-auto sm:text-sm transition-colors duration-150"
          >
            Close
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { formatDate } from '../../utils/dateUtils'

const props = defineProps({
  show: {
    type: Boolean,
    default: false
  },
  product: {
    type: Object,
    default: null
  },
  costHistory: {
    type: Array,
    default: () => []
  },
  loading: {
    type: Boolean,
    default: false
  },
  error: {
    type: String,
    default: null
  }
})

const emit = defineEmits(['close'])

// Computed statistics
const averageUnitCost = computed(() => {
  if (props.costHistory.length === 0) return '0.00'
  const total = props.costHistory.reduce((sum, entry) => sum + Number(entry.unit_cost), 0)
  return (total / props.costHistory.length).toFixed(2)
})

const lowestUnitCost = computed(() => {
  if (props.costHistory.length === 0) return '0.00'
  const lowest = Math.min(...props.costHistory.map(entry => Number(entry.unit_cost)))
  return lowest.toFixed(2)
})

const highestUnitCost = computed(() => {
  if (props.costHistory.length === 0) return '0.00'
  const highest = Math.max(...props.costHistory.map(entry => Number(entry.unit_cost)))
  return highest.toFixed(2)
})

const totalQuantity = computed(() => {
  if (props.costHistory.length === 0) return 0
  return props.costHistory.reduce((sum, entry) => sum + Number(entry.quantity), 0)
})
</script> 