import { ref, computed } from 'vue'
import { api } from '../services/api'

export function useSuppliers() {
  const suppliers = ref([])
  const loading = ref(true)
  const error = ref(null)
  const showModal = ref(false)
  const showDeleteModal = ref(false)
  const isEditing = ref(false)
  const supplierToDelete = ref(null)
  const selectedSupplier = ref(null)

  // Form state
  const supplierForm = ref({
    name: '',
    contact_person: '',
    phone: '',
    email: '',
    address: '',
    notes: '',
    is_active: true
  })

  // Computed properties
  const supplierCount = computed(() => suppliers.value.length)
  const activeSuppliers = computed(() => suppliers.value.filter(s => s.is_active))
  const inactiveSuppliers = computed(() => suppliers.value.filter(s => !s.is_active))

  // Reset form
  const resetForm = () => {
    supplierForm.value = {
      name: '',
      contact_person: '',
      phone: '',
      email: '',
      address: '',
      notes: '',
      is_active: true
    }
  }

  // Fetch all suppliers
  const fetchSuppliers = async (params = {}) => {
    loading.value = true
    error.value = null
    
    try {
      const response = await api.getSuppliers(params)
      suppliers.value = response.data
      console.log('Suppliers loaded:', suppliers.value.length)
    } catch (err) {
      console.error('Error fetching suppliers:', err)
      error.value = 'Failed to load suppliers. Please try again later.'
    } finally {
      loading.value = false
    }
  }

  // Fetch only active suppliers
  const fetchActiveSuppliers = async () => {
    try {
      const response = await api.getActiveSuppliers()
      return response.data
    } catch (err) {
      console.error('Error fetching active suppliers:', err)
      throw new Error('Failed to load active suppliers. Please try again later.')
    }
  }

  // Create a new supplier
  const createSupplier = async (supplierData) => {
    try {
      console.log('Creating supplier:', supplierData)
      const response = await api.createSupplier(supplierData)
      console.log('Supplier created successfully:', response.data)
      
      // Refresh the suppliers list
      await fetchSuppliers()
      return response.data
    } catch (err) {
      console.error('Error creating supplier:', err)
      const errorMessage = err.response?.data?.name?.[0] || 
                          err.response?.data?.detail || 
                          'Failed to create supplier. Please try again.'
      throw new Error(errorMessage)
    }
  }

  // Update an existing supplier
  const updateSupplier = async (supplierId, supplierData) => {
    try {
      console.log('Updating supplier:', supplierId, supplierData)
      const response = await api.updateSupplier(supplierId, supplierData)
      console.log('Supplier updated successfully:', response.data)
      
      // Refresh the suppliers list
      await fetchSuppliers()
      return response.data
    } catch (err) {
      console.error('Error updating supplier:', err)
      const errorMessage = err.response?.data?.name?.[0] || 
                          err.response?.data?.detail || 
                          'Failed to update supplier. Please try again.'
      throw new Error(errorMessage)
    }
  }

  // Delete a supplier
  const deleteSupplier = async (supplierId) => {
    try {
      await api.deleteSupplier(supplierId)
      console.log('Supplier deleted successfully')
      
      // Refresh the suppliers list
      await fetchSuppliers()
    } catch (err) {
      console.error('Error deleting supplier:', err)
      const errorMessage = err.response?.data?.error || 
                          'Failed to delete supplier. Please try again.'
      throw new Error(errorMessage)
    }
  }

  // Toggle supplier active status
  const toggleSupplierActive = async (supplierId) => {
    try {
      const response = await api.toggleSupplierActive(supplierId)
      console.log('Supplier status toggled:', response.data)
      
      // Refresh the suppliers list
      await fetchSuppliers()
      return response.data
    } catch (err) {
      console.error('Error toggling supplier status:', err)
      const errorMessage = 'Failed to toggle supplier status. Please try again.'
      throw new Error(errorMessage)
    }
  }

  // Modal management
  const openAddModal = () => {
    resetForm()
    isEditing.value = false
    selectedSupplier.value = null
    showModal.value = true
  }

  const editSupplier = (supplier) => {
    supplierForm.value = { ...supplier }
    isEditing.value = true
    selectedSupplier.value = supplier
    showModal.value = true
  }

  const closeModal = () => {
    showModal.value = false
    resetForm()
    isEditing.value = false
    selectedSupplier.value = null
  }

  const confirmDelete = (supplier) => {
    supplierToDelete.value = supplier
    showDeleteModal.value = true
  }

  const closeDeleteModal = () => {
    showDeleteModal.value = false
    supplierToDelete.value = null
  }

  // Save supplier (create or update)
  const saveSupplier = async () => {
    try {
      if (isEditing.value) {
        await updateSupplier(selectedSupplier.value.id, supplierForm.value)
      } else {
        await createSupplier(supplierForm.value)
      }
      closeModal()
    } catch (err) {
      throw err // Re-throw to let the component handle the error display
    }
  }

  // Delete supplier with confirmation
  const handleDeleteSupplier = async () => {
    try {
      await deleteSupplier(supplierToDelete.value.id)
      closeDeleteModal()
    } catch (err) {
      throw err // Re-throw to let the component handle the error display
    }
  }

  // Find a supplier by ID
  const findSupplierById = (supplierId) => {
    return suppliers.value.find(supplier => supplier.id === supplierId)
  }

  // Initialize data
  const initialize = async () => {
    await fetchSuppliers()
  }

  return {
    // State
    suppliers,
    loading,
    error,
    showModal,
    showDeleteModal,
    isEditing,
    supplierToDelete,
    selectedSupplier,
    supplierForm,
    
    // Computed
    supplierCount,
    activeSuppliers,
    inactiveSuppliers,
    
    // Methods
    fetchSuppliers,
    fetchActiveSuppliers,
    createSupplier,
    updateSupplier,
    deleteSupplier,
    toggleSupplierActive,
    openAddModal,
    editSupplier,
    closeModal,
    confirmDelete,
    closeDeleteModal,
    saveSupplier,
    handleDeleteSupplier,
    findSupplierById,
    resetForm,
    initialize
  }
} 