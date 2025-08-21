<template>
  <div class="flex flex-col">
    <h4 class="text-sm font-medium text-gray-700 mb-2">Machines at Location</h4>
    <div class="mb-3 p-3 bg-blue-50 border border-blue-200 rounded-lg flex-shrink-0">
      <div class="flex items-center">
        <svg class="h-5 w-5 text-blue-400 mr-2" fill="currentColor" viewBox="0 0 20 20">
          <path fill-rule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clip-rule="evenodd"></path>
        </svg>
        <div class="text-sm text-blue-700 flex-1">
          <p class="font-medium">Partial Restock Allowed</p>
          <p class="text-blue-600">You can restock only the machines/products you need. Leave others empty to skip them.</p>
        </div>
        <div v-if="totalProductCount > 10" class="ml-3 text-xs text-blue-600 hidden sm:flex items-center">
          <svg class="h-4 w-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
          </svg>
          Scroll to see all products
        </div>
      </div>
    </div>
    <div class="flex-1 overflow-y-auto min-h-[200px] max-h-[25vh] sm:max-h-[30vh] lg:max-h-[32vh] border border-gray-200 rounded-lg">
      <div class="space-y-4 p-4">
      <div v-for="machine in machines" :key="machine.id" :class="['border rounded-lg p-3 sm:p-4', getMachineStatusClass(machine)]">
        <div class="flex flex-col sm:flex-row sm:justify-between sm:items-center mb-3 sm:mb-2">
          <h5 class="text-sm font-medium text-gray-900 mb-2 sm:mb-0">
            {{ machine.name }} ({{ machine.machine_type }} {{ machine.model }})
            <span v-if="hasRestockDataForMachine(machine)" class="ml-2 inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-green-100 text-green-800">
              Will be restocked
            </span>
          </h5>
          <div class="text-sm text-gray-500">
            {{ machine.products.length }} products
            <span v-if="hasRestockDataForMachine(machine)" class="ml-2 text-green-600">
              ({{ getRestockProductCount(machine) }} being restocked)
            </span>
          </div>
        </div>
        
        <div class="space-y-3 sm:space-y-2">
          <div v-if="machine.products.length === 0" class="text-sm text-gray-500 italic p-2 text-center">
            No products in this machine
          </div>
          
          <!-- Mobile Layout -->
          <div v-for="product in machine.products" :key="product.id" class="sm:hidden">
            <div :class="['border rounded-lg p-3', getProductStatusClass(product)]">
              <div class="flex items-center justify-between mb-3">
                <div class="flex items-center space-x-2">
                  <div class="text-sm font-medium text-gray-900 bg-gray-100 rounded-md px-2 py-1 min-w-[2rem] text-center">
                    {{ product.slot }}
                  </div>
                  <div class="text-sm font-medium text-gray-900">
                    {{ product.name }}
                    <span v-if="hasRestockDataForProduct(product)" class="ml-1 inline-flex items-center w-2 h-2 bg-green-500 rounded-full" title="Will be restocked"></span>
                  </div>
                </div>
              </div>
              
              <div class="space-y-3">
                <!-- Current Stock -->
                <div>
                  <label class="block text-xs text-gray-500 mb-1">Current Stock</label>
                  <ResponsiveNumberInput
                    v-model="product.stock_before"
                    :min="0"
                    placeholder="0"
                    label="Current Stock"
                    @update:model-value="(value) => updateProductValue(product, 'stock_before', value)"
                  />
                </div>
                
                <!-- Discarded Amount -->
                <div>
                  <label class="block text-xs text-gray-500 mb-1">Discarded Amount</label>
                  <ResponsiveNumberInput
                    v-model="product.discarded"
                    :min="0"
                    placeholder="0"
                    label="Discarded Amount"
                    @update:model-value="(value) => updateProductValue(product, 'discarded', value)"
                  />
                </div>
                
                <!-- Restock Amount -->
                <div>
                  <label class="block text-xs text-gray-500 mb-1">Restock Amount</label>
                  <ResponsiveNumberInput
                    v-model="product.restocked"
                    :min="0"
                    placeholder="0"
                    label="Restock Amount"
                    @update:model-value="(value) => updateProductValue(product, 'restocked', value)"
                  />
                </div>
                
                <!-- New Total -->
                <div class="text-sm text-gray-500 font-medium pt-2 border-t">
                  New Total: {{ calculateNewTotal(product) }}
                </div>
              </div>
            </div>
          </div>
          
          <!-- Desktop/Tablet Layout -->
          <div v-for="product in machine.products" :key="product.id" :class="['hidden sm:grid grid-cols-12 gap-4 items-center', getProductStatusClass(product)]">
            <div class="col-span-1 text-sm font-medium text-gray-900 text-center bg-gray-100 rounded-md py-1">
              {{ product.slot }}
            </div>
            <div class="col-span-3 text-sm font-medium text-gray-900">
              {{ product.name }}
              <span v-if="hasRestockDataForProduct(product)" class="ml-1 inline-flex items-center w-2 h-2 bg-green-500 rounded-full" title="Will be restocked"></span>
            </div>
            
            <!-- Current Stock -->
            <div class="col-span-2">
              <label class="block text-xs text-gray-500">Current Stock</label>
              <ResponsiveNumberInput
                v-model="product.stock_before"
                :min="0"
                placeholder="0"
                label="Current Stock"
                @update:model-value="(value) => updateProductValue(product, 'stock_before', value)"
              />
            </div>
            
            <!-- Discarded Amount -->
            <div class="col-span-2">
              <label class="block text-xs text-gray-500">Discarded Amount</label>
              <ResponsiveNumberInput
                v-model="product.discarded"
                :min="0"
                placeholder="0"
                label="Discarded Amount"
                @update:model-value="(value) => updateProductValue(product, 'discarded', value)"
              />
            </div>
            
            <!-- Restock Amount -->
            <div class="col-span-2">
              <label class="block text-xs text-gray-500">Restock Amount</label>
              <ResponsiveNumberInput
                v-model="product.restocked"
                :min="0"
                placeholder="0"
                label="Restock Amount"
                @update:model-value="(value) => updateProductValue(product, 'restocked', value)"
              />
            </div>
            
            <!-- New Total -->
            <div class="col-span-2 text-sm text-gray-500">
              New Total: {{ calculateNewTotal(product) }}
            </div>
          </div>
        </div>
      </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import ResponsiveNumberInput from '../common/ResponsiveNumberInput.vue'

const props = defineProps({
  machines: Array
})

// Calculate total number of products across all machines
const totalProductCount = computed(() => {
  return props.machines?.reduce((total, machine) => total + (machine.products?.length || 0), 0) || 0
})

// Update product value method for the new component
const updateProductValue = (product, field, value) => {
  product[field] = value
}

// Legacy methods for backward compatibility (now unused but kept for safety)
const incrementValue = (product, field) => {
  const currentValue = product[field] === '' ? 0 : parseInt(product[field]) || 0
  product[field] = currentValue + 1
}

const decrementValue = (product, field) => {
  const currentValue = product[field] === '' ? 0 : parseInt(product[field]) || 0
  product[field] = Math.max(0, currentValue - 1)
}

const calculateNewTotal = (product) => {
  return (parseInt(product.stock_before) || 0) - (parseInt(product.discarded) || 0) + (parseInt(product.restocked) || 0)
}

const hasRestockDataForProduct = (product) => {
  return product.stock_before !== '' || 
         product.restocked !== '' || 
         product.discarded !== ''
}

const hasRestockDataForMachine = (machine) => {
  return machine.products.some(product => hasRestockDataForProduct(product))
}

const getRestockProductCount = (machine) => {
  return machine.products.filter(product => hasRestockDataForProduct(product)).length
}

const getMachineStatusClass = (machine) => {
  return hasRestockDataForMachine(machine) ? 'border-green-300 bg-green-50' : 'border-gray-200'
}

const getProductStatusClass = (product) => {
  return hasRestockDataForProduct(product) ? 'bg-green-50 rounded-md p-2' : 'p-2'
}
</script> 