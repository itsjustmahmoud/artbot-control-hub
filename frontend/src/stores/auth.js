import { defineStore } from 'pinia'
import apiClient from '@/services/api'

export const useAuthStore = defineStore('auth', {
  state: () => ({
    token: localStorage.getItem('authToken'),
    accessLevel: localStorage.getItem('accessLevel'),
    isLoading: false,
    error: null
  }),
  
  getters: {
    isAuthenticated: (state) => !!state.token,
    isAdmin: (state) => state.accessLevel === 'ADMIN',
    isMuseum: (state) => state.accessLevel === 'MUSEUM'
  },
  
  actions: {
    async login(password) {
      this.isLoading = true
      this.error = null
      
      try {
        const response = await apiClient.post('/auth/validate', { password })
        
        this.token = response.data.access_token
        this.accessLevel = response.data.access_level
        
        // Store in localStorage
        localStorage.setItem('authToken', this.token)
        localStorage.setItem('accessLevel', this.accessLevel)
        
        // Set default header for future requests
        apiClient.defaults.headers.common['Authorization'] = `Bearer ${this.token}`
        
        return response.data
        
      } catch (error) {
        this.error = error.response?.data?.detail || 'Login failed'
        throw error
      } finally {
        this.isLoading = false
      }
    },
    
    logout() {
      this.token = null
      this.accessLevel = null
      this.error = null
      
      // Clear localStorage
      localStorage.removeItem('authToken')
      localStorage.removeItem('accessLevel')
      
      // Clear API client header
      delete apiClient.defaults.headers.common['Authorization']
    },
    
    hasRole(role) {
      if (this.accessLevel === 'ADMIN') {
        return true // Admin has access to everything
      }
      return this.accessLevel === role
    },
    
    hasPermission(permission) {
      // Simplified permission check
      if (this.accessLevel === 'ADMIN') {
        return true
      }
      
      const museumPermissions = [
        'robot.view',
        'exhibition.start',
        'exhibition.stop', 
        'logs.view_basic'
      ]
      
      return this.accessLevel === 'MUSEUM' && museumPermissions.includes(permission)
    },
    
    // Initialize auth state from localStorage on app start
    initializeAuth() {
      if (this.token) {
        apiClient.defaults.headers.common['Authorization'] = `Bearer ${this.token}`
      }
    }
  }
})
