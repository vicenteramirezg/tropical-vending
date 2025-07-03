import { ref, computed } from 'vue'
import { api } from '../services/api'

export function useMachineProducts() {
  const allProducts = ref([])
  const machineProducts = ref([])
  const loading = ref(false)
  const error = ref(null)

  // Form for adding a new product
  const productForm = ref({
    product: '',
    price: '',
    slot: ''
  })

  // Available products (excluding those already in the machine)
  const availableProducts = computed(() => {
    const existingProductIds = machineProducts.value.map(p => p.product)
    return allProducts.value.filter(p => !existingProductIds.includes(p.id))
  })

  // Fetch all products
  const fetchAllProducts = async () => {
    try {
      const response = await api.getProducts()
      allProducts.value = response.data
    } catch (err) {
      console.error('Error fetching products:', err)
      error.value = 'Failed to load products. Please try again.'
    }
  }

  // Fetch machine products
  const fetchMachineProducts = async (machineId) => {
    loading.value = true
    error.value = null
    
    try {
      const params = { machine: machineId }
      const response = await api.getMachineItems(params)
      
      if (response && response.data) {
        const filteredItems = response.data.filter(item => item.machine == machineId)
        
        machineProducts.value = filteredItems.map(item => ({
          ...item,
          editing: false,
          editingSlot: false,
          newPrice: item.price,
          newSlot: item.slot,
          price: typeof item.price === 'string' ? parseFloat(item.price) : item.price
        }))
      }
    } catch (err) {
      console.error('Error fetching machine products:', err)
      error.value = 'Failed to load machine products. Please try again.'
    } finally {
      loading.value = false
    }
  }

  // Add product to machine
  const addProductToMachine = async (machineId) => {
    error.value = null
    
    try {
      const data = {
        machine: machineId,
        product: parseInt(productForm.value.product),
        price: parseFloat(productForm.value.price),
        slot: parseInt(productForm.value.slot)
      }
      
      await api.createMachineItem(data)
      
      // Reset form
      productForm.value = { product: '', price: '', slot: '' }
      
      // Refresh machine products
      await fetchMachineProducts(machineId)
      
      return true
    } catch (err) {
      console.error('Error adding product to machine:', err)
      if (err.response && err.response.data) {
        error.value = `Failed to add product: ${JSON.stringify(err.response.data)}`
      } else {
        error.value = 'Failed to add product to machine. Please try again.'
      }
      return false
    }
  }

  // Update product price
  const updateProductPrice = async (product, machineId) => {
    error.value = null
    
    try {
      await api.updateMachineItem(product.id, {
        machine: machineId,
        product: product.product,
        price: parseFloat(product.newPrice),
        slot: product.slot
      })
      
      product.price = parseFloat(product.newPrice)
      product.editing = false
      
      // Refresh machine products
      await fetchMachineProducts(machineId)
      
      return true
    } catch (err) {
      console.error('Error updating product price:', err)
      error.value = 'Failed to update product price. Please try again.'
      return false
    }
  }

  // Update product slot
  const updateProductSlot = async (product, machineId) => {
    error.value = null
    
    try {
      await api.updateMachineItem(product.id, {
        machine: machineId,
        product: product.product,
        price: product.price,
        slot: parseInt(product.newSlot)
      })
      
      product.slot = parseInt(product.newSlot)
      product.editingSlot = false
      
      // Refresh machine products
      await fetchMachineProducts(machineId)
      
      return true
    } catch (err) {
      console.error('Error updating product slot:', err)
      error.value = 'Failed to update product slot. Please try again.'
      
      // Check for validation/uniqueness errors
      if (err.response && err.response.data) {
        if (err.response.data.non_field_errors) {
          error.value = err.response.data.non_field_errors[0]
        }
      }
      return false
    }
  }

  // Remove product from machine
  const removeProductFromMachine = async (product, machineId) => {
    try {
      await api.deleteMachineItem(product.id)
      
      // Refresh machine products
      await fetchMachineProducts(machineId)
      
      return true
    } catch (err) {
      console.error('Error removing product from machine:', err)
      error.value = 'Failed to remove product from machine. Please try again.'
      return false
    }
  }

  // Edit product price
  const editProductPrice = (product) => {
    product.editing = true
    product.newPrice = product.price
  }

  // Edit product slot
  const editProductSlot = (product) => {
    product.editingSlot = true
    product.newSlot = product.slot
  }

  // Reset state
  const resetState = () => {
    machineProducts.value = []
    productForm.value = { product: '', price: '', slot: '' }
    error.value = null
  }

  // Clear error
  const clearError = () => {
    error.value = null
  }

  return {
    // State
    allProducts,
    machineProducts,
    loading,
    error,
    productForm,
    availableProducts,
    
    // Actions
    fetchAllProducts,
    fetchMachineProducts,
    addProductToMachine,
    updateProductPrice,
    updateProductSlot,
    removeProductFromMachine,
    editProductPrice,
    editProductSlot,
    resetState,
    clearError
  }
} 