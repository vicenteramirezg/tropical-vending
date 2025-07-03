<template>
  <div v-if="show" class="fixed inset-0 overflow-y-auto" aria-labelledby="modal-title" role="dialog" aria-modal="true">
    <div class="flex items-end justify-center min-h-screen pt-4 px-4 pb-20 text-center sm:block sm:p-0">
      <div class="fixed inset-0 bg-gray-500 bg-opacity-75 transition-opacity" aria-hidden="true" @click="$emit('close')"></div>
      
      <span class="hidden sm:inline-block sm:align-middle sm:h-screen" aria-hidden="true">&#8203;</span>
      
      <div class="inline-block align-bottom bg-white rounded-lg text-left overflow-hidden shadow-xl transform transition-all sm:my-8 sm:align-middle sm:max-w-lg sm:w-full">
        <form @submit.prevent="$emit('save', machineForm)">
          <div class="bg-white px-4 pt-5 pb-4 sm:p-6 sm:pb-4">
            <div class="sm:flex sm:items-start">
              <div class="mt-3 text-center sm:mt-0 sm:text-left w-full">
                <h3 class="text-lg leading-6 font-medium text-gray-900" id="modal-title">
                  {{ isEditing ? 'Edit Machine' : 'Add New Machine' }}
                </h3>
                <div class="mt-4 space-y-4">
                  <div>
                    <label for="name" class="block text-sm font-medium text-gray-700">Machine Name</label>
                    <input 
                      type="text" 
                      name="name" 
                      id="name" 
                      v-model="machineForm.name"
                      placeholder="e.g. Building A Snack Machine"
                      class="mt-1 focus:ring-primary-500 focus:border-primary-500 block w-full shadow-sm sm:text-sm border-gray-300 rounded-md"
                      required
                    >
                  </div>
                  <div>
                    <label for="location" class="block text-sm font-medium text-gray-700">Location</label>
                    <select
                      id="location"
                      name="location"
                      v-model="machineForm.location"
                      class="mt-1 block w-full pl-3 pr-10 py-2 text-base border-gray-300 focus:outline-none focus:ring-primary-500 focus:border-primary-500 sm:text-sm rounded-md"
                      required
                    >
                      <option value="" disabled>Select a location</option>
                      <option v-for="location in locations" :key="location.id" :value="location.id">
                        {{ location.name }}
                      </option>
                    </select>
                  </div>
                  <div>
                    <label for="machine_type" class="block text-sm font-medium text-gray-700">Machine Type</label>
                    <select
                      id="machine_type"
                      name="machine_type"
                      v-model="machineForm.machine_type"
                      class="mt-1 block w-full pl-3 pr-10 py-2 text-base border-gray-300 focus:outline-none focus:ring-primary-500 focus:border-primary-500 sm:text-sm rounded-md"
                      required
                    >
                      <option value="" disabled>Select a machine type</option>
                      <option value="Snack">Snack</option>
                      <option value="Soda">Soda</option>
                      <option value="Combo">Combo</option>
                    </select>
                  </div>
                  <div>
                    <label for="model" class="block text-sm font-medium text-gray-700">Model (Optional)</label>
                    <select
                      id="model"
                      name="model"
                      v-model="machineForm.model"
                      class="mt-1 block w-full pl-3 pr-10 py-2 text-base border-gray-300 focus:outline-none focus:ring-primary-500 focus:border-primary-500 sm:text-sm rounded-md"
                    >
                      <option value="">Select a model (optional)</option>
                      <option v-for="model in machineModels" :key="model" :value="model">
                        {{ model }}
                      </option>
                    </select>
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
              {{ isEditing ? 'Update' : 'Add' }}
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
defineProps({
  show: {
    type: Boolean,
    required: true
  },
  isEditing: {
    type: Boolean,
    required: true
  },
  machineForm: {
    type: Object,
    required: true
  },
  locations: {
    type: Array,
    required: true
  },
  machineModels: {
    type: Array,
    required: true
  }
})

defineEmits(['close', 'save'])
</script> 