import { ref } from 'vue'
import { api } from '../services/api'
import { useAuthStore } from '../store/auth'
import { getCurrentDateTimeLocal } from '../utils/dateUtils'

export function useRestockFormOptimized() {
  const authStore = useAuthStore()
  
  const isEditing = ref(false)
  const selectedLocation = ref('')
  const error = ref(null)
  const saving = ref(false)
  
  const restockForm = ref({
    id: null,
    visit_date: '',
    notes: '',
    location: '',
    machines: []
  })

  const initializeForm = (existingRestock = null) => {
    if (existingRestock) {
      isEditing.value = true
      selectedLocation.value = existingRestock.location_id
      restockForm.value = {
        id: existingRestock.id,
        visit_date: existingRestock.visit_date,
        notes: existingRestock.notes,
        location: existingRestock.location_id
      }
    } else {
      isEditing.value = false
      selectedLocation.value = ''
      restockForm.value = {
        id: null,
        visit_date: getCurrentDateTimeLocal(),
        notes: '',
        location: '',
        machines: []
      }
    }
  }

  const validateForm = (locationMachines) => {
    // Check if at least one machine has restock data
    const hasAnyRestockData = locationMachines.some(machine => 
      machine.products.some(product => 
        hasRestockData(product)
      )
    )
    
    if (!hasAnyRestockData) {
      error.value = 'Please record stock levels for at least one product'
      return false
    }
    
    // Validate that products with partial data have all required fields
    const hasIncompleteData = locationMachines.some(machine => 
      machine.products.some(product => {
        const hasPartialData = hasRestockData(product)
        if (hasPartialData) {
          // If any field has data, stock_before and restocked are required
          return product.stock_before === '' || product.restocked === ''
        }
        return false
      })
    )
    
    if (hasIncompleteData) {
      error.value = 'Please complete all fields for products being restocked (stock before and restock amount are required)'
      return false
    }
    
    return true
  }

  const hasRestockData = (product) => {
    return product.stock_before !== '' || 
           product.restocked !== '' || 
           product.discarded !== ''
  }

  /**
   * Optimized bulk save function that sends all data in a single API call
   * Reduces 90+ API calls to just 1 call for typical visit
   */
  const saveRestockOptimized = async (locationMachines) => {
    try {
      saving.value = true
      error.value = null
      
      if (!validateForm(locationMachines)) {
        return false
      }
      
      // Prepare the bulk payload
      const bulkData = prepareBulkPayload(locationMachines)
      
      console.log('Saving visit with bulk data:', bulkData)
      
      // Make single API call instead of 90+ individual calls
      if (isEditing.value && restockForm.value.id) {
        await api.updateVisitBulk(restockForm.value.id, bulkData)
      } else {
        await api.createVisitBulk(bulkData)
      }
      
      return true
    } catch (err) {
      console.error('Error saving restock visit:', err)
      error.value = err.response?.data?.error || 'Failed to save visit. Please try again.'
      return false
    } finally {
      saving.value = false
    }
  }

  /**
   * Prepare the optimized bulk payload structure
   */
  const prepareBulkPayload = (locationMachines) => {
    const visitData = {
      location: selectedLocation.value,
      visit_date: restockForm.value.visit_date,
      notes: restockForm.value.notes,
      user: authStore.user?.id
    }

    // Filter machines that have restock data and prepare entries
    const machineRestocks = locationMachines
      .filter(machine => machine.products.some(product => hasRestockData(product)))
      .map(machine => {
        // Filter products that have restock data
        const restockEntries = machine.products
          .filter(product => hasRestockData(product))
          .map(product => ({
            product: product.id,
            stock_before: parseInt(product.stock_before) || 0,
            discarded: parseInt(product.discarded) || 0,
            restocked: parseInt(product.restocked) || 0
          }))

        return {
          machine: machine.id,
          notes: '', // Machine-level notes if needed
          restock_entries: restockEntries
        }
      })

    return {
      visit: visitData,
      machine_restocks: machineRestocks
    }
  }

  /**
   * Legacy save function for backward compatibility
   * This maintains the old behavior but is not recommended for performance
   */
  const saveRestock = async (locationMachines, createVisit, updateVisit) => {
    console.warn('Using legacy saveRestock - consider migrating to saveRestockOptimized for better performance')
    
    try {
      error.value = null
      
      if (!validateForm(locationMachines)) {
        return false
      }
      
      // First create/update the Visit
      let visitId
      
      const visitData = {
        location: selectedLocation.value,
        visit_date: restockForm.value.visit_date,
        notes: restockForm.value.notes,
        user: authStore.user?.id
      }
      
      console.log('Saving visit with data:', visitData)
      
      if (isEditing.value && restockForm.value.id) {
        const visitResponse = await updateVisit(restockForm.value.id, visitData)
        visitId = visitResponse.id
      } else {
        const visitResponse = await createVisit(visitData)
        visitId = visitResponse.id
      }
      
      // Process each machine restock
      await processMachineRestocks(visitId, locationMachines)
      
      return true
    } catch (err) {
      console.error('Error saving restock visit:', err)
      error.value = 'Failed to save visit. Please try again.'
      return false
    }
  }

  const processMachineRestocks = async (visitId, locationMachines) => {
    // Only process machines that have restock data
    const machinesWithRestockData = locationMachines.filter(machine => 
      machine.products.some(product => hasRestockData(product))
    )
    
    for (const machine of machinesWithRestockData) {
      let visitMachineRestockId
      
      if (isEditing.value) {
        // When editing, look for an existing restock for this machine
        try {
          const existingRestocksResponse = await api.getRestocks({ 
            visit: visitId,
            machine: machine.id 
          })
          
          if (existingRestocksResponse.data.length > 0) {
            // Update the existing restock
            const existingRestock = existingRestocksResponse.data[0]
            const restockData = {
              visit: visitId,
              machine: machine.id,
              notes: existingRestock.notes || ''
            }
            
            await api.updateRestock(existingRestock.id, restockData)
            visitMachineRestockId = existingRestock.id
          } else {
            // Create a new restock if none exists for this machine
            const restockData = {
              visit: visitId,
              machine: machine.id,
              notes: ''
            }
            
            const machineRestockResponse = await api.createRestock(restockData)
            visitMachineRestockId = machineRestockResponse.data.id
          }
        } catch (err) {
          console.error('Error handling machine restock:', err)
          throw err
        }
      } else {
        // Creating a new visit, so create new restocks
        const restockData = {
          visit: visitId,
          machine: machine.id,
          notes: ''
        }
        
        const machineRestockResponse = await api.createRestock(restockData)
        visitMachineRestockId = machineRestockResponse.data.id
      }
      
      // Process restock entries for each product
      await processRestockEntries(visitMachineRestockId, machine.products)
    }
  }

  const processRestockEntries = async (visitMachineRestockId, products) => {
    // Only process products that have restock data
    const productsWithRestockData = products.filter(product => hasRestockData(product))
    
    for (const product of productsWithRestockData) {
      try {
        const restockEntryData = {
          visit_machine_restock: visitMachineRestockId,
          product: product.id,
          stock_before: parseInt(product.stock_before) || 0,
          discarded: parseInt(product.discarded) || 0,
          restocked: parseInt(product.restocked) || 0
        }
        
        if (isEditing.value) {
          // For editing, check if an entry already exists
          const existingEntriesResponse = await api.getRestockEntries({
            visit_machine_restock: visitMachineRestockId,
            product: product.id
          })
          
          if (existingEntriesResponse.data.length > 0) {
            // Update existing entry
            await api.updateRestockEntry(existingEntriesResponse.data[0].id, restockEntryData)
          } else {
            // Create new entry
            await api.createRestockEntry(restockEntryData)
          }
        } else {
          // For new visits, always create new entries
          await api.createRestockEntry(restockEntryData)
        }
      } catch (err) {
        console.error('Error handling restock entry:', err)
        throw err
      }
    }
  }

  const resetForm = () => {
    initializeForm()
    error.value = null
  }

  return {
    restockForm,
    isEditing,
    selectedLocation,
    error,
    saving,
    initializeForm,
    validateForm,
    saveRestock, // Legacy method
    saveRestockOptimized, // New optimized method
    resetForm
  }
}
