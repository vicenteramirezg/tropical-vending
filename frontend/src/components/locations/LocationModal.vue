<template>
  <div v-if="show" class="fixed inset-0 overflow-y-auto z-50" aria-labelledby="modal-title" role="dialog" aria-modal="true">
    <div class="flex items-end justify-center min-h-screen pt-4 px-4 pb-20 text-center sm:block sm:p-0">
      <div class="fixed inset-0 bg-gray-500 bg-opacity-75 transition-opacity" aria-hidden="true" @click="$emit('close')"></div>
      
      <span class="hidden sm:inline-block sm:align-middle sm:h-screen" aria-hidden="true">&#8203;</span>
      
      <div class="inline-block align-bottom bg-white rounded-xl text-left overflow-hidden shadow-xl transform transition-all sm:my-8 sm:align-middle sm:max-w-lg sm:w-full">
        <form @submit.prevent="handleSubmit">
          <div class="bg-white px-4 pt-5 pb-4 sm:p-6 sm:pb-4">
            <div class="sm:flex sm:items-start">
              <div class="mt-3 text-center sm:mt-0 sm:text-left w-full">
                <h3 class="text-lg leading-6 font-medium text-gray-900" id="modal-title">
                  {{ isEditing ? 'Edit Location' : 'Add New Location' }}
                </h3>
                <div class="mt-4 space-y-4">
                  <div>
                    <label for="name" class="block text-sm font-medium text-gray-700">Name</label>
                    <input 
                      type="text" 
                      name="name" 
                      id="name" 
                      v-model="formData.name"
                      class="mt-1 focus:ring-primary-500 focus:border-primary-500 block w-full shadow-sm sm:text-sm border-gray-300 rounded-md"
                      required
                    >
                  </div>
                  <div>
                    <label for="address" class="block text-sm font-medium text-gray-700">Address</label>
                    <textarea 
                      id="address" 
                      name="address" 
                      rows="3" 
                      v-model="formData.address"
                      class="shadow-sm focus:ring-primary-500 focus:border-primary-500 mt-1 block w-full sm:text-sm border border-gray-300 rounded-md"
                      required
                    ></textarea>
                  </div>
                  <div>
                    <label for="route" class="block text-sm font-medium text-gray-700">Route</label>
                    <input 
                      type="text" 
                      name="route" 
                      id="route" 
                      v-model="formData.route"
                      placeholder="e.g. Route A, Downtown, etc."
                      class="mt-1 focus:ring-primary-500 focus:border-primary-500 block w-full shadow-sm sm:text-sm border-gray-300 rounded-md"
                    >
                    <p class="mt-1 text-xs text-gray-500">Optional: Assign this location to a route for restocking planning</p>
                  </div>
                </div>
              </div>
            </div>
          </div>
          <div class="bg-gray-50 px-4 py-3 sm:px-6 sm:flex sm:flex-row-reverse">
            <button 
              type="submit"
              class="w-full inline-flex justify-center rounded-md border border-transparent shadow-sm px-4 py-2 bg-primary-600 text-base font-medium text-white hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500 sm:ml-3 sm:w-auto sm:text-sm transition-colors duration-150"
            >
              {{ isEditing ? 'Update' : 'Add' }}
            </button>
            <button 
              type="button"
              @click="$emit('close')"
              class="mt-3 w-full inline-flex justify-center rounded-md border border-gray-300 shadow-sm px-4 py-2 bg-white text-base font-medium text-gray-700 hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500 sm:mt-0 sm:ml-3 sm:w-auto sm:text-sm transition-colors duration-150"
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
import { ref, watch } from 'vue'

const props = defineProps({
  show: {
    type: Boolean,
    required: true
  },
  location: {
    type: Object,
    default: null
  }
})

const emit = defineEmits(['close', 'save'])

const formData = ref({
  id: null,
  name: '',
  address: '',
  route: ''
})

const isEditing = ref(false)

// Watch for changes in the location prop to populate the form
watch(() => props.location, (newLocation) => {
  if (newLocation) {
    isEditing.value = true
    formData.value = {
      id: newLocation.id,
      name: newLocation.name,
      address: newLocation.address,
      route: newLocation.route || ''
    }
  } else {
    isEditing.value = false
    formData.value = {
      id: null,
      name: '',
      address: '',
      route: ''
    }
  }
}, { immediate: true })

// Watch for show prop to reset form when modal is closed
watch(() => props.show, (newShow) => {
  if (!newShow && !props.location) {
    // Reset form when modal is closed and no location is being edited
    formData.value = {
      id: null,
      name: '',
      address: '',
      route: ''
    }
  }
})

const handleSubmit = () => {
  emit('save', { ...formData.value })
}
</script> 