<template>
  <div v-if="show" class="fixed inset-0 overflow-y-auto" aria-labelledby="modal-title" role="dialog" aria-modal="true">
    <div class="flex items-end justify-center min-h-screen pt-4 px-4 pb-20 text-center sm:block sm:p-0">
      <div class="fixed inset-0 bg-gray-500 bg-opacity-75 transition-opacity" aria-hidden="true" @click="$emit('close')"></div>
      
      <span class="hidden sm:inline-block sm:align-middle sm:h-screen" aria-hidden="true">&#8203;</span>
      
      <div class="inline-block align-bottom bg-white rounded-lg text-left overflow-hidden shadow-xl transform transition-all sm:my-8 sm:align-middle sm:max-w-3xl sm:w-full">
        <div class="bg-white px-4 pt-5 pb-4 sm:p-6 sm:pb-4">
          <div class="sm:flex sm:items-start">
            <div class="mt-3 text-center sm:mt-0 sm:text-left w-full">
              <h3 class="text-lg leading-6 font-medium text-gray-900" id="modal-title">
                Manage Products for {{ selectedMachine?.name }}
              </h3>
              
              <div class="mt-4">
                <!-- Add New Product Form -->
                <div class="bg-gray-50 rounded-lg p-4 mb-4">
                  <h4 class="text-sm font-medium text-gray-700 mb-2">Add Product to Machine</h4>
                  
                  <!-- Error notification -->
                  <div v-if="error" class="mb-4 bg-red-50 border-l-4 border-red-400 p-4 rounded-r-lg">
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
                  
                  <form @submit.prevent="$emit('add-product')" class="grid grid-cols-1 gap-y-3 sm:grid-cols-12 sm:gap-x-3">
                    <div class="sm:col-span-6">
                      <label for="product" class="block text-xs font-medium text-gray-700">Product</label>
                      <select
                        id="product"
                        v-model="productForm.product"
                        class="mt-1 block w-full pl-3 pr-10 py-2 text-sm border-gray-300 focus:outline-none focus:ring-primary-500 focus:border-primary-500 rounded-md"
                        required
                      >
                        <option value="" disabled>Select a product</option>
                        <option 
                          v-for="product in availableProducts" 
                          :key="product.id" 
                          :value="product.id"
                        >
                          {{ product.name }}
                        </option>
                      </select>
                    </div>
                    <div class="sm:col-span-2">
                      <label for="slot" class="block text-xs font-medium text-gray-700">Slot #</label>
                      <input 
                        type="number" 
                        id="slot" 
                        min="1" 
                        v-model="productForm.slot"
                        placeholder="1"
                        class="mt-1 focus:ring-primary-500 focus:border-primary-500 block w-full py-2 px-3 sm:text-sm border-gray-300 rounded-md"
                        required
                      >
                    </div>
                    <div class="sm:col-span-2">
                      <label for="price" class="block text-xs font-medium text-gray-700">Price</label>
                      <div class="mt-1 relative rounded-md shadow-sm">
                        <div class="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                          <span class="text-gray-500 sm:text-sm">$</span>
                        </div>
                        <input 
                          type="number" 
                          id="price" 
                          step="0.01" 
                          min="0.01" 
                          v-model="productForm.price"
                          placeholder="0.00"
                          class="focus:ring-primary-500 focus:border-primary-500 block w-full pl-7 pr-3 py-2 sm:text-sm border-gray-300 rounded-md"
                          required
                        >
                      </div>
                    </div>
                    <div class="sm:col-span-2 flex items-end">
                      <button
                        type="submit"
                        class="w-full inline-flex justify-center rounded-md border border-transparent shadow-sm px-4 py-2 bg-primary-600 text-sm font-medium text-white hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500"
                      >
                        Add
                      </button>
                    </div>
                  </form>
                </div>
                
                <!-- Products Table -->
                <div v-if="machineProducts.length > 0" class="border border-gray-200 rounded-md overflow-hidden">
                  <div class="overflow-x-auto -mx-4 sm:mx-0">
                    <div class="inline-block min-w-full align-middle">
                      <table class="min-w-full divide-y divide-gray-200">
                        <thead class="bg-gray-50">
                          <tr>
                            <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                              Product
                            </th>
                            <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                              Slot
                            </th>
                            <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                              Price
                            </th>
                            <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                              Current Stock
                            </th>
                            <th scope="col" class="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                              Actions
                            </th>
                          </tr>
                        </thead>
                        <tbody class="bg-white divide-y divide-gray-200">
                          <tr v-for="product in machineProducts" :key="product.id">
                            <td class="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                              {{ product.product_name }}
                            </td>
                            <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                              <div class="flex items-center">
                                <span v-if="product.editingSlot">
                                  <div class="relative rounded-md shadow-sm">
                                    <input 
                                      type="number" 
                                      min="1" 
                                      v-model="product.newSlot"
                                      class="focus:ring-primary-500 focus:border-primary-500 block w-full py-1 px-3 sm:text-sm border-gray-300 rounded-md"
                                    >
                                  </div>
                                </span>
                                <span v-else>{{ product.slot }}</span>
                              </div>
                            </td>
                            <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                              <div class="flex items-center">
                                <span v-if="product.editing">
                                  <div class="relative rounded-md shadow-sm">
                                    <div class="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                                      <span class="text-gray-500 sm:text-sm">$</span>
                                    </div>
                                    <input 
                                      type="number" 
                                      step="0.01" 
                                      min="0.01" 
                                      v-model="product.newPrice"
                                      class="focus:ring-primary-500 focus:border-primary-500 block w-full pl-7 pr-3 py-1 sm:text-sm border-gray-300 rounded-md"
                                    >
                                  </div>
                                </span>
                                <span v-else>${{ typeof product.price === 'number' ? product.price.toFixed(2) : Number(product.price).toFixed(2) }}</span>
                              </div>
                            </td>
                            <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                              {{ product.current_stock || 'Not set' }}
                            </td>
                            <td class="px-6 py-4 whitespace-nowrap text-right text-sm font-medium space-x-2">
                              <button 
                                v-if="product.editingSlot"
                                @click="$emit('update-slot', product)"
                                class="text-primary-600 hover:text-primary-900"
                              >
                                Save Slot
                              </button>
                              <button 
                                v-else
                                @click="$emit('edit-slot', product)"
                                class="text-primary-600 hover:text-primary-900"
                              >
                                Edit Slot
                              </button>
                              <button 
                                v-if="product.editing"
                                @click="$emit('update-price', product)"
                                class="text-primary-600 hover:text-primary-900"
                              >
                                Save Price
                              </button>
                              <button 
                                v-else
                                @click="$emit('edit-price', product)"
                                class="text-primary-600 hover:text-primary-900"
                              >
                                Edit Price
                              </button>
                              <button 
                                @click="$emit('remove-product', product)"
                                class="text-red-600 hover:text-red-900"
                              >
                                Remove
                              </button>
                            </td>
                          </tr>
                        </tbody>
                      </table>
                    </div>
                  </div>
                </div>
                
                <div v-else class="text-center p-6 bg-gray-50 rounded-md">
                  <p class="text-sm text-gray-500">No products added to this machine yet.</p>
                </div>
              </div>
            </div>
          </div>
        </div>
        <div class="bg-gray-50 px-4 py-3 sm:px-6 sm:flex sm:flex-row-reverse">
          <button 
            type="button"
            @click="$emit('close')"
            class="w-full inline-flex justify-center rounded-md border border-gray-300 shadow-sm px-4 py-2 bg-white text-base font-medium text-gray-700 hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500 sm:ml-3 sm:w-auto sm:text-sm"
          >
            Close
          </button>
        </div>
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
  selectedMachine: {
    type: Object,
    default: null
  },
  machineProducts: {
    type: Array,
    required: true
  },
  availableProducts: {
    type: Array,
    required: true
  },
  productForm: {
    type: Object,
    required: true
  },
  error: {
    type: String,
    default: null
  }
})

defineEmits([
  'close',
  'add-product',
  'edit-price',
  'update-price',
  'edit-slot',
  'update-slot',
  'remove-product'
])
</script> 