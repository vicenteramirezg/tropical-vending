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
                  {{ isEditing ? 'Edit Supplier' : 'Add New Supplier' }}
                </h3>
                <div class="mt-4 space-y-4">
                  <div>
                    <label for="name" class="block text-sm font-medium text-gray-700">Supplier Name *</label>
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
                    <label for="contact_person" class="block text-sm font-medium text-gray-700">Contact Person</label>
                    <input 
                      type="text" 
                      name="contact_person" 
                      id="contact_person" 
                      v-model="formData.contact_person"
                      class="mt-1 focus:ring-primary-500 focus:border-primary-500 block w-full shadow-sm sm:text-sm border-gray-300 rounded-md"
                    >
                  </div>
                  
                  <div class="grid grid-cols-2 gap-4">
                    <div>
                      <label for="phone" class="block text-sm font-medium text-gray-700">Phone</label>
                      <input 
                        type="tel" 
                        name="phone" 
                        id="phone" 
                        v-model="formData.phone"
                        class="mt-1 focus:ring-primary-500 focus:border-primary-500 block w-full shadow-sm sm:text-sm border-gray-300 rounded-md"
                      >
                    </div>
                    <div>
                      <label for="email" class="block text-sm font-medium text-gray-700">Email</label>
                      <input 
                        type="email" 
                        name="email" 
                        id="email" 
                        v-model="formData.email"
                        class="mt-1 focus:ring-primary-500 focus:border-primary-500 block w-full shadow-sm sm:text-sm border-gray-300 rounded-md"
                      >
                    </div>
                  </div>
                  
                  <div>
                    <label for="address" class="block text-sm font-medium text-gray-700">Address</label>
                    <textarea 
                      id="address" 
                      name="address" 
                      rows="3" 
                      v-model="formData.address"
                      class="shadow-sm focus:ring-primary-500 focus:border-primary-500 mt-1 block w-full sm:text-sm border border-gray-300 rounded-md"
                    ></textarea>
                  </div>
                  
                  <div>
                    <label for="notes" class="block text-sm font-medium text-gray-700">Notes</label>
                    <textarea 
                      id="notes" 
                      name="notes" 
                      rows="3" 
                      v-model="formData.notes"
                      class="shadow-sm focus:ring-primary-500 focus:border-primary-500 mt-1 block w-full sm:text-sm border border-gray-300 rounded-md"
                    ></textarea>
                  </div>
                  
                  <div>
                    <div class="flex items-center">
                      <input 
                        id="is_active" 
                        name="is_active" 
                        type="checkbox" 
                        v-model="formData.is_active"
                        class="h-4 w-4 text-primary-600 focus:ring-primary-500 border-gray-300 rounded"
                      >
                      <label for="is_active" class="ml-2 block text-sm text-gray-900">
                        Active supplier
                      </label>
                    </div>
                    <p class="mt-1 text-sm text-gray-500">
                      Inactive suppliers won't appear in purchase forms
                    </p>
                  </div>
                  
                  <div v-if="isEditing && supplier" class="mt-4 bg-gray-50 p-3 rounded-md">
                    <h4 class="text-sm font-medium text-gray-700 mb-2">Supplier Statistics:</h4>
                    <div class="grid grid-cols-2 gap-2">
                      <div>
                        <span class="text-xs text-gray-500">Total Purchases:</span>
                        <p class="text-sm font-medium text-primary-600">{{ supplier.purchase_count || 0 }}</p>
                      </div>
                      <div>
                        <span class="text-xs text-gray-500">Total Spent:</span>
                        <p class="text-sm font-medium text-primary-600">${{ supplier.total_spent || '0.00' }}</p>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
          <div class="bg-gray-50 px-4 py-3 sm:px-6 sm:flex sm:flex-row-reverse">
            <button 
              type="submit"
              :disabled="loading"
              class="w-full inline-flex justify-center rounded-md border border-transparent shadow-sm px-4 py-2 bg-primary-600 text-base font-medium text-white hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500 sm:ml-3 sm:w-auto sm:text-sm transition-colors duration-150 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              <svg v-if="loading" class="animate-spin -ml-1 mr-2 h-4 w-4 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
              </svg>
              {{ loading ? 'Saving...' : (isEditing ? 'Update' : 'Add') }}
            </button>
            <button 
              type="button"
              @click="$emit('close')"
              :disabled="loading"
              class="mt-3 w-full inline-flex justify-center rounded-md border border-gray-300 shadow-sm px-4 py-2 bg-white text-base font-medium text-gray-700 hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500 sm:mt-0 sm:ml-3 sm:w-auto sm:text-sm transition-colors duration-150 disabled:opacity-50 disabled:cursor-not-allowed"
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
import { ref, computed, watch } from 'vue'

const props = defineProps({
  show: {
    type: Boolean,
    default: false
  },
  supplier: {
    type: Object,
    default: null
  },
  loading: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits(['close', 'save'])

// Form data
const formData = ref({
  id: null,
  name: '',
  contact_person: '',
  phone: '',
  email: '',
  address: '',
  notes: '',
  is_active: true
})

// Computed property to check if we're editing
const isEditing = computed(() => Boolean(props.supplier?.id))

// Watch for supplier changes to populate form
watch(() => props.supplier, (newSupplier) => {
  if (newSupplier) {
    formData.value = {
      id: newSupplier.id,
      name: newSupplier.name,
      contact_person: newSupplier.contact_person || '',
      phone: newSupplier.phone || '',
      email: newSupplier.email || '',
      address: newSupplier.address || '',
      notes: newSupplier.notes || '',
      is_active: newSupplier.is_active !== undefined ? newSupplier.is_active : true
    }
  } else {
    // Reset form for new supplier
    formData.value = {
      id: null,
      name: '',
      contact_person: '',
      phone: '',
      email: '',
      address: '',
      notes: '',
      is_active: true
    }
  }
}, { immediate: true })

// Handle form submission
const handleSubmit = () => {
  emit('save', { ...formData.value })
}
</script> 