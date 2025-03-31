import axios from 'axios'
import { useAuthStore } from '../store/auth'

// Get the API URL from environment variables or use fallbacks
const API_URL = import.meta.env.VITE_API_URL || '/api'
const MEDIA_URL = import.meta.env.VITE_MEDIA_URL || '/media'

// Debug logging
console.log('API Service - API_URL:', API_URL)
console.log('API Service - MEDIA_URL:', MEDIA_URL)
console.log('API Service - Environment:', import.meta.env.MODE)

// Create an axios instance for API calls
const apiClient = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json'
  }
})

// Request interceptor for API calls
apiClient.interceptors.request.use(
  (config) => {
    const authStore = useAuthStore()
    if (authStore.token) {
      config.headers['Authorization'] = `Bearer ${authStore.token}`
    }
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// Response interceptor for API calls
apiClient.interceptors.response.use(
  (response) => {
    return response
  },
  async (error) => {
    const originalRequest = error.config
    const authStore = useAuthStore()
    
    // If the error is 401 and we haven't retried yet
    if (error.response.status === 401 && !originalRequest._retry && authStore.refreshToken) {
      originalRequest._retry = true
      
      try {
        // Try refreshing the token
        const refreshResult = await authStore.refreshUserToken()
        
        if (refreshResult.success) {
          // Update the header with the new token
          originalRequest.headers['Authorization'] = `Bearer ${authStore.token}`
          return apiClient(originalRequest)
        }
      } catch (refreshError) {
        // If refresh fails, route to login
        authStore.logout()
        window.location.href = '/login'
        return Promise.reject(refreshError)
      }
    }
    
    return Promise.reject(error)
  }
)

export const api = {
  // Location endpoints
  getLocations() {
    return apiClient.get('/locations/')
  },
  getLocation(id) {
    return apiClient.get(`/locations/${id}/`)
  },
  createLocation(data) {
    return apiClient.post('/locations/', data)
  },
  updateLocation(id, data) {
    return apiClient.put(`/locations/${id}/`, data)
  },
  deleteLocation(id) {
    return apiClient.delete(`/locations/${id}/`)
  },
  
  // Machine endpoints
  getMachines(params = {}) {
    return apiClient.get('/machines/', { params })
  },
  getMachine(id) {
    return apiClient.get(`/machines/${id}/`)
  },
  createMachine(data) {
    return apiClient.post('/machines/', data)
  },
  updateMachine(id, data) {
    return apiClient.put(`/machines/${id}/`, data)
  },
  deleteMachine(id) {
    return apiClient.delete(`/machines/${id}/`)
  },
  
  // Product endpoints
  getProducts(params = {}) {
    return apiClient.get('/products/', { params })
  },
  getProduct(id) {
    return apiClient.get(`/products/${id}/`)
  },
  createProduct(data) {
    // Use FormData for file uploads
    const formData = new FormData()
    Object.keys(data).forEach(key => {
      formData.append(key, data[key])
    })
    
    return apiClient.post('/products/', formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    })
  },
  updateProduct(id, data) {
    // Use FormData for file uploads
    const formData = new FormData()
    Object.keys(data).forEach(key => {
      formData.append(key, data[key])
    })
    
    return apiClient.put(`/products/${id}/`, formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    })
  },
  deleteProduct(id) {
    return apiClient.delete(`/products/${id}/`)
  },
  
  // Machine Item Price endpoints
  getMachineItems(params = {}) {
    return apiClient.get('/machine-items/', { params })
  },
  getMachineItem(id) {
    return apiClient.get(`/machine-items/${id}/`)
  },
  createMachineItem(data) {
    return apiClient.post('/machine-items/', data)
  },
  updateMachineItem(id, data) {
    return apiClient.put(`/machine-items/${id}/`, data)
  },
  deleteMachineItem(id) {
    return apiClient.delete(`/machine-items/${id}/`)
  },
  
  // Wholesale Purchase endpoints
  getPurchases(params = {}) {
    return apiClient.get('/purchases/', { params })
  },
  getPurchase(id) {
    return apiClient.get(`/purchases/${id}/`)
  },
  createPurchase(data) {
    return apiClient.post('/purchases/', data)
  },
  updatePurchase(id, data) {
    return apiClient.put(`/purchases/${id}/`, data)
  },
  deletePurchase(id) {
    return apiClient.delete(`/purchases/${id}/`)
  },
  
  // Visit endpoints
  getVisits(params = {}) {
    return apiClient.get('/visits/', { params })
  },
  getVisit(id) {
    return apiClient.get(`/visits/${id}/`)
  },
  createVisit(data) {
    return apiClient.post('/visits/', data)
  },
  updateVisit(id, data) {
    return apiClient.put(`/visits/${id}/`, data)
  },
  deleteVisit(id) {
    return apiClient.delete(`/visits/${id}/`)
  },
  
  // Restock endpoints
  getRestocks(params = {}) {
    return apiClient.get('/restocks/', { params })
  },
  getRestock(id) {
    return apiClient.get(`/restocks/${id}/`)
  },
  createRestock(data) {
    return apiClient.post('/restocks/', data)
  },
  updateRestock(id, data) {
    return apiClient.put(`/restocks/${id}/`, data)
  },
  deleteRestock(id) {
    return apiClient.delete(`/restocks/${id}/`)
  },
  
  // Restock entry endpoints
  getRestockEntries(params = {}) {
    return apiClient.get('/restock-entries/', { params })
  },
  getRestockEntry(id) {
    return apiClient.get(`/restock-entries/${id}/`)
  },
  createRestockEntry(data) {
    return apiClient.post('/restock-entries/', data)
  },
  updateRestockEntry(id, data) {
    return apiClient.put(`/restock-entries/${id}/`, data)
  },
  deleteRestockEntry(id) {
    return apiClient.delete(`/restock-entries/${id}/`)
  },
  
  // Analytics endpoints
  getDashboardData() {
    return apiClient.get('/dashboard/')
  },
  getStockLevels(params = {}) {
    return apiClient.get('/analytics/stock-levels/', { params })
  },
  getDemandAnalysis(params = {}) {
    return apiClient.get('/analytics/demand/', { params })
  },
  getRevenueProfitData(params = {}) {
    return apiClient.get('/analytics/revenue-profit/', { params })
  }
}

// Helper function to get image URL
export const getImageUrl = (imagePath) => {
  if (!imagePath) return null
  if (imagePath.startsWith('http')) return imagePath
  return `${MEDIA_URL}/${imagePath}`
} 