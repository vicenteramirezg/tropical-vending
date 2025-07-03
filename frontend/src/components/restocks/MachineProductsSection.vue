<template>
  <div>
    <h4 class="text-sm font-medium text-gray-700 mb-2">Machines at Location</h4>
    <div class="space-y-4">
      <div v-for="machine in machines" :key="machine.id" class="border rounded-lg p-4">
        <div class="flex justify-between items-center mb-2">
          <h5 class="text-sm font-medium text-gray-900">
            {{ machine.name }} ({{ machine.machine_type }} {{ machine.model }})
          </h5>
          <div class="text-sm text-gray-500">
            {{ machine.products.length }} products
          </div>
        </div>
        
        <div class="space-y-2">
          <div v-if="machine.products.length === 0" class="text-sm text-gray-500 italic p-2 text-center">
            No products in this machine
          </div>
          <div v-for="product in machine.products" :key="product.id" class="grid grid-cols-12 gap-4 items-center">
            <div class="col-span-1 text-sm font-medium text-gray-900 text-center bg-gray-100 rounded-md py-1">
              {{ product.slot }}
            </div>
            <div class="col-span-3 text-sm font-medium text-gray-900">
              {{ product.name }}
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
                  required
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
                  required
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
                  required
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
  product[field] = (parseInt(product[field]) || 0) + 1
}

const decrementValue = (product, field) => {
  product[field] = Math.max(0, (parseInt(product[field]) || 0) - 1)
}

const calculateNewTotal = (product) => {
  return (parseInt(product.stock_before) || 0) - (parseInt(product.discarded) || 0) + (parseInt(product.restocked) || 0)
}
</script> 