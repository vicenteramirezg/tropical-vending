<template>
  <div v-if="show" class="fixed inset-0 overflow-y-auto z-50" aria-labelledby="modal-title" role="dialog" aria-modal="true">
    <!-- Mobile/Tablet: Full screen layout (up to md breakpoint) -->
    <div class="md:hidden min-h-screen bg-white">
      <form @submit.prevent="$emit('save')" novalidate class="h-full flex flex-col">
        <!-- Mobile Header -->
        <div class="flex items-center justify-between p-4 border-b border-gray-200 bg-white sticky top-0 z-10">
          <h3 class="text-lg font-medium text-gray-900" id="modal-title">
            {{ isEditing ? 'Edit Visit' : 'Record New Visit' }}
          </h3>
          <button 
            type="button"
            @click="$emit('close')"
            class="text-gray-400 hover:text-gray-500 focus:outline-none focus:text-gray-500 transition ease-in-out duration-150"
          >
            <svg class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>
        
        <!-- Mobile Content - Ensure it's scrollable and doesn't overflow -->
        <div class="flex-1 overflow-y-auto p-4 pb-20">
          <div class="space-y-6">
            <!-- Route Selection -->
            <div>
              <label for="route-mobile" class="block text-sm font-medium text-gray-700 mb-2">Filter by Route (Optional)</label>
              <select
                id="route-mobile"
                name="route"
                :value="selectedRoute"
                @change="$emit('route-change', $event.target.value)"
                class="block w-full pl-3 pr-10 py-3 text-base border-gray-300 focus:outline-none focus:ring-primary-500 focus:border-primary-500 rounded-md"
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
              <label for="location-search-mobile" class="block text-sm font-medium text-gray-700 mb-2">Search Location</label>
              <input
                id="location-search-mobile"
                name="location-search"
                type="text"
                :value="locationSearchText"
                @input="$emit('location-search', $event.target.value)"
                placeholder="Type to search locations..."
                class="block w-full pl-3 pr-3 py-3 text-base border-gray-300 focus:outline-none focus:ring-primary-500 focus:border-primary-500 rounded-md"
              >
            </div>
            
            <!-- Location Selection -->
            <div>
              <label for="location-mobile" class="block text-sm font-medium text-gray-700 mb-2">
                Location
                <span class="text-xs text-gray-500 ml-1">({{ locations.length }} locations)</span>
              </label>
              <select
                id="location-mobile"
                name="location"
                :value="selectedLocation"
                @change="$emit('location-change', $event.target.value)"
                class="block w-full pl-3 pr-10 py-3 text-base border-gray-300 focus:outline-none focus:ring-primary-500 focus:border-primary-500 rounded-md"
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
              <label for="visit_date_mobile" class="block text-sm font-medium text-gray-700 mb-2">Visit Date</label>
              <input 
                type="datetime-local" 
                name="visit_date" 
                id="visit_date_mobile" 
                v-model="restockForm.visit_date"
                class="focus:ring-primary-500 focus:border-primary-500 block w-full shadow-sm text-base border-gray-300 rounded-md text-gray-900 py-3"
                required
              >
            </div>

            <!-- Machine Products Section - Ensure it doesn't take up too much space -->
            <div v-if="locationMachines.length > 0" class="space-y-4">
              <MachineProductsSection
                :machines="locationMachines"
              />
            </div>
            
            <div>
              <label for="notes-mobile" class="block text-sm font-medium text-gray-700 mb-2">Visit Notes</label>
              <textarea 
                id="notes-mobile" 
                name="notes" 
                rows="3" 
                v-model="restockForm.notes"
                class="shadow-sm focus:ring-primary-500 focus:border-primary-500 block w-full text-base border border-gray-300 rounded-md py-3"
                placeholder="Add any notes about this visit..."
              ></textarea>
            </div>
            
            <!-- Add bottom padding to ensure content doesn't get hidden behind footer -->
            <div class="h-20"></div>
          </div>
        </div>
        
        <!-- Mobile Footer - Fixed at bottom with proper z-index -->
        <div class="border-t border-gray-200 bg-white p-4 space-y-3 fixed bottom-0 left-0 right-0 z-20">
          <button 
            type="submit"
            :disabled="saving"
            class="w-full inline-flex justify-center items-center rounded-md border border-transparent shadow-sm px-4 py-3 bg-primary-600 text-base font-medium text-white hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500 disabled:opacity-50 disabled:cursor-not-allowed min-h-[48px]"
          >
            <span v-if="saving" class="inline-flex items-center">
              <svg class="animate-spin -ml-1 mr-2 h-4 w-4 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
              </svg>
              Saving...
            </span>
            <span v-else>Save Visit</span>
          </button>
          <button 
            type="button"
            @click="$emit('close')"
            class="w-full inline-flex justify-center rounded-md border border-gray-300 shadow-sm px-4 py-3 bg-white text-base font-medium text-gray-700 hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500 min-h-[48px]"
          >
            Cancel
          </button>
        </div>
      </form>
    </div>

    <!-- Desktop: Modal overlay layout (md breakpoint and above) -->
    <div class="hidden md:block modal-overlay">
      <div class="flex items-center justify-center min-h-full pt-4 px-4 pb-20 text-center">
        <div class="fixed inset-0 bg-gray-500 bg-opacity-75 transition-opacity" aria-hidden="true" @click="$emit('close')"></div>
        
        <div class="modal-content inline-block align-bottom bg-white rounded-lg text-left shadow-xl transform transition-all my-8 align-middle max-w-5xl w-full">
          <form @submit.prevent="$emit('save')" novalidate class="flex flex-col h-full">
            <!-- Modal Header (Fixed) -->
            <div class="bg-white px-4 pt-5 pb-4 sm:px-6 border-b border-gray-200 flex-shrink-0">
              <div class="flex items-center justify-between">
                <h3 class="text-lg leading-6 font-medium text-gray-900" id="modal-title">
                  {{ isEditing ? 'Edit Visit' : 'Record New Visit' }}
                </h3>
                <button 
                  type="button"
                  @click="$emit('close')"
                  class="text-gray-400 hover:text-gray-500 focus:outline-none focus:text-gray-500 transition ease-in-out duration-150"
                >
                  <svg class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
                  </svg>
                </button>
              </div>
            </div>

            <!-- Modal Content (Scrollable) -->
            <div class="modal-scrollable bg-white px-4 py-4 sm:px-6">
              <div class="space-y-6">
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
                    class="mt-1 focus:ring-primary-500 focus:border-primary-500 block w-full shadow-sm sm:text-sm border-gray-300 rounded-md text-gray-900"
                    required
                  >
                </div>

                <!-- Machine Products Section -->
                <div v-if="locationMachines.length > 0">
                  <MachineProductsSection :machines="locationMachines" />
                </div>
                
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
            
            <!-- Modal Footer (Fixed) -->
            <div class="bg-gray-50 px-4 py-3 sm:px-6 sm:flex sm:flex-row-reverse border-t flex-shrink-0">
              <button 
                type="submit"
                :disabled="saving"
                class="w-full inline-flex justify-center rounded-md border border-transparent shadow-sm px-4 py-2 bg-primary-600 text-base font-medium text-white hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500 sm:ml-3 sm:w-auto sm:text-sm disabled:opacity-50 disabled:cursor-not-allowed"
              >
                <span v-if="saving" class="inline-flex items-center">
                  <svg class="animate-spin -ml-1 mr-2 h-4 w-4 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                    <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                    <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                  </svg>
                  Saving...
                </span>
                <span v-else>Save Visit</span>
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
  </div>
</template>

<script setup>
import { watch, onMounted, onUnmounted } from 'vue'
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
  locationMachines: Array,
  saving: Boolean
})

defineEmits(['close', 'save', 'route-change', 'location-search', 'location-change'])

// Prevent background scrolling when modal is open
const preventBodyScroll = () => {
  // Store original overflow style
  const originalOverflow = document.body.style.overflow
  
  // Prevent body scroll
  document.body.style.overflow = 'hidden'
  
  // Return cleanup function
  return () => {
    document.body.style.overflow = originalOverflow
  }
}

// Watch for modal show/hide to manage body scroll
let cleanupBodyScroll = null

watch(() => props.show, (newShow) => {
  if (newShow) {
    // Modal is opening - prevent background scroll
    cleanupBodyScroll = preventBodyScroll()
  } else {
    // Modal is closing - restore background scroll
    if (cleanupBodyScroll) {
      cleanupBodyScroll()
      cleanupBodyScroll = null
    }
  }
}, { immediate: true })

// Cleanup on component unmount
onUnmounted(() => {
  if (cleanupBodyScroll) {
    cleanupBodyScroll()
  }
})
</script> 