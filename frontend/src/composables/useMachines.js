import { ref, computed } from 'vue'
import { api } from '../services/api'

export function useMachines() {
  const machines = ref([])
  const locationMachines = ref([])
  const loading = ref(false)
  const error = ref(null)

  // Machine models list
  const machineModels = ref([
    '3D14',
    'AMS 39640',
    'AMS GB624',
    'AMS-LB9 Combo',
    'AP Snack Shop 111',
    'AP Snack Shop 133',
    'AP Snack Shop 152-D',
    'AP Snack Shop 6600',
    'AP Snack Shop III D20C',
    'AP Studio 3',
    'Crane 147',
    'Crane 148',
    'Crane 157',
    'Crane 158',
    'Crane 168',
    'Crane 172',
    'Crane 180',
    'Crane 181',
    'Crane 452',
    'Crane 784',
    'Dixie Narco',
    'Dixie Narco 276E',
    'Dixie Narco 348C',
    'Dixie Narco 368',
    'Dixie Narco 368 12',
    'Dixie Narco 368 R',
    'Dixie Narco 36812',
    'Dixie Narco 414 CC',
    'Dixie Narco 501-C',
    'Dixie Narco 501E',
    'ISI 3177',
    'Lektro Vending V599C Serie II',
    'Royal Vendor 390-9',
    'Royal Vendor 462-9',
    'Royal Vendor 550-6',
    'Royal Vendor 630-10',
    'Royal Vendor 650-10',
    'Royal Vendor 660',
    'Royal Vendor 660-8',
    'Royal Vendor 660-9',
    'Royal Vendor 804-',
    'Royal Vendor 804-13',
    'Royal Vendor 804-9',
    'Snack Mart 111 3000/Model: 301A',
    'Snack Shop 111',
    'Snack Shop 111 D206',
    'Snack Shop 113',
    'Snack Shop 6000',
    'Snack Shop 6600',
    'Snack Shop III 400 / Model:3014',
    'Snack Shop LCM2',
    'USA 3129',
    'USI 3014A',
    'USI 3166'
  ])

  // Group machines by location
  const groupedMachines = computed(() => {
    const grouped = {}
    
    machines.value.forEach(machine => {
      if (!grouped[machine.location]) {
        grouped[machine.location] = []
      }
      grouped[machine.location].push(machine)
    })
    
    return grouped
  })

  // Fetch machines with optional filters
  const fetchMachines = async (filters = {}) => {
    loading.value = true
    error.value = null
    
    try {
      const params = {}
      if (filters.location) params.location = filters.location
      if (filters.route) params.route = filters.route
      if (filters.machineType) params.machine_type = filters.machineType
      
      const response = await api.getMachines(params)
      // Handle paginated response - extract results array
      machines.value = response.data.results || response.data
    } catch (err) {
      console.error('Error fetching machines:', err)
      error.value = 'Failed to load machines. Please try again.'
    } finally {
      loading.value = false
    }
  }

  // Fetch machines for a specific location with their products
  const fetchLocationMachines = async (locationId) => {
    if (!locationId) {
      locationMachines.value = []
      return
    }
    
    loading.value = true
    error.value = null
    
    try {
      // Fetch machines for this location
      const machinesResponse = await api.getMachines({ location: locationId })
      // Handle paginated response - extract results array
      const machines = machinesResponse.data.results || machinesResponse.data
      
      // For each machine, fetch its products
      const machinesWithProducts = await Promise.all(
        machines.map(async (machine) => {
          try {
            const productsResponse = await api.getMachineItems({ machine: machine.id })
            // Handle paginated response - extract results array
            const productsData = productsResponse.data.results || productsResponse.data
            const products = productsData.map(item => ({
              id: item.product,
              name: item.product_name,
              slot: item.slot,
              current_stock: item.current_stock || 0,
              stock_before: '',
              discarded: '',
              restocked: ''
            }))
            
            return {
              ...machine,
              products
            }
          } catch (err) {
            console.error(`Error fetching products for machine ${machine.id}:`, err)
            return {
              ...machine,
              products: []
            }
          }
        })
      )
      
      locationMachines.value = machinesWithProducts
    } catch (err) {
      console.error('Error fetching location machines:', err)
      error.value = 'Failed to load machines for this location. Please try again.'
      locationMachines.value = []
    } finally {
      loading.value = false
    }
  }

  // Update machine product data with existing restock entries
  const updateMachineProductData = async (visitId, machineId) => {
    try {
      // Find the machine in locationMachines
      const machine = locationMachines.value.find(m => m.id === machineId)
      if (!machine) return
      
      // Get existing restock entries for this visit and machine
      const restocksResponse = await api.getRestocks({ 
        visit: visitId, 
        machine: machineId 
      })
      
      if (restocksResponse.data.length > 0) {
        const visitMachineRestock = restocksResponse.data[0]
        
        // Get restock entries for this visit machine restock
        const entriesResponse = await api.getRestockEntries({ 
          visit_machine_restock: visitMachineRestock.id 
        })
        
        // Update each product with existing data
        machine.products.forEach(product => {
          const existingEntry = entriesResponse.data.find(entry => entry.product === product.id)
          if (existingEntry) {
            product.stock_before = existingEntry.stock_before || ''
            product.discarded = existingEntry.discarded || ''
            product.restocked = existingEntry.restocked || ''
          }
        })
      }
    } catch (err) {
      console.error('Error updating machine product data:', err)
      // Don't throw error here, just log it
    }
  }

  // Reset machine data
  const resetMachineData = () => {
    locationMachines.value = []
  }

  // Create a new machine
  const createMachine = async (machineData) => {
    try {
      await api.createMachine(machineData)
      return true
    } catch (err) {
      console.error('Error creating machine:', err)
      error.value = 'Failed to create machine. Please try again.'
      return false
    }
  }

  // Update an existing machine
  const updateMachine = async (id, machineData) => {
    try {
      await api.updateMachine(id, machineData)
      return true
    } catch (err) {
      console.error('Error updating machine:', err)
      error.value = 'Failed to update machine. Please try again.'
      return false
    }
  }

  // Delete a machine
  const deleteMachine = async (id) => {
    try {
      await api.deleteMachine(id)
      return true
    } catch (err) {
      console.error('Error deleting machine:', err)
      error.value = 'Failed to delete machine. Please try again.'
      return false
    }
  }

  // Clear error
  const clearError = () => {
    error.value = null
  }

  return {
    // State
    machines,
    locationMachines,
    loading,
    error,
    machineModels,
    groupedMachines,
    
    // Actions
    fetchMachines,
    fetchLocationMachines,
    updateMachineProductData,
    resetMachineData,
    createMachine,
    updateMachine,
    deleteMachine,
    clearError
  }
} 