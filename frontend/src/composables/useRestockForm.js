import { ref } from 'vue'
import { api } from '../services/api'
import { useAuthStore } from '../store/auth'
import { getCurrentDateTimeLocal } from '../utils/dateUtils'

export function useRestockForm() {
  const authStore = useAuthStore()
  
  const isEditing = ref(false)
  const selectedLocation = ref('')
  const error = ref(null)
  
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
    // Validate that all products have stock levels recorded
    const hasEmptyFields = locationMachines.some(machine => 
      machine.products.some(product => 
        product.stock_before === '' || product.restocked === ''
      )
    )
    
    if (hasEmptyFields) {
      error.value = 'Please record stock levels for all products in all machines'
      return false
    }
    
    return true
  }

  const saveRestock = async (locationMachines, createVisit, updateVisit) => {
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
    for (const machine of locationMachines) {
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
    for (const product of products) {
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
    initializeForm,
    validateForm,
    saveRestock,
    resetForm
  }
} 