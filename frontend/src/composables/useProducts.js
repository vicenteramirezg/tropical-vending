import { ref, computed } from 'vue'
import { api } from '../services/api'

export function useProducts() {
  const products = ref([])
  const loading = ref(true)
  const error = ref(null)

  // Computed properties
  const productCount = computed(() => products.value.length)

  // Fetch all products
  const fetchProducts = async () => {
    loading.value = true
    error.value = null
    
    try {
      const response = await api.getProducts()
      // Handle paginated response - extract results array
      products.value = response.data.results || response.data
      
      // Log product data for debugging
      console.log('Products loaded:', products.value.length)
      products.value.forEach(product => {
        if (!product.image_url) {
          console.warn('Product missing image URL:', product.name)
        }
      })
    } catch (err) {
      console.error('Error fetching products:', err)
      error.value = 'Failed to load products. Please try again later.'
    } finally {
      loading.value = false
    }
  }

  // Create a new product
  const createProduct = async (productData) => {
    try {
      console.log('Sending product data:', JSON.stringify(productData))
      const response = await api.createProduct(productData)
      console.log('Product created successfully:', response.data)
      
      // Refresh the products list
      await fetchProducts()
      return response.data
    } catch (err) {
      console.error('Error creating product:', err)
      console.error('Error details:', err.response?.data || err.message)
      const errorMessage = err.response?.data?.detail || 'Failed to create product. Please try again.'
      throw new Error(errorMessage)
    }
  }

  // Update an existing product
  const updateProduct = async (productId, productData) => {
    try {
      console.log('Product form data before updating:', JSON.stringify(productData))
      const response = await api.updateProduct(productId, productData)
      console.log('Product updated successfully:', response.data)
      
      // Refresh the products list
      await fetchProducts()
      return response.data
    } catch (err) {
      console.error('Error updating product:', err)
      console.error('Error details:', err.response?.data || err.message)
      const errorMessage = err.response?.data?.detail || 'Failed to update product. Please try again.'
      throw new Error(errorMessage)
    }
  }

  // Delete a product
  const deleteProduct = async (productId) => {
    try {
      await api.deleteProduct(productId)
      
      // Refresh the products list
      await fetchProducts()
    } catch (err) {
      console.error('Error deleting product:', err)
      const errorMessage = 'Failed to delete product. Please try again.'
      throw new Error(errorMessage)
    }
  }

  // Get product cost history
  const getProductCostHistory = async (productId) => {
    try {
      const response = await api.getProductCostHistory(productId)
      return response.data
    } catch (err) {
      console.error('Error fetching cost history:', err)
      const errorMessage = 'Failed to load cost history. Please try again later.'
      throw new Error(errorMessage)
    }
  }

  // Find a product by ID
  const findProductById = (productId) => {
    return products.value.find(product => product.id === productId)
  }

  return {
    // State
    products,
    loading,
    error,
    
    // Computed
    productCount,
    
    // Methods
    fetchProducts,
    createProduct,
    updateProduct,
    deleteProduct,
    getProductCostHistory,
    findProductById
  }
} 