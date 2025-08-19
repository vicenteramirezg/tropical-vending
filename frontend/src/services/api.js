import axios from 'axios'
import { useAuthStore } from '../store/auth'

// Determine the API URL based on the current host
const isLocalhost = window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1';

// Get the API URL from environment variables or use fallbacks
let API_URL = isLocalhost ? 'http://localhost:8000/api' : '/api';
let MEDIA_URL = isLocalhost ? 'http://localhost:8000/media' : '/media';

// Debug logging
console.log('API Service - Current hostname:', window.location.hostname);
console.log('API Service - isLocalhost:', isLocalhost);
console.log('API Service - API_URL:', API_URL);
console.log('API Service - MEDIA_URL:', MEDIA_URL);
console.log('API Service - Environment:', import.meta.env.MODE);

// Cache configuration
const CACHE_TTL = 2 * 60 * 60 * 1000; // 2 hours in milliseconds
const cache = new Map();

// Cache utilities
const getCacheKey = (url, params = {}) => {
  const paramString = new URLSearchParams(params).toString();
  return `${url}${paramString ? '?' + paramString : ''}`;
};

const isCacheValid = (cacheEntry) => {
  return Date.now() - cacheEntry.timestamp < CACHE_TTL;
};

const getFromCache = (cacheKey) => {
  const cacheEntry = cache.get(cacheKey);
  if (cacheEntry && isCacheValid(cacheEntry)) {
    console.log('Cache hit:', cacheKey);
    return cacheEntry.data;
  }
  if (cacheEntry) {
    cache.delete(cacheKey); // Remove expired entry
  }
  return null;
};

const setCache = (cacheKey, data) => {
  cache.set(cacheKey, {
    data,
    timestamp: Date.now()
  });
  console.log('Cache set:', cacheKey);
};

// Cache invalidation patterns
const invalidateCachePattern = (pattern) => {
  const keysToDelete = [];
  for (const key of cache.keys()) {
    if (key.includes(pattern)) {
      keysToDelete.push(key);
    }
  }
  keysToDelete.forEach(key => cache.delete(key));
  console.log('Cache invalidated for pattern:', pattern, 'Keys removed:', keysToDelete.length);
};

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
    console.log('API Request:', config.method, config.url);
    return config
  },
  (error) => {
    console.error('API Request Error:', error);
    return Promise.reject(error)
  }
)

// Response interceptor for API calls
apiClient.interceptors.response.use(
  (response) => {
    console.log('API Response:', response.status, response.config.url);
    return response
  },
  async (error) => {
    console.error('API Response Error:', error?.response?.status, error?.config?.url, error.message);
    
    const originalRequest = error.config
    const authStore = useAuthStore()
    
    // If the error is 401 and we haven't retried yet
    if (error.response?.status === 401 && !originalRequest._retry && authStore.refreshToken) {
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
        window.location.href = '/home'
        return Promise.reject(refreshError)
      }
    }
    
    return Promise.reject(error)
  }
)

// Enhanced API client with caching
const cachedGet = async (url, params = {}, skipCache = false) => {
  const cacheKey = getCacheKey(url, params);
  
  if (!skipCache) {
    const cachedData = getFromCache(cacheKey);
    if (cachedData) {
      return { data: cachedData };
    }
  }
  
  const response = await apiClient.get(url, { params });
  setCache(cacheKey, response.data);
  return response;
};

// Batch API calls utility
const batchApiCalls = async (calls) => {
  try {
    const results = await Promise.all(calls);
    return results;
  } catch (error) {
    console.error('Batch API call failed:', error);
    throw error;
  }
};

export const api = {
  // Utility methods
  batchApiCalls,
  invalidateCache: invalidateCachePattern,
  clearCache: () => {
    cache.clear();
    console.log('Cache cleared');
  },

  // Location endpoints
  getLocations(skipCache = false) {
    return cachedGet('/locations/', {}, skipCache)
  },
  getLocation(id) {
    return cachedGet(`/locations/${id}/`)
  },
  createLocation(data) {
    invalidateCachePattern('/locations');
    return apiClient.post('/locations/', data)
  },
  updateLocation(id, data) {
    invalidateCachePattern('/locations');
    return apiClient.put(`/locations/${id}/`, data)
  },
  deleteLocation(id) {
    invalidateCachePattern('/locations');
    return apiClient.delete(`/locations/${id}/`)
  },
  getRoutes(skipCache = false) {
    return cachedGet('/locations/routes/', {}, skipCache)
  },
  
  // Machine endpoints
  getMachines(params = {}, skipCache = false) {
    return cachedGet('/machines/', params, skipCache)
  },
  getMachine(id) {
    return cachedGet(`/machines/${id}/`)
  },
  createMachine(data) {
    invalidateCachePattern('/machines');
    return apiClient.post('/machines/', data)
  },
  updateMachine(id, data) {
    invalidateCachePattern('/machines');
    return apiClient.put(`/machines/${id}/`, data)
  },
  deleteMachine(id) {
    invalidateCachePattern('/machines');
    return apiClient.delete(`/machines/${id}/`)
  },
  
  // Product endpoints
  getProducts(params = {}, skipCache = false) {
    return cachedGet('/products/', params, skipCache)
  },
  getProduct(id) {
    return cachedGet(`/products/${id}/`)
  },
  createProduct(data) {
    invalidateCachePattern('/products');
    return apiClient.post('/products/', data)
  },
  updateProduct(id, data) {
    invalidateCachePattern('/products');
    return apiClient.put(`/products/${id}/`, data)
  },
  deleteProduct(id) {
    invalidateCachePattern('/products');
    return apiClient.delete(`/products/${id}/`)
  },
  
  // Machine Item Price endpoints
  getMachineItems(params = {}, skipCache = false) {
    return cachedGet('/machine-items/', params, skipCache)
  },
  getMachineItem(id) {
    return cachedGet(`/machine-items/${id}/`)
  },
  createMachineItem(data) {
    invalidateCachePattern('/machine-items');
    return apiClient.post('/machine-items/', data)
  },
  updateMachineItem(id, data) {
    invalidateCachePattern('/machine-items');
    return apiClient.put(`/machine-items/${id}/`, data)
  },
  deleteMachineItem(id) {
    invalidateCachePattern('/machine-items');
    return apiClient.delete(`/machine-items/${id}/`)
  },
  
  // Supplier endpoints
  getSuppliers(params = {}, skipCache = false) {
    return cachedGet('/suppliers/', params, skipCache)
  },
  getSupplier(id) {
    return cachedGet(`/suppliers/${id}/`)
  },
  createSupplier(data) {
    invalidateCachePattern('/suppliers');
    return apiClient.post('/suppliers/', data)
  },
  updateSupplier(id, data) {
    invalidateCachePattern('/suppliers');
    return apiClient.put(`/suppliers/${id}/`, data)
  },
  deleteSupplier(id) {
    invalidateCachePattern('/suppliers');
    return apiClient.delete(`/suppliers/${id}/`)
  },
  getActiveSuppliers(skipCache = false) {
    return cachedGet('/suppliers/active/', {}, skipCache)
  },
  toggleSupplierActive(id) {
    invalidateCachePattern('/suppliers');
    return apiClient.post(`/suppliers/${id}/toggle_active/`)
  },
  
  // Wholesale Purchase endpoints
  getPurchases(params = {}, skipCache = false) {
    return cachedGet('/purchases/', params, skipCache)
  },
  getPurchase(id) {
    return cachedGet(`/purchases/${id}/`)
  },
  createPurchase(data) {
    invalidateCachePattern('/purchases');
    invalidateCachePattern('/products'); // Purchases affect product inventory
    return apiClient.post('/purchases/', data)
  },
  updatePurchase(id, data) {
    invalidateCachePattern('/purchases');
    invalidateCachePattern('/products');
    return apiClient.put(`/purchases/${id}/`, data)
  },
  deletePurchase(id) {
    invalidateCachePattern('/purchases');
    invalidateCachePattern('/products');
    return apiClient.delete(`/purchases/${id}/`)
  },
  
  // Visit endpoints
  getVisits(params = {}, skipCache = false) {
    return cachedGet('/visits/', params, skipCache)
  },
  getVisit(id) {
    return cachedGet(`/visits/${id}/`)
  },
  createVisit(data) {
    invalidateCachePattern('/visits');
    invalidateCachePattern('/analytics');
    invalidateCachePattern('/dashboard');
    invalidateCachePattern('/inventory');
    return apiClient.post('/visits/', data)
  },
  updateVisit(id, data) {
    invalidateCachePattern('/visits');
    invalidateCachePattern('/analytics');
    invalidateCachePattern('/dashboard');
    invalidateCachePattern('/inventory');
    return apiClient.put(`/visits/${id}/`, data)
  },
  
  // Bulk visit operations for performance optimization
  createVisitBulk(data) {
    invalidateCachePattern('/visits');
    invalidateCachePattern('/analytics');
    invalidateCachePattern('/dashboard');
    invalidateCachePattern('/inventory');
    return apiClient.post('/visits/bulk-save/', data)
  },
  updateVisitBulk(id, data) {
    invalidateCachePattern('/visits');
    invalidateCachePattern('/analytics');
    invalidateCachePattern('/dashboard');
    invalidateCachePattern('/inventory');
    return apiClient.put(`/visits/${id}/bulk-update/`, data)
  },
  deleteVisit(id) {
    invalidateCachePattern('/visits');
    invalidateCachePattern('/analytics');
    invalidateCachePattern('/dashboard');
    invalidateCachePattern('/inventory');
    return apiClient.delete(`/visits/${id}/`)
  },
  
  // Restock endpoints
  getRestocks(params = {}, skipCache = false) {
    return cachedGet('/restocks/', params, skipCache)
  },
  getRestock(id) {
    return cachedGet(`/restocks/${id}/`)
  },
  createRestock(data) {
    invalidateCachePattern('/restocks');
    invalidateCachePattern('/analytics');
    invalidateCachePattern('/dashboard');
    invalidateCachePattern('/inventory');
    return apiClient.post('/restocks/', data)
  },
  updateRestock(id, data) {
    invalidateCachePattern('/restocks');
    invalidateCachePattern('/analytics');
    invalidateCachePattern('/dashboard');
    invalidateCachePattern('/inventory');
    return apiClient.put(`/restocks/${id}/`, data)
  },
  deleteRestock(id) {
    invalidateCachePattern('/restocks');
    invalidateCachePattern('/analytics');
    invalidateCachePattern('/dashboard');
    invalidateCachePattern('/inventory');
    return apiClient.delete(`/restocks/${id}/`)
  },
  
  // Restock entry endpoints
  getRestockEntries(params = {}, skipCache = false) {
    return cachedGet('/restock-entries/', params, skipCache)
  },
  getRestockEntry(id) {
    return cachedGet(`/restock-entries/${id}/`)
  },
  createRestockEntry(data) {
    invalidateCachePattern('/restock-entries');
    invalidateCachePattern('/analytics');
    invalidateCachePattern('/dashboard');
    invalidateCachePattern('/inventory');
    return apiClient.post('/restock-entries/', data)
  },
  updateRestockEntry(id, data) {
    invalidateCachePattern('/restock-entries');
    invalidateCachePattern('/analytics');
    invalidateCachePattern('/dashboard');
    invalidateCachePattern('/inventory');
    return apiClient.put(`/restock-entries/${id}/`, data)
  },
  deleteRestockEntry(id) {
    invalidateCachePattern('/restock-entries');
    invalidateCachePattern('/analytics');
    invalidateCachePattern('/dashboard');
    invalidateCachePattern('/inventory');
    return apiClient.delete(`/restock-entries/${id}/`)
  },
  
  // Analytics endpoints - cached with shorter TTL for dynamic data
  getDashboardData(params = {}, skipCache = false) {
    return cachedGet('/dashboard/', params, skipCache)
  },
  getStockLevels(params = {}, skipCache = false) {
    return cachedGet('/analytics/stock-levels/', params, skipCache)
  },
  getDemandAnalysis(params = {}, skipCache = false) {
    return cachedGet('/analytics/demand/', params, skipCache)
  },
  getRevenueProfitData(params = {}, skipCache = false) {
    return cachedGet('/analytics/revenue-profit/', params, skipCache)
  },
  
  getProductCostHistory: async (productId, skipCache = false) => {
    return await cachedGet(`/product-costs/?product=${productId}`, {}, skipCache);
  },

  // Inventory reporting endpoints
  getCurrentStockReport(params = {}, skipCache = false) {
    return cachedGet('/inventory/current-stock/', params, skipCache)
  },
  getRestockSummary(params = {}, skipCache = false) {
    return cachedGet('/inventory/restock-summary/', params, skipCache)
  },
  getStockCoverageEstimate(params = {}, skipCache = false) {
    return cachedGet('/inventory/stock-coverage/', params, skipCache)
  }
}

// Helper function to get image URL
export const getImageUrl = (imagePath) => {
  if (!imagePath) return null
  if (imagePath.startsWith('http')) return imagePath
  return `${MEDIA_URL}/${imagePath}`
} 