<template>
  <div>
    <!-- Loading State -->
    <div v-if="loading" class="flex justify-center">
      <div class="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-primary-500"></div>
    </div>
    
    <!-- Error State -->
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
    
    <!-- Empty State -->
    <div v-else-if="restocks.length === 0" class="bg-white shadow overflow-hidden sm:rounded-lg">
      <div class="px-4 py-5 sm:p-6 text-center">
        <h3 class="text-lg leading-6 font-medium text-gray-900">No visits recorded</h3>
        <div class="mt-2 max-w-xl text-sm text-gray-500">
          <p>Get started by recording your first location visit.</p>
        </div>
        <div class="mt-5">
          <button
            @click="$emit('add-restock')"
            class="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-primary-600 hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500"
          >
            Record New Visit
          </button>
        </div>
      </div>
    </div>
    
    <!-- Restock List -->
    <div v-else class="bg-white shadow overflow-hidden sm:rounded-lg">
      <ul role="list" class="divide-y divide-gray-200">
        <li v-for="restock in restocks" :key="restock.id" class="px-4 py-4 sm:px-6">
          <div class="flex items-center justify-between">
            <div class="flex-1 min-w-0">
              <p class="text-sm font-medium text-primary-600 truncate">
                {{ restock.location_name }}
              </p>
              <p class="text-sm text-gray-500">
                {{ formatDate(restock.visit_date) }}
              </p>
            </div>
            <div class="ml-4 flex-shrink-0 flex space-x-2">
              <button
                @click="$emit('view-details', restock)"
                class="inline-flex items-center px-3 py-1 border border-gray-300 shadow-sm text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500"
              >
                View Details
              </button>
              <button
                @click="$emit('edit-restock', restock)"
                class="inline-flex items-center px-3 py-1 border border-transparent text-sm font-medium rounded-md text-white bg-primary-600 hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500"
              >
                Edit
              </button>
              <button
                @click="$emit('delete-restock', restock)"
                class="inline-flex items-center px-3 py-1 border border-transparent text-sm font-medium rounded-md text-white bg-red-600 hover:bg-red-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-red-500"
              >
                Delete
              </button>
            </div>
          </div>
        </li>
      </ul>
    </div>
  </div>
</template>

<script setup>
import { formatDate } from '../../utils/dateUtils'

const props = defineProps({
  restocks: Array,
  loading: Boolean,
  error: String
})

defineEmits(['add-restock', 'view-details', 'edit-restock', 'delete-restock'])
</script> 