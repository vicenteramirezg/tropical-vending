import { ref } from 'vue'
import { api } from '../services/api'

export function useMachines() {
  const locationMachines = ref([])
  const loading = ref(false)
  const error = ref(null)

  const fetchLocationMachines = async (locationId) => {
    if (!locationId) {
      locationMachines.value = []
      return
    }
    
    loading.value = true
    error.value = null
    
    try {
      // First fetch machines for the location
      const machinesResponse = await api.getMachines({ location: locationId })
      const machines = machinesResponse.data
      
      // Then fetch the machine items (products) for each machine
      const machinesWithProducts = []
      
      for (const machine of machines) {
        // Get products for this machine
        const itemsResponse = await api.getMachineItems({ machine: machine.id })
        const products = itemsResponse.data
          .map(item => ({
            id: item.product,
            name: item.product_name,
            price: item.price,
            slot: item.slot,
            current_stock: item.current_stock || 0,
            stock_before: item.current_stock || 0,
            discarded: 0,
            restocked: 0
          }))
          .sort((a, b) => a.slot - b.slot) // Sort products by slot number
        
        machinesWithProducts.push({
          ...machine,
          products: products
        })
      }
      
      locationMachines.value = machinesWithProducts
    } catch (err) {
      console.error('Error fetching machines and products:', err)
      error.value = 'Failed to load machine products. Please try again.'
    } finally {
      loading.value = false
    }
  }

  const updateMachineProductData = async (visitId, machineId) => {
    try {
      // Fetch the machine restocks for this visit and machine
      const machineRestocksResponse = await api.getRestocks({ 
        visit: visitId,
        machine: machineId 
      })
      
      if (machineRestocksResponse.data.length > 0) {
        const machineRestock = machineRestocksResponse.data[0]
        const entriesResponse = await api.getRestockEntries({ 
          visit_machine_restock: machineRestock.id 
        })
        const entries = entriesResponse.data
        
        // Find the machine in locationMachines and update its products
        const machineIndex = locationMachines.value.findIndex(m => m.id === machineId)
        
        if (machineIndex !== -1) {
          const machine = locationMachines.value[machineIndex]
          
          entries.forEach(entry => {
            const productIndex = machine.products.findIndex(p => p.id === entry.product)
            
            if (productIndex !== -1) {
              machine.products[productIndex].stock_before = entry.stock_before
              machine.products[productIndex].discarded = entry.discarded || 0
              machine.products[productIndex].restocked = entry.restocked
            }
          })
        }
      }
    } catch (err) {
      console.error('Error updating machine product data:', err)
      throw err
    }
  }

  const resetMachineData = () => {
    locationMachines.value = []
  }

  return {
    locationMachines,
    loading,
    error,
    fetchLocationMachines,
    updateMachineProductData,
    resetMachineData
  }
} 