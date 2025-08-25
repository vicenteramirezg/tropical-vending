import { ref, computed } from 'vue'
import { api } from '../services/api'
import { getCurrentDateLocal } from '../utils/dateUtils'

export function usePurchases() {
  // State
  const purchases = ref([])
  const products = ref([])
  const suppliers = ref([])
  const loading = ref(true)
  const error = ref(null)
  const selectedProduct = ref(null)

  // Modal states
  const showModal = ref(false)
  const showDeleteModal = ref(false)
  const isEditing = ref(false)
  const purchaseToDelete = ref(null)

  // Form state
  const purchaseForm = ref({
    id: null,
    product: '',
    supplier: '',
    purchase_date: '',
    quantity: 1,
    total_cost: 0,
    notes: ''
  })

  // Computed properties
  const totalCost = computed(() => {
    const quantity = parseFloat(purchaseForm.value.quantity) || 0
    const totalCost = parseFloat(purchaseForm.value.total_cost) || 0
    return totalCost
  })

  const unitCost = computed(() => {
    const quantity = parseFloat(purchaseForm.value.quantity) || 0
    const totalCost = parseFloat(purchaseForm.value.total_cost) || 0
    
    if (quantity > 0) {
      return totalCost / quantity
    }
    return 0
  })

  // Methods
  const fetchPurchases = async () => {
    loading.value = true
    try {
      const response = await api.getPurchases()
      console.log('Purchases data:', response.data)
      // Handle paginated response - extract results array
      const purchasesData = response.data.results || response.data
      purchases.value = purchasesData.map(purchase => {
        const unitCost = purchase.cost_per_unit || 
                        (purchase.unit_cost) || 
                        (purchase.total_cost && purchase.quantity ? purchase.total_cost / purchase.quantity : 0)
        
        const purchaseDate = purchase.purchase_date || purchase.purchased_at
        
        return {
          ...purchase,
          purchase_date: purchaseDate,
          total_cost: purchase.total_cost || (purchase.cost_per_unit * purchase.quantity),
          cost_per_unit: unitCost
        }
      })
    } catch (err) {
      console.error('Error fetching purchases:', err)
      error.value = 'Failed to load purchases. Please try again later.'
    } finally {
      loading.value = false
    }
  }

  const fetchProducts = async () => {
    try {
      // Use the dedicated endpoint to get all products without pagination
      // This ensures the purchase form dropdown shows all available products
      const response = await api.getAllProducts()
      products.value = response.data
    } catch (err) {
      console.error('Error fetching products with getAllProducts, falling back to paginated method:', err)
      try {
        // Fallback: fetch all products by setting a very large page size
        const response = await api.getProducts({ page_size: 1000 })
        products.value = response.data.results || response.data
      } catch (fallbackErr) {
        console.error('Fallback method also failed:', fallbackErr)
        error.value = 'Failed to load products. Please try again later.'
      }
    }
  }

  const fetchSuppliers = async () => {
    try {
      const response = await api.getActiveSuppliers()
      // Handle paginated response - extract results array
      suppliers.value = response.data.results || response.data
    } catch (err) {
      console.error('Error fetching suppliers:', err)
    }
  }

  const onProductChange = () => {
    if (purchaseForm.value.product) {
      selectedProduct.value = products.value.find(p => p.id == purchaseForm.value.product)
      
      if (selectedProduct.value && selectedProduct.value.latest_cost) {
        const latestCost = parseFloat(selectedProduct.value.latest_cost)
        if (latestCost > 0) {
          purchaseForm.value.total_cost = latestCost * purchaseForm.value.quantity
          calculateUnitCost()
        }
      }
    } else {
      selectedProduct.value = null
    }
  }

  const calculateNewInventory = () => {
    if (!selectedProduct.value) return 0
    
    const currentInventory = selectedProduct.value.inventory_quantity || 0
    const purchaseQuantity = parseInt(purchaseForm.value.quantity) || 0
    
    if (isEditing.value) {
      const originalPurchase = purchases.value.find(p => p.id === purchaseForm.value.id)
      const originalQuantity = originalPurchase ? parseInt(originalPurchase.quantity) || 0 : 0
      
      return currentInventory + (purchaseQuantity - originalQuantity)
    }
    
    return currentInventory + purchaseQuantity
  }

  const openAddModal = () => {
    isEditing.value = false
    selectedProduct.value = null
    
    purchaseForm.value = {
      id: null,
      product: '',
      supplier: '',
      purchase_date: getCurrentDateLocal(),
      quantity: 1,
      total_cost: 0,
      notes: ''
    }
    
    showModal.value = true
  }

  const editPurchase = (purchase) => {
    isEditing.value = true
    
    const totalCost = purchase.total_cost || (purchase.cost_per_unit * purchase.quantity)
    
    let dateString = purchase.purchased_at || purchase.purchase_date
    let formattedDate = dateString ? dateString.split('T')[0] : ''
    
    if (!formattedDate) {
      formattedDate = getCurrentDateLocal()
    }
    
    purchaseForm.value = {
      id: purchase.id,
      product: purchase.product,
      supplier: purchase.supplier || '',
      purchase_date: formattedDate,
      quantity: purchase.quantity,
      total_cost: totalCost,
      notes: purchase.notes || ''
    }
    
    if (purchase.product) {
      selectedProduct.value = products.value.find(p => p.id == purchase.product)
    }
    
    calculateUnitCost()
    showModal.value = true
  }

  const savePurchase = async () => {
    try {
      const quantity = parseInt(purchaseForm.value.quantity) || 0
      const totalCost = parseFloat(purchaseForm.value.total_cost) || 0
      
      if (quantity <= 0) {
        error.value = 'Quantity must be greater than zero'
        return
      }
      
      if (totalCost <= 0) {
        error.value = 'Total cost must be greater than zero'
        return
      }
      
      const dateWithTime = `${purchaseForm.value.purchase_date}T12:00:00`
      
      const purchaseData = {
        product: purchaseForm.value.product,
        supplier: purchaseForm.value.supplier || null,
        purchased_at: dateWithTime,
        purchase_date: dateWithTime,
        quantity: quantity,
        total_cost: totalCost,
        notes: purchaseForm.value.notes || '',
        cost_per_unit: Math.round(unitCost.value * 100) / 100
      }
      
      console.log('Saving purchase with data:', purchaseData)
      
      let response
      if (isEditing.value) {
        response = await api.updatePurchase(purchaseForm.value.id, purchaseData)
      } else {
        response = await api.createPurchase(purchaseData)
      }
      
      console.log('Purchase saved successfully:', response.data)
      
      const productResponse = await api.getProduct(purchaseForm.value.product)
      console.log('Updated product:', productResponse.data)
      
      showModal.value = false
      
      await Promise.all([fetchPurchases(), fetchProducts()])
    } catch (err) {
      console.error('Error saving purchase:', err)
      if (err.response && err.response.data) {
        console.error('Server error details:', err.response.data)
        error.value = `Failed to save purchase: ${JSON.stringify(err.response.data)}`
      } else {
        error.value = 'Failed to save purchase. Please try again.'
      }
    }
  }

  const confirmDelete = (purchase) => {
    purchaseToDelete.value = purchase
    showDeleteModal.value = true
  }

  const deletePurchase = async () => {
    if (!purchaseToDelete.value) return
    
    try {
      await api.deletePurchase(purchaseToDelete.value.id)
      showDeleteModal.value = false
      
      await Promise.all([fetchPurchases(), fetchProducts()])
    } catch (err) {
      console.error('Error deleting purchase:', err)
      error.value = 'Failed to delete purchase. Please try again.'
    }
  }

  const calculateUnitCost = () => {
    const quantity = parseFloat(purchaseForm.value.quantity) || 0
    const totalCost = parseFloat(purchaseForm.value.total_cost) || 0
    
    if (quantity > 0) {
      purchaseForm.value.cost_per_unit = Math.round((totalCost / quantity) * 100) / 100
    } else {
      purchaseForm.value.cost_per_unit = 0
    }
  }

  const closeModal = () => {
    showModal.value = false
  }

  const closeDeleteModal = () => {
    showDeleteModal.value = false
  }

  const initialize = async () => {
    await Promise.all([fetchPurchases(), fetchProducts(), fetchSuppliers()])
  }

  return {
    // State
    purchases,
    products,
    suppliers,
    loading,
    error,
    selectedProduct,
    showModal,
    showDeleteModal,
    isEditing,
    purchaseToDelete,
    purchaseForm,
    
    // Computed
    totalCost,
    unitCost,
    
    // Methods
    fetchPurchases,
    fetchProducts,
    fetchSuppliers,
    onProductChange,
    calculateNewInventory,
    openAddModal,
    editPurchase,
    savePurchase,
    confirmDelete,
    deletePurchase,
    calculateUnitCost,
    closeModal,
    closeDeleteModal,
    initialize
  }
} 