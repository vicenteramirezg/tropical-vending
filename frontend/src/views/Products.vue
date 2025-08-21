<template>
  <div>
    <!-- Header -->
    <div class="flex justify-between items-center mb-6">
      <h1 class="text-2xl font-semibold text-gray-900">Products</h1>
      <button 
        @click="openAddModal" 
        class="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-primary-600 hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500 transition-colors duration-150"
      >
        <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 mr-1.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
        </svg>
        Add Product
      </button>
    </div>

    <!-- Filters -->
    <ProductFilters
      v-model:searchQuery="searchQuery"
      v-model:selectedProductType="selectedProductType"
      :hasActiveFilters="hasActiveFilters"
      :activeFilters="activeFilters"
      :filteredCount="filteredProducts.length"
      :totalCount="totalCount"
      @clearSearch="clearSearch"
      @clearAllFilters="clearAllFilters"
      @removeFilter="removeFilter"
    />
    
    <!-- Loading State -->
    <div v-if="loading" class="flex justify-center py-20">
      <div class="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-primary-500"></div>
    </div>
    
    <!-- Error State -->
    <div v-else-if="error" class="bg-red-50 border-l-4 border-red-400 p-4 mb-6 rounded-r-lg shadow-sm">
      <div class="flex">
        <div class="flex-shrink-0">
          <svg class="h-5 w-5 text-red-400" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor">
            <path fill-rule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clip-rule="evenodd" />
          </svg>
        </div>
        <div class="ml-3">
          <p class="text-sm text-red-700">{{ error }}</p>
        </div>
      </div>
    </div>
    
    <!-- No Results State -->
    <EmptyState
      v-else-if="filteredProducts.length === 0 && hasActiveFilters"
      type="no-results"
      title="No products found"
      description="No products match your current filters."
      :activeFilters="activeFilters"
      :showClearFilters="true"
      @clearFilters="clearAllFilters"
    />
    
    <!-- Empty State -->
    <EmptyState
      v-else-if="products.length === 0"
      type="empty"
      title="No products found"
      description="Get started by adding your first product."
      buttonText="Add Product"
      :showButton="true"
      @action="openAddModal"
    />
    
    <!-- Products List -->
    <ProductList
      v-else
      :products="filteredProducts"
      @edit="editProduct"
      @viewCostHistory="viewCostHistory"
      @delete="confirmDelete"
    />
    
    <!-- Pagination -->
    <Pagination
      v-if="totalPages > 1 && !loading && !error"
      :current-page="currentPage"
      :total-pages="totalPages"
      :total-items="totalCount"
      :page-size="pageSize"
      :page-size-options="[10, 20, 50, 100]"
      @page-change="handlePageChange"
      @page-size-change="handlePageSizeChange"
    />
    
    <!-- Product Form Modal -->
    <ProductFormModal
      :show="showModal"
      :product="currentProduct"
      :loading="modalLoading"
      @close="closeModal"
      @save="saveProduct"
    />
    
    <!-- Delete Confirmation Modal -->
    <DeleteConfirmationModal
      :show="showDeleteModal"
      :title="`Delete Product`"
      :message="`Are you sure you want to delete ${productToDelete?.name}? This action cannot be undone.`"
      :loading="deleteLoading"
      @close="closeDeleteModal"
      @confirm="deleteProduct"
    />

    <!-- Cost History Modal -->
    <CostHistoryModal
      :show="showCostHistoryModal"
      :product="selectedProduct"
      :costHistory="costHistory"
      :loading="costHistoryLoading"
      :error="costHistoryError"
      @close="closeCostHistoryModal"
    />
  </div>
</template>

<script setup>
import { ref, onMounted, watch, computed } from 'vue'
import { useProducts } from '../composables/useProducts'
import { useProductFilters } from '../composables/useProductFilters'
import ProductFilters from '../components/products/ProductFilters.vue'
import ProductList from '../components/products/ProductList.vue'
import ProductFormModal from '../components/products/ProductFormModal.vue'
import DeleteConfirmationModal from '../components/products/DeleteConfirmationModal.vue'
import CostHistoryModal from '../components/products/CostHistoryModal.vue'
import EmptyState from '../components/products/EmptyState.vue'
import Pagination from '../components/common/Pagination.vue'

// Use composables
const {
  products,
  loading,
  error,
  productCount,
  currentPage,
  pageSize,
  totalCount,
  totalPages,
  fetchProducts,
  goToPage,
  changePageSize,
  createProduct,
  updateProduct,
  deleteProduct: deleteProductApi,
  getProductCostHistory,
  resetToFirstPage
} = useProducts()

const {
  searchQuery,
  selectedProductType,
  hasActiveFilters,
  activeFilters,
  getFilteredProducts,
  getFilterParams,
  clearSearch,
  clearAllFilters,
  removeFilter
} = useProductFilters()

// Computed filtered products (for display purposes)
const filteredProducts = computed(() => {
  return getFilteredProducts(products.value)
})

// Watch for filter changes and reset to first page
watch([searchQuery, selectedProductType], async () => {
  if (hasActiveFilters.value) {
    await resetToFirstPage()
  }
})

// Enhanced fetch products with filters
const fetchProductsWithFilters = async (page = 1, size = pageSize.value) => {
  const filterParams = getFilterParams()
  
  // Call the base fetchProducts function with filters
  await fetchProducts(page, size, filterParams)
}

// Modal states
const showModal = ref(false)
const showDeleteModal = ref(false)
const showCostHistoryModal = ref(false)
const modalLoading = ref(false)
const deleteLoading = ref(false)
const costHistoryLoading = ref(false)

// Current data
const currentProduct = ref(null)
const productToDelete = ref(null)
const selectedProduct = ref(null)
const costHistory = ref([])
const costHistoryError = ref(null)

// Modal management
const openAddModal = () => {
  currentProduct.value = null
  showModal.value = true
}

const editProduct = (product) => {
  currentProduct.value = product
  showModal.value = true
}

const closeModal = () => {
  showModal.value = false
  currentProduct.value = null
  modalLoading.value = false
}

const confirmDelete = (product) => {
  productToDelete.value = product
  showDeleteModal.value = true
}

const closeDeleteModal = () => {
  showDeleteModal.value = false
  productToDelete.value = null
  deleteLoading.value = false
}

const viewCostHistory = async (product) => {
  selectedProduct.value = product
  showCostHistoryModal.value = true
  costHistoryLoading.value = true
  costHistoryError.value = null
  costHistory.value = []
  
  try {
    const history = await getProductCostHistory(product.id)
    costHistory.value = history
  } catch (err) {
    costHistoryError.value = err.message
  } finally {
    costHistoryLoading.value = false
  }
}

const closeCostHistoryModal = () => {
  showCostHistoryModal.value = false
  selectedProduct.value = null
  costHistory.value = []
  costHistoryError.value = null
}

// Pagination handlers
const handlePageChange = async (page) => {
  await fetchProductsWithFilters(page, pageSize.value)
}

const handlePageSizeChange = async (size) => {
  await fetchProductsWithFilters(1, size) // Reset to first page when changing page size
}

// Product operations
const saveProduct = async (productData) => {
  modalLoading.value = true
  
  try {
    if (currentProduct.value?.id) {
      await updateProduct(currentProduct.value.id, productData)
    } else {
      await createProduct(productData)
    }
    
    closeModal()
  } catch (err) {
    // Error handling is done in the composable
    console.error('Error saving product:', err.message)
  } finally {
    modalLoading.value = false
  }
}

const deleteProduct = async () => {
  if (!productToDelete.value) return
  
  deleteLoading.value = true
  
  try {
    await deleteProductApi(productToDelete.value.id)
    closeDeleteModal()
  } catch (err) {
    console.error('Error deleting product:', err.message)
  } finally {
    deleteLoading.value = false
  }
}

// Initialize data on component mount
onMounted(() => {
  fetchProductsWithFilters()
})
</script> 