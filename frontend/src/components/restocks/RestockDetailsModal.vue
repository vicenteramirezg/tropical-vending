<template>
  <div v-if="show" class="fixed inset-0 overflow-y-auto" aria-labelledby="modal-title" role="dialog" aria-modal="true">
    <div class="flex items-end justify-center min-h-screen pt-4 px-4 pb-20 text-center sm:block sm:p-0">
      <div class="fixed inset-0 bg-gray-500 bg-opacity-75 transition-opacity" aria-hidden="true" @click="$emit('close')"></div>
      
      <span class="hidden sm:inline-block sm:align-middle sm:h-screen" aria-hidden="true">&#8203;</span>
      
      <div class="inline-block align-bottom bg-white rounded-lg text-left overflow-hidden shadow-xl transform transition-all sm:my-8 sm:align-middle sm:max-w-lg sm:w-full">
        <div class="bg-white px-4 pt-5 pb-4 sm:p-6 sm:pb-4">
          <div class="sm:flex sm:items-start">
            <div class="mt-3 text-center sm:mt-0 sm:text-left w-full">
              <h3 class="text-lg leading-6 font-medium text-gray-900" id="modal-title">
                Restock Details
              </h3>
              <div class="mt-4" v-if="restock">
                <dl class="grid grid-cols-1 gap-x-4 gap-y-6 sm:grid-cols-2">
                  <div class="sm:col-span-1">
                    <dt class="text-sm font-medium text-gray-500">Location</dt>
                    <dd class="mt-1 text-sm text-gray-900">{{ restock.location_name }}</dd>
                  </div>
                  <div class="sm:col-span-1">
                    <dt class="text-sm font-medium text-gray-500">Visit Date</dt>
                    <dd class="mt-1 text-sm text-gray-900">{{ formatDate(restock.visit_date) }}</dd>
                  </div>
                  <div class="sm:col-span-1">
                    <dt class="text-sm font-medium text-gray-500">Restocked By</dt>
                    <dd class="mt-1 text-sm text-gray-900">{{ restock.user_name }}</dd>
                  </div>
                  <div class="sm:col-span-2">
                    <dt class="text-sm font-medium text-gray-500">Notes</dt>
                    <dd class="mt-1 text-sm text-gray-900">{{ restock.notes || 'No notes' }}</dd>
                  </div>
                </dl>
                
                <div class="mt-6" v-if="restock.entries && restock.entries.length > 0">
                  <h4 class="text-sm font-medium text-gray-500">Restocked Items</h4>
                  <div class="mt-2 border border-gray-200 rounded-md overflow-hidden">
                    <div class="px-4 py-3 bg-gray-50 text-xs font-medium text-gray-500 uppercase tracking-wider">
                      <div class="grid grid-cols-6 gap-2">
                        <div class="col-span-1 text-center">Slot</div>
                        <div class="col-span-1">Product</div>
                        <div class="col-span-1 text-center">Prev Qty</div>
                        <div class="col-span-1 text-center">Discarded</div>
                        <div class="col-span-1 text-center">Added</div>
                        <div class="col-span-1 text-center">New Qty</div>
                      </div>
                    </div>
                    <div class="divide-y divide-gray-200">
                      <div 
                        v-for="entry in restock.entries" 
                        :key="entry.id" 
                        class="px-4 py-3"
                      >
                        <div class="grid grid-cols-6 gap-2 items-center">
                          <div class="col-span-1 text-center bg-gray-100 rounded-md py-1 text-sm font-medium text-gray-900">
                            {{ entry.slot || '-' }}
                          </div>
                          <div class="col-span-1 text-sm font-medium text-gray-900">
                            {{ entry.product_name }}
                          </div>
                          <div class="col-span-1 text-center text-sm text-gray-500">
                            {{ entry.previous_quantity }}
                          </div>
                          <div class="col-span-1 text-center text-sm text-gray-500">
                            {{ entry.quantity_discarded }}
                          </div>
                          <div class="col-span-1 text-center text-sm text-green-600 font-medium">
                            +{{ entry.quantity_added }}
                          </div>
                          <div class="col-span-1 text-center text-sm font-medium text-gray-900">
                            {{ entry.previous_quantity + entry.quantity_added - entry.quantity_discarded }}
                          </div>
                        </div>
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
            class="w-full inline-flex justify-center rounded-md border border-gray-300 shadow-sm px-4 py-2 bg-white text-base font-medium text-gray-700 hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500 sm:w-auto sm:text-sm"
          >
            Close
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { formatDate } from '../../utils/dateUtils'

const props = defineProps({
  show: Boolean,
  restock: Object
})

defineEmits(['close'])
</script> 