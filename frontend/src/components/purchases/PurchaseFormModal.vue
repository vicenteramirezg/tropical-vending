<template>
  <div v-if="show" class="fixed inset-0 overflow-y-auto" aria-labelledby="modal-title" role="dialog" aria-modal="true">
    <div class="flex items-end justify-center min-h-screen pt-4 px-4 pb-20 text-center sm:block sm:p-0">
      <div class="fixed inset-0 bg-gray-500 bg-opacity-75 transition-opacity" aria-hidden="true" @click="$emit('close')"></div>
      
      <span class="hidden sm:inline-block sm:align-middle sm:h-screen" aria-hidden="true">&#8203;</span>
      
      <div class="inline-block align-bottom bg-white rounded-lg text-left overflow-hidden shadow-xl transform transition-all sm:my-8 sm:align-middle sm:max-w-lg sm:w-full">
        <form @submit.prevent="$emit('save')">
          <div class="bg-white px-4 pt-5 pb-4 sm:p-6 sm:pb-4">
            <div class="sm:flex sm:items-start">
              <div class="mt-3 text-center sm:mt-0 sm:text-left w-full">
                <h3 class="text-lg leading-6 font-medium text-gray-900" id="modal-title">
                  {{ isEditing ? 'Edit Purchase' : 'Add New Purchase' }}
                </h3>
                <div class="mt-4 space-y-4">
                  <div>
                    <label for="product" class="block text-sm font-medium text-gray-700">Product</label>
                    <select
                      id="product"
                      name="product"
                      :value="form.product"
                      @input="$emit('update:form', { ...form, product: $event.target.value })"
                      @change="$emit('product-change')"
                      class="mt-1 block w-full pl-3 pr-10 py-2 text-base border-gray-300 focus:outline-none focus:ring-primary-500 focus:border-primary-500 sm:text-sm rounded-md"
                      required
                    >
                      <option value="" disabled>Select a product</option>
                      <option v-for="product in products" :key="product.id" :value="product.id">
                        {{ product.name }} ({{ product.inventory_quantity }} in stock)
                      </option>
                    </select>
                  </div>
                  
                  <div>
                    <label for="supplier" class="block text-sm font-medium text-gray-700">Supplier</label>
                    <select
                      id="supplier"
                      name="supplier"
                      :value="form.supplier"
                      @input="$emit('update:form', { ...form, supplier: $event.target.value })"
                      class="mt-1 block w-full pl-3 pr-10 py-2 text-base border-gray-300 focus:outline-none focus:ring-primary-500 focus:border-primary-500 sm:text-sm rounded-md"
                      required
                    >
                      <option value="" disabled>Select a supplier</option>
                      <option v-for="supplier in suppliers" :key="supplier.id" :value="supplier.id">
                        {{ supplier.name }}
                      </option>
                    </select>
                  </div>
                  
                  <div>
                    <label for="purchase_date" class="block text-sm font-medium text-gray-700">Purchase Date</label>
                    <input 
                      type="date" 
                      name="purchase_date" 
                      id="purchase_date" 
                      :value="form.purchase_date"
                      @input="$emit('update:form', { ...form, purchase_date: $event.target.value })"
                      class="mt-1 focus:ring-primary-500 focus:border-primary-500 block w-full shadow-sm sm:text-sm border-gray-300 rounded-md"
                      required
                    >
                  </div>
                  
                  <div class="grid grid-cols-2 gap-4">
                    <div>
                      <label for="quantity" class="block text-sm font-medium text-gray-700">Quantity</label>
                      <input 
                        type="number" 
                        name="quantity" 
                        id="quantity" 
                        :value="form.quantity"
                        @input="$emit('update:form', { ...form, quantity: $event.target.value })"
                        @change="$emit('calculate-unit-cost')"
                        min="1"
                        class="mt-1 focus:ring-primary-500 focus:border-primary-500 block w-full shadow-sm sm:text-sm border-gray-300 rounded-md"
                        required
                      >
                    </div>
                    
                    <div>
                      <label for="total_cost" class="block text-sm font-medium text-gray-700">Total Cost ($)</label>
                      <input 
                        type="number" 
                        name="total_cost" 
                        id="total_cost" 
                        :value="form.total_cost"
                        @input="$emit('update:form', { ...form, total_cost: $event.target.value })"
                        @change="$emit('calculate-unit-cost')"
                        min="0.01"
                        step="0.01"
                        class="mt-1 focus:ring-primary-500 focus:border-primary-500 block w-full shadow-sm sm:text-sm border-gray-300 rounded-md"
                        required
                      >
                    </div>
                  </div>
                  
                  <div>
                    <label for="notes" class="block text-sm font-medium text-gray-700">Notes</label>
                    <textarea 
                      id="notes" 
                      name="notes" 
                      rows="3" 
                      :value="form.notes"
                      @input="$emit('update:form', { ...form, notes: $event.target.value })"
                      class="shadow-sm focus:ring-primary-500 focus:border-primary-500 mt-1 block w-full sm:text-sm border border-gray-300 rounded-md"
                    ></textarea>
                  </div>
                  
                  <div class="grid grid-cols-2 gap-4">
                    <div class="bg-gray-50 p-3 rounded-md">
                      <div class="text-sm font-medium text-gray-700">Unit Cost:</div>
                      <div class="text-lg font-bold text-primary-600">
                        ${{ unitCost.toFixed(2) }} per unit
                      </div>
                    </div>
                    
                    <div v-if="selectedProduct" class="bg-gray-50 p-3 rounded-md">
                      <div class="text-sm font-medium text-gray-700">Current Inventory:</div>
                      <div class="text-lg font-bold text-primary-600">
                        {{ selectedProduct.inventory_quantity || 0 }} units
                      </div>
                      <div class="text-xs text-gray-500 mt-1">
                        After purchase: {{ calculateNewInventory() }} units
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
import { computed } from 'vue'

const props = defineProps({
  show: {
    type: Boolean,
    default: false
  },
  isEditing: {
    type: Boolean,
    default: false
  },
  form: {
    type: Object,
    required: true
  },
  products: {
    type: Array,
    default: () => []
  },
  suppliers: {
    type: Array,
    default: () => []
  },
  selectedProduct: {
    type: Object,
    default: null
  },
  unitCost: {
    type: Number,
    default: 0
  }
})

const emit = defineEmits(['close', 'save', 'update:form', 'product-change', 'calculate-unit-cost'])

const calculateNewInventory = () => {
  if (!props.selectedProduct) return 0
  
  const currentInventory = props.selectedProduct.inventory_quantity || 0
  const purchaseQuantity = parseInt(props.form.quantity) || 0
  
  return currentInventory + purchaseQuantity
}
</script> 