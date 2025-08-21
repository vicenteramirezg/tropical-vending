import { ref, computed } from 'vue'
import { api } from '../services/api'

export function useProducts() {
  const products = ref([])
  const loading = ref(true)
  const error = ref(null)
  
  // Pagination state
  const currentPage = ref(1)
  const pageSize = ref(50)
  const totalCount = ref(0)
  const totalPages = ref(1)

  // Computed properties
  const productCount = computed(() => products.value.length)
  const hasNextPage = computed(() => currentPage.value < totalPages.value)
  const hasPreviousPage = computed(() => currentPage.value > 1)

  // Fetch products with pagination
  const fetchProducts = async (page = 1, size = pageSize.value, filterParams = {}) => {
    loading.value = true
    error.value = null
    
    try {
      const params = {
        page: page,
        page_size: size,
        ...filterParams
      }
      
      const response = await api.getProducts(params)
      
      // Handle paginated response
      if (response.data.results) {
        products.value = response.data.results
        totalCount.value = response.data.count || 0
        totalPages.value = Math.ceil(totalCount.value / size)
        currentPage.value = page
        pageSize.value = size
      } else {
        // Fallback for non-paginated responses
        products.value = response.data
        totalCount.value = response.data.length || 0
        totalPages.value = 1
        currentPage.value = 1
      }
      
      // Log product data for debugging
      console.log('Products loaded:', products.value.length)
      console.log('Pagination info:', { page, size, totalCount: totalCount.value, totalPages: totalPages.value })
      console.log('Filter params:', filterParams)
      
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

  // Go to specific page
  const goToPage = async (page) => {
    if (page >= 1 && page <= totalPages.value && page !== currentPage.value) {
      await fetchProducts(page, pageSize.value)
    }
  }

  // Change page size
  const changePageSize = async (size) => {
    if (size !== pageSize.value) {
      await fetchProducts(1, size) // Reset to first page when changing page size
    }
  }

  // Go to next page
  const nextPage = async () => {
    if (hasNextPage.value) {
      await goToPage(currentPage.value + 1)
    }
  }

  // Go to previous page
  const previousPage = async () => {
    if (hasPreviousPage.value) {
      await goToPage(currentPage.value - 1)
    }
  }

  // Create a new product
  const createProduct = async (productData) => {
    try {
      console.log('Sending product data:', JSON.stringify(productData))
      const response = await api.createProduct(productData)
      console.log('Product created successfully:', response.data)
      
      // Refresh the products list (stay on current page)
      await fetchProducts(currentPage.value, pageSize.value)
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
      
      // Refresh the products list (stay on current page)
      await fetchProducts(currentPage.value, pageSize.value)
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
      
      // Refresh the products list (stay on current page, but go back if current page is empty)
      const currentPageSize = products.value.length
      if (currentPageSize === 1 && currentPage.value > 1) {
        // If we deleted the last item on the page, go to previous page
        await goToPage(currentPage.value - 1)
      } else {
        await fetchProducts(currentPage.value, pageSize.value)
      }
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

  // Reset pagination to first page
  const resetToFirstPage = async () => {
    await fetchProducts(1, pageSize.value)
  }

  return {
    // State
    products,
    loading,
    error,
    
    // Pagination state
    currentPage,
    pageSize,
    totalCount,
    totalPages,
    
    // Computed
    productCount,
    hasNextPage,
    hasPreviousPage,
    
    // Methods
    fetchProducts,
    goToPage,
    changePageSize,
    nextPage,
    previousPage,
    resetToFirstPage,
    createProduct,
    updateProduct,
    deleteProduct,
    getProductCostHistory,
    findProductById
  }
} 