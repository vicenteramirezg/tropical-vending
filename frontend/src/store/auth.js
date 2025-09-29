import { defineStore } from 'pinia'
import axios from 'axios'

// Determine the API URL based on environment and host
const isLocalhost = window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1'
const ENV_API_URL = import.meta?.env?.VITE_API_URL
const API_URL = ENV_API_URL || (isLocalhost ? 'http://localhost:8000/api' : '/api')

console.log('Auth Store - Current hostname:', window.location.hostname)
console.log('Auth Store - isLocalhost:', isLocalhost)
console.log('Auth Store - API_URL:', API_URL) // Debug log

export const useAuthStore = defineStore('auth', {
  state: () => ({
    user: null,
    token: localStorage.getItem('token') || null,
    refreshToken: localStorage.getItem('refreshToken') || null,
    logoutRedirect: '/home' // Store the logout redirect path here
  }),
  
  getters: {
    isAuthenticated: (state) => !!state.token
  },
  
  actions: {
    async login(username, password) {
      console.log(`Attempting login for user: ${username} with API URL: ${API_URL}`);
      
      try {
        const response = await axios.post(`${API_URL}/token/`, {
          username,
          password
        });
        
        console.log('Login response:', response.status);
        
        this.token = response.data.access
        this.refreshToken = response.data.refresh
        
        localStorage.setItem('token', this.token)
        localStorage.setItem('refreshToken', this.refreshToken)
        
        // Fetch user profile
        await this.fetchUser()
        
        return { success: true }
      } catch (error) {
        console.error('Login error:', error.message);
        if (error.response) {
          console.error('Login error status:', error.response.status);
          console.error('Login error data:', error.response.data);
        }
        return {
          success: false,
          message: error.response?.data?.detail || 'Login failed'
        }
      }
    },
    
    async register(userData) {
      try {
        await axios.post(`${API_URL}/register/`, userData)
        return { success: true }
      } catch (error) {
        return {
          success: false,
          message: error.response?.data || 'Registration failed'
        }
      }
    },
    
    async fetchUser() {
      try {
        const response = await axios.get(`${API_URL}/profile/`, {
          headers: {
            Authorization: `Bearer ${this.token}`
          }
        })
        
        this.user = response.data
        return { success: true }
      } catch (error) {
        return {
          success: false,
          message: error.response?.data?.detail || 'Failed to fetch user data'
        }
      }
    },
    
    async refreshUserToken() {
      try {
        const response = await axios.post(`${API_URL}/token/refresh/`, {
          refresh: this.refreshToken
        })
        
        this.token = response.data.access
        localStorage.setItem('token', this.token)
        
        return { success: true }
      } catch (error) {
        // If refresh fails, log the user out
        this.logout()
        return {
          success: false,
          message: 'Session expired. Please log in again.'
        }
      }
    },
    
    logout() {
      this.user = null
      this.token = null
      this.refreshToken = null
      
      localStorage.removeItem('token')
      localStorage.removeItem('refreshToken')
      
      // Don't handle navigation here, let components handle it
      return this.logoutRedirect
    }
  }
}) 
