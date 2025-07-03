<template>
  <div v-if="show" class="fixed inset-0 overflow-y-auto" aria-labelledby="modal-title" role="dialog" aria-modal="true">
    <div class="flex items-end justify-center min-h-screen pt-4 px-4 pb-20 text-center sm:block sm:p-0">
      <div class="fixed inset-0 bg-gray-500 bg-opacity-75 transition-opacity" aria-hidden="true" @click="$emit('close')"></div>
      
      <span class="hidden sm:inline-block sm:align-middle sm:h-screen" aria-hidden="true">&#8203;</span>
      
      <div class="inline-block align-bottom bg-white rounded-lg text-left overflow-hidden shadow-xl transform transition-all sm:my-8 sm:align-middle sm:max-w-4xl sm:w-full">
        <form @submit.prevent="$emit('save')">
          <div class="bg-white px-4 pt-5 pb-4 sm:p-6 sm:pb-4">
            <div class="sm:flex sm:items-start">
              <div class="mt-3 text-center sm:mt-0 sm:text-left w-full">
                <h3 class="text-lg leading-6 font-medium text-gray-900" id="modal-title">
                  {{ isEditing ? 'Edit Visit' : 'Record New Visit' }}
                </h3>
                <div class="mt-4 space-y-4">
                  <!-- Route Selection -->
                  <div>
                    <label for="route" class="block text-sm font-medium text-gray-700">Filter by Route (Optional)</label>
                    <select
                      id="route"
                      name="route"
                      :value="selectedRoute"
                      @change="$emit('route-change', $event.target.value)"
                      class="mt-1 block w-full pl-3 pr-10 py-2 text-base border-gray-300 focus:outline-none focus:ring-primary-500 focus:border-primary-500 sm:text-sm rounded-md"
                    >
                      <option value="">All Routes</option>
                      <option value="unassigned">Unassigned</option>
                      <option v-for="route in routes" :key="route" :value="route">
                        {{ route }}
                      </option>
                    </select>
                  </div>
                  
                  <!-- Location Search -->
                  <div>
                    <label for="location-search" class="block text-sm font-medium text-gray-700">Search Location</label>
                    <input
                      id="location-search"
                      name="location-search"
                      type="text"
                      :value="locationSearchText"
                      @input="$emit('location-search', $event.target.value)"
                      placeholder="Type to search locations..."
                      class="mt-1 block w-full pl-3 pr-3 py-2 text-base border-gray-300 focus:outline-none focus:ring-primary-500 focus:border-primary-500 sm:text-sm rounded-md"
                    >
                  </div>
                  
                  <!-- Location Selection -->
                  <div>
                    <label for="location" class="block text-sm font-medium text-gray-700">
                      Location
                      <span class="text-xs text-gray-500 ml-1">({{ locations.length }} locations)</span>
                    </label>
                    <select
                      id="location"
                      name="location"
                      :value="selectedLocation"
                      @change="$emit('location-change', $event.target.value)"
                      class="mt-1 block w-full pl-3 pr-10 py-2 text-base border-gray-300 focus:outline-none focus:ring-primary-500 focus:border-primary-500 sm:text-sm rounded-md"
                      required
                    >
                      <option value="" disabled>Select a location</option>
                      <option v-for="location in locations" :key="location.id" :value="location.id">
                        {{ location.name }}
                        <span v-if="location.route" class="text-gray-500"> - {{ location.route }}</span>
                      </option>
                    </select>
                  </div>
                  
                  <div>
                    <label for="visit_date" class="block text-sm font-medium text-gray-700">Visit Date</label>
                    <input 
                      type="datetime-local" 
                      name="visit_date" 
                      id="visit_date" 
                      v-model="restockForm.visit_date"
                      class="mt-1 focus:ring-primary-500 focus:border-primary-500 block w-full shadow-sm sm:text-sm border-gray-300 rounded-md"
                      required
                    >
                  </div>

                  <!-- Machine Products Section -->
                  <MachineProductsSection
                    v-if="locationMachines.length > 0"
                    :machines="locationMachines"
                  />
                  
                  <div>
                    <label for="notes" class="block text-sm font-medium text-gray-700">Visit Notes</label>
                    <textarea 
                      id="notes" 
                      name="notes" 
                      rows="2" 
                      v-model="restockForm.notes"
                      class="shadow-sm focus:ring-primary-500 focus:border-primary-500 mt-1 block w-full sm:text-sm border border-gray-300 rounded-md"
                    ></textarea>
                  </div>
                </div>
              </div>
            </div>
          </div>
          
          <div class="bg-gray-50 px-4 py-3 sm:px-6 sm:flex sm:flex-row-reverse">
            <button 
              type="submit"
              class="w-full inline-flex justify-center rounded-md border border-transparent shadow-sm px-4 py-2 bg-primary-600 text-base font-medium text-white hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500 sm:ml-3 sm:w-auto sm:text-sm"
            >
              Save Visit
            </button>
            <button 
              type="button"
              @click="$emit('close')"
              class="mt-3 w-full inline-flex justify-center rounded-md border border-gray-300 shadow-sm px-4 py-2 bg-white text-base font-medium text-gray-700 hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500 sm:mt-0 sm:ml-3 sm:w-auto sm:text-sm"
            >
              Cancel
            </button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup>
import MachineProductsSection from './MachineProductsSection.vue'

const props = defineProps({
  show: Boolean,
  isEditing: Boolean,
  restockForm: Object,
  selectedLocation: String,
  selectedRoute: String,
  locationSearchText: String,
  locations: Array,
  routes: Array,
  locationMachines: Array
})

defineEmits(['close', 'save', 'route-change', 'location-search', 'location-change'])
</script> 