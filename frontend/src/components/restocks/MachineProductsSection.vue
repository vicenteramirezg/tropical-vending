<template>
  <div>
    <h4 class="text-sm font-medium text-gray-700 mb-2">Machines at Location</h4>
    <div class="mb-3 p-3 bg-blue-50 border border-blue-200 rounded-lg">
      <div class="flex items-center">
        <svg class="h-5 w-5 text-blue-400 mr-2" fill="currentColor" viewBox="0 0 20 20">
          <path fill-rule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clip-rule="evenodd"></path>
        </svg>
        <div class="text-sm text-blue-700">
          <p class="font-medium">Partial Restock Allowed</p>
          <p class="text-blue-600">You can restock only the machines/products you need. Leave others empty to skip them.</p>
        </div>
      </div>
    </div>
    <div class="space-y-4">
      <div v-for="machine in machines" :key="machine.id" :class="['border rounded-lg p-4', getMachineStatusClass(machine)]">
        <div class="flex justify-between items-center mb-2">
          <h5 class="text-sm font-medium text-gray-900">
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
        
        <div class="space-y-2">
          <div v-if="machine.products.length === 0" class="text-sm text-gray-500 italic p-2 text-center">
            No products in this machine
          </div>
          <div v-for="product in machine.products" :key="product.id" :class="['grid grid-cols-12 gap-4 items-center', getProductStatusClass(product)]">
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
              <div class="mt-1 flex rounded-md shadow-sm">
                <button 
                  type="button"
                  @click="decrementValue(product, 'stock_before')"
                  class="relative inline-flex items-center px-2 py-2 rounded-l-md border border-gray-300 bg-white text-sm font-medium text-gray-500 hover:bg-gray-50"
                >
                  <span class="sr-only">Decrease</span>
                  -
                </button>
                <input 
                  type="number" 
                  v-model="product.stock_before"
                  min="0"
                  class="focus:ring-primary-500 focus:border-primary-500 block w-full border-gray-300 rounded-none text-center sm:text-sm"
                  placeholder="0"
                >
                <button 
                  type="button"
                  @click="incrementValue(product, 'stock_before')"
                  class="relative inline-flex items-center px-2 py-2 rounded-r-md border border-gray-300 bg-white text-sm font-medium text-gray-500 hover:bg-gray-50"
                >
                  <span class="sr-only">Increase</span>
                  +
                </button>
              </div>
            </div>
            
            <!-- Discarded Amount -->
            <div class="col-span-2">
              <label class="block text-xs text-gray-500">Discarded Amount</label>
              <div class="mt-1 flex rounded-md shadow-sm">
                <button 
                  type="button"
                  @click="decrementValue(product, 'discarded')"
                  class="relative inline-flex items-center px-2 py-2 rounded-l-md border border-gray-300 bg-white text-sm font-medium text-gray-500 hover:bg-gray-50"
                >
                  <span class="sr-only">Decrease</span>
                  -
                </button>
                <input 
                  type="number" 
                  v-model="product.discarded"
                  min="0"
                  class="focus:ring-primary-500 focus:border-primary-500 block w-full border-gray-300 rounded-none text-center sm:text-sm"
                  placeholder="0"
                >
                <button 
                  type="button"
                  @click="incrementValue(product, 'discarded')"
                  class="relative inline-flex items-center px-2 py-2 rounded-r-md border border-gray-300 bg-white text-sm font-medium text-gray-500 hover:bg-gray-50"
                >
                  <span class="sr-only">Increase</span>
                  +
                </button>
              </div>
            </div>
            
            <!-- Restock Amount -->
            <div class="col-span-2">
              <label class="block text-xs text-gray-500">Restock Amount</label>
              <div class="mt-1 flex rounded-md shadow-sm">
                <button 
                  type="button"
                  @click="decrementValue(product, 'restocked')"
                  class="relative inline-flex items-center px-2 py-2 rounded-l-md border border-gray-300 bg-white text-sm font-medium text-gray-500 hover:bg-gray-50"
                >
                  <span class="sr-only">Decrease</span>
                  -
                </button>
                <input 
                  type="number" 
                  v-model="product.restocked"
                  min="0"
                  class="focus:ring-primary-500 focus:border-primary-500 block w-full border-gray-300 rounded-none text-center sm:text-sm"
                  placeholder="0"
                >
                <button 
                  type="button"
                  @click="incrementValue(product, 'restocked')"
                  class="relative inline-flex items-center px-2 py-2 rounded-r-md border border-gray-300 bg-white text-sm font-medium text-gray-500 hover:bg-gray-50"
                >
                  <span class="sr-only">Increase</span>
                  +
                </button>
              </div>
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
</template>

<script setup>
const props = defineProps({
  machines: Array
})

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