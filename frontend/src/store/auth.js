import { defineStore } from 'pinia'
import axios from 'axios'

const API_URL = import.meta.env.VITE_API_URL

export const useAuthStore = defineStore('auth', {
  state: () => ({
    user: null,
    token: localStorage.getItem('token') || null,
    refreshToken: localStorage.getItem('refreshToken') || null
  }),
  
  getters: {
    isAuthenticated: (state) => !!state.token
  },
  
  actions: {
    async login(username, password) {
      try {
        const response = await axios.post(`${API_URL}/token/`, {
          username,
          password
        })
        
        this.token = response.data.access
        this.refreshToken = response.data.refresh
        
        localStorage.setItem('token', this.token)
        localStorage.setItem('refreshToken', this.refreshToken)
        
        // Fetch user profile
        await this.fetchUser()
        
        return { success: true }
      } catch (error) {
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
    }
  }
}) 