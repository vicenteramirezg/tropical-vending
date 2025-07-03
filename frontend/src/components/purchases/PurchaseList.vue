<template>
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
  
  <div v-else-if="purchases.length === 0" class="bg-white shadow overflow-hidden sm:rounded-lg">
    <div class="px-4 py-5 sm:p-6 text-center">
      <h3 class="text-lg leading-6 font-medium text-gray-900">No purchases found</h3>
      <div class="mt-2 max-w-xl text-sm text-gray-500">
        <p>Get started by recording your first wholesale purchase.</p>
      </div>
      <div class="mt-5">
        <button
          @click="$emit('add-purchase')"
          class="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-primary-600 hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500"
        >
          Add Purchase
        </button>
      </div>
    </div>
  </div>
  
  <div v-else class="bg-white shadow overflow-hidden sm:rounded-lg">
    <ul role="list" class="divide-y divide-gray-200">
      <li v-for="purchase in purchases" :key="purchase.id" class="px-4 py-4 sm:px-6">
        <div class="flex items-center justify-between">
          <div>
            <div class="flex items-center">
              <p class="text-sm font-medium text-primary-600">
                {{ purchase.product_name }}
              </p>
              <span class="ml-2 px-2 inline-flex text-xs leading-5 font-semibold rounded-full bg-blue-100 text-blue-800">
                {{ purchase.quantity }} units
              </span>
              <span class="ml-2 px-2 inline-flex text-xs leading-5 font-semibold rounded-full bg-green-100 text-green-800">
                {{ purchase.supplier || "Unknown" }}
              </span>
              <span v-if="purchase.current_inventory" class="ml-2 px-2 inline-flex text-xs leading-5 font-semibold rounded-full bg-purple-100 text-purple-800">
                Inventory: {{ purchase.current_inventory }}
              </span>
            </div>
            <div class="mt-1">
              <p class="text-sm text-gray-500">
                Date: {{ formatDate(purchase.purchase_date) }}
              </p>
              <p class="text-sm text-gray-500">
                Total: ${{ parseFloat(purchase.total_cost).toFixed(2) }} | 
                Unit Cost: ${{ parseFloat(purchase.cost_per_unit || (purchase.total_cost / purchase.quantity)).toFixed(2) }}
              </p>
            </div>
          </div>
          <div class="flex space-x-2">
            <button
              @click="$emit('edit-purchase', purchase)"
              class="inline-flex items-center px-2.5 py-1.5 border border-gray-300 shadow-sm text-xs font-medium rounded text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500"
            >
              Edit
            </button>
            <button
              @click="$emit('delete-purchase', purchase)"
              class="inline-flex items-center px-2.5 py-1.5 border border-gray-300 shadow-sm text-xs font-medium rounded text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-red-500"
            >
              Delete
            </button>
          </div>
        </div>
      </li>
    </ul>
  </div>
</template>

<script setup>
import { formatDate } from '../../utils/dateUtils'

const props = defineProps({
  purchases: {
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

const emit = defineEmits(['add-purchase', 'edit-purchase', 'delete-purchase'])
</script> 