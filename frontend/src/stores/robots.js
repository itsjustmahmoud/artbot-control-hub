import { defineStore } from 'pinia'
import apiClient from '@/services/api'
import websocketService from '@/services/websocket'

export const useRobotsStore = defineStore('robots', {
  state: () => ({
    robots: {},
    exhibitionStatus: {
      total_robots: 0,
      online_robots: 0,
      active_robots: 0,
      exhibition_running: false,
      last_update: null
    },
    isLoading: false,
    error: null
  }),
  
  getters: {
    robotsList: (state) => Object.values(state.robots),
    onlineRobots: (state) => Object.values(state.robots).filter(robot => robot.status !== 'offline'),
    activeRobots: (state) => Object.values(state.robots).filter(robot => robot.status === 'active'),
    totalRobots: (state) => Object.keys(state.robots).length
  },
    actions: {
    async initialize() {
      // Set up WebSocket connection for real-time updates
      websocketService.addListener('dashboard', this.handleWebSocketMessage)
      websocketService.connect('dashboard')
      
      // Initial fetch
      await this.fetchRobots()
      await this.fetchExhibitionStatus()
    },
    
    handleWebSocketMessage(message) {
      switch (message.type) {
        case 'robot_update':
          this.updateRobot(message.robot_id, message.data)
          break
        case 'system_alert':
          console.warn('System Alert:', message)
          break
        case 'command_response':
          console.log('Command Response:', message)
          break
        case 'connection_status':
          console.log('WebSocket status:', message.status)
          break
        default:
          console.log('Unknown WebSocket message:', message)
      }
    },
    
    updateRobot(robotId, robotData) {
      if (this.robots[robotId]) {
        this.robots[robotId] = { ...this.robots[robotId], ...robotData }
      } else {
        this.robots[robotId] = { id: robotId, ...robotData }
      }
      
      // Update exhibition status counters
      this.updateExhibitionStatus()
    },
    
    updateExhibitionStatus() {
      const robots = Object.values(this.robots)
      this.exhibitionStatus = {
        total_robots: robots.length,
        online_robots: robots.filter(r => r.status !== 'offline').length,
        active_robots: robots.filter(r => r.status === 'active').length,
        exhibition_running: robots.some(r => r.status === 'active'),
        last_update: new Date().toISOString()
      }
    },
    
    async fetchRobots() {
      this.isLoading = true
      this.error = null
      
      try {
        const response = await apiClient.get('/robots')
        
        // Convert array to object with robot ID as key
        this.robots = {}
        response.data.robots.forEach(robot => {
          this.robots[robot.id] = robot
        })
        
        this.updateExhibitionStatus()
        
      } catch (error) {
        this.error = error.response?.data?.detail || 'Failed to fetch robots'
        console.error('Error fetching robots:', error)
      } finally {
        this.isLoading = false
      }
    },
    
    async fetchExhibitionStatus() {
      try {
        const response = await apiClient.get('/robots/exhibition/status')
        this.exhibitionStatus = response.data
      } catch (error) {
        console.error('Error fetching exhibition status:', error)
      }
    },
    
    async sendRobotCommand(robotId, action, parameters = {}) {
      try {
        const response = await apiClient.post(`/robots/${robotId}/command`, {
          action,
          parameters
        })
        
        // Update robot status optimistically
        if (this.robots[robotId]) {
          switch (action) {
            case 'start':
              this.robots[robotId].status = 'active'
              this.robots[robotId].current_action = 'person_following'
              break
            case 'stop':
              this.robots[robotId].status = 'idle'
              this.robots[robotId].current_action = 'stopped'
              break
            case 'restart':
              this.robots[robotId].status = 'restarting'
              this.robots[robotId].current_action = 'system_restart'
              break
          }
          this.robots[robotId].last_update = new Date().toISOString()
        }
        
        return response.data
        
      } catch (error) {
        this.error = error.response?.data?.detail || `Failed to ${action} robot`
        throw error
      }
    },
    
    async sendExhibitionCommand(action) {
      try {
        const response = await apiClient.post('/robots/exhibition/command', {
          action: action === 'start' ? 'start_all' : 'stop_all'
        })
        
        // Update all robot statuses optimistically
        Object.values(this.robots).forEach(robot => {
          if (action === 'start') {
            robot.status = 'active'
            robot.current_action = 'person_following'
          } else {
            robot.status = 'idle'
            robot.current_action = 'stopped'
          }
          robot.last_update = new Date().toISOString()
        })
        
        // Update exhibition status
        this.exhibitionStatus.exhibition_running = action === 'start'
        this.exhibitionStatus.active_robots = action === 'start' ? this.exhibitionStatus.online_robots : 0
        
        return response.data
        
      } catch (error) {
        this.error = error.response?.data?.detail || `Failed to ${action} exhibition`
        throw error
      }
    },
    
    updateRobotFromWebSocket(robotData) {
      if (robotData.id && this.robots[robotData.id]) {
        this.robots[robotData.id] = { ...this.robots[robotData.id], ...robotData }
      }
    },
    
    addRobot(robotData) {
      if (robotData.id) {
        this.robots[robotData.id] = robotData
      }
    },
    
    removeRobot(robotId) {
      if (this.robots[robotId]) {
        delete this.robots[robotId]
      }
    },
    
    // Initialize real-time updates
    initializeRealTimeUpdates() {
      websocketService.connect('robots')
      
      websocketService.onMessage('robots', (data) => {
        if (data.type === 'robot_update') {
          this.updateRobotFromWebSocket(data.robot)
        } else if (data.type === 'exhibition_status') {
          this.exhibitionStatus = { ...this.exhibitionStatus, ...data.status }
        }
      })
    },
    
    clearError() {
      this.error = null
    },
    
    // New role-based API methods
    async sendWorkspaceCommand(robotId, action) {
      try {
        const endpoint = action === 'start' ? 'start' : 'stop'
        const response = await apiClient.post(`/robots/${robotId}/workspace/${endpoint}`)
        
        // Update robot workspace status optimistically
        if (this.robots[robotId]) {
          this.robots[robotId].workspace_status = action === 'start' ? 'running' : 'stopped'
          this.robots[robotId].last_update = new Date().toISOString()
        }
        
        return response.data
        
      } catch (error) {
        this.error = error.response?.data?.detail || `Failed to ${action} workspace`
        throw error
      }
    },
    
    async sendCreate3Command(robotId, action) {
      try {
        const response = await apiClient.post(`/robots/${robotId}/create3/${action}`)
        
        // Update robot Create3 status optimistically
        if (this.robots[robotId]) {
          this.robots[robotId].create3_status = action === 'restart' ? 'restarting' : 'rebooting'
          this.robots[robotId].last_update = new Date().toISOString()
        }
        
        return response.data
        
      } catch (error) {
        this.error = error.response?.data?.detail || `Failed to ${action} Create3`
        throw error
      }
    },
    
    async getWorkspaceLogs(robotId) {
      try {
        const response = await apiClient.get(`/robots/${robotId}/workspace/logs`)
        return response.data
        
      } catch (error) {
        this.error = error.response?.data?.detail || 'Failed to get workspace logs'
        throw error
      }
    },
  }
})
