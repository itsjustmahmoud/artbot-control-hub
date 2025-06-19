import axios from 'axios'

// Determine the correct API base URL
const getApiBaseUrl = () => {
  // If we're accessing via network IP, use that IP for the backend too
  const hostname = window.location.hostname
  const port = window.location.port
  
  if (hostname === 'localhost' || hostname === '127.0.0.1') {
    // Local access - use proxy
    return '/api'
  } else {
    // Network access - directly target the backend
    return `http://${hostname}:8000/api`
  }
}

// Create axios instance with base configuration
const apiClient = axios.create({
  baseURL: getApiBaseUrl(),
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json'
  }
})

// Request interceptor to add auth token
apiClient.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('authToken')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// Response interceptor to handle common errors
apiClient.interceptors.response.use(
  (response) => {
    return response
  },
  (error) => {
    if (error.response?.status === 401) {
      // Unauthorized - clear token and redirect to login
      localStorage.removeItem('authToken')
      localStorage.removeItem('accessLevel')
      window.location.href = '/'
    }
    
    return Promise.reject(error)
  }
)

export default apiClient
