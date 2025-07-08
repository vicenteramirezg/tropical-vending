import { ref } from 'vue'
import { api } from '../services/api'

export function useRestocks() {
  const restocks = ref([])
  const loading = ref(false)
  const error = ref(null)

  const fetchRestocks = async () => {
    loading.value = true
    error.value = null
    try {
      const response = await api.getVisits()
      restocks.value = response.data.map(visit => ({
        id: visit.id,
        location_id: visit.location,
        location_name: visit.location_name,
        visit_date: visit.visit_date,
        notes: visit.notes,
        user_name: visit.user_name
      }))
    } catch (err) {
      console.error('Error fetching visits:', err)
      error.value = 'Failed to load visits. Please try again later.'
    } finally {
      loading.value = false
    }
  }

  const createVisit = async (visitData) => {
    try {
      const response = await api.createVisit(visitData)
      return response.data
    } catch (err) {
      console.error('Error creating visit:', err)
      throw err
    }
  }

  const updateVisit = async (id, visitData) => {
    try {
      const response = await api.updateVisit(id, visitData)
      return response.data
    } catch (err) {
      console.error('Error updating visit:', err)
      throw err
    }
  }

  const deleteVisit = async (id) => {
    try {
      await api.deleteVisit(id)
      await fetchRestocks() // Refresh the list
    } catch (err) {
      console.error('Error deleting visit:', err)
      throw err
    }
  }

  const getVisitDetails = async (visitId) => {
    try {
      // Fetch the machine restocks for this visit
      const machineRestocksResponse = await api.getRestocks({ visit: visitId })
      const machineRestocks = machineRestocksResponse.data
      
      // Fetch entries for each machine restock
      let allEntries = []
      
      for (const machineRestock of machineRestocks) {
        const entriesResponse = await api.getRestockEntries({ visit_machine_restock: machineRestock.id })
        const entriesData = entriesResponse.data
        
        // Get machine item info to get the slot number for each product
        const machineItemsResponse = await api.getMachineItems({ machine: machineRestock.machine })
        const machineItems = machineItemsResponse.data
        
        // Add slot info to each entry
        const entriesWithSlot = entriesData.map(entry => {
          const matchingItem = machineItems.find(item => item.product === entry.product)
          return {
            ...entry,
            slot: matchingItem ? matchingItem.slot : null
          }
        })
        
        allEntries.push(...entriesWithSlot)
      }
      
      // Sort entries by slot within each machine
      allEntries.sort((a, b) => {
        if (a.visit_machine_restock !== b.visit_machine_restock) {
          return 0
        }
        return (a.slot || 999) - (b.slot || 999)
      })
      
      return allEntries.map(entry => ({
        id: entry.id,
        product_name: entry.product_name,
        product_id: entry.product,
        previous_quantity: entry.stock_before,
        quantity_discarded: entry.discarded,
        quantity_added: entry.restocked,
        machine_name: entry.machine_name,
        machine_type: entry.machine_type,
        machine_model: entry.machine_model,
        slot: entry.slot
      }))
    } catch (err) {
      console.error('Error fetching visit details:', err)
      throw err
    }
  }

  return {
    restocks,
    loading,
    error,
    fetchRestocks,
    createVisit,
    updateVisit,
    deleteVisit,
    getVisitDetails
  }
} 