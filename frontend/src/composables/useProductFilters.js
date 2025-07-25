import { ref, computed } from 'vue'

export function useProductFilters(products) {
  const searchQuery = ref('')
  const selectedProductType = ref('')

  // Computed property for filtered products
  const filteredProducts = computed(() => {
    let filtered = products.value || []

    // Filter by search query
    if (searchQuery.value.trim()) {
      const query = searchQuery.value.toLowerCase().trim()
      filtered = filtered.filter(product => 
        product.name.toLowerCase().includes(query)
      )
    }

    // Filter by product type
    if (selectedProductType.value) {
      filtered = filtered.filter(product => 
        product.product_type === selectedProductType.value
      )
    }

    return filtered
  })

  // Check if any filters are active
  const hasActiveFilters = computed(() => {
    return Boolean(searchQuery.value || selectedProductType.value)
  })

  // Get active filter tags for display
  const activeFilters = computed(() => {
    const filters = []
    
    if (searchQuery.value) {
      filters.push({
        type: 'search',
        label: `Name: "${searchQuery.value}"`,
        value: searchQuery.value,
        color: 'blue'
      })
    }
    
    if (selectedProductType.value) {
      filters.push({
        type: 'productType',
        label: `Type: ${selectedProductType.value}`,
        value: selectedProductType.value,
        color: 'green'
      })
    }
    
    return filters
  })

  // Clear search function
  const clearSearch = () => {
    searchQuery.value = ''
  }

  // Clear product type filter
  const clearProductType = () => {
    selectedProductType.value = ''
  }

  // Clear all filters function
  const clearAllFilters = () => {
    searchQuery.value = ''
    selectedProductType.value = ''
  }

  // Remove specific filter
  const removeFilter = (filterType) => {
    switch (filterType) {
      case 'search':
        clearSearch()
        break
      case 'productType':
        clearProductType()
        break
    }
  }

  return {
    // State
    searchQuery,
    selectedProductType,
    
    // Computed
    filteredProducts,
    hasActiveFilters,
    activeFilters,
    
    // Methods
    clearSearch,
    clearProductType,
    clearAllFilters,
    removeFilter
  }
} 