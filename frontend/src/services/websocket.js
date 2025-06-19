class WebSocketService {
  constructor() {
    this.connections = new Map()
    this.listeners = new Map()
    this.reconnectAttempts = new Map()
    this.maxReconnectAttempts = 5
    this.reconnectDelay = 3000
  }
  
  connect(type) {
    if (this.connections.has(type)) {
      return // Already connected
    }
    
    const wsProtocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:'
    const wsHost = import.meta.env.VITE_WS_HOST || window.location.host
    const wsUrl = `${wsProtocol}//${wsHost}/ws/${type}`
    
    try {
      const ws = new WebSocket(wsUrl)
      
      ws.onopen = () => {
        console.log(`WebSocket connected: ${type}`)
        this.connections.set(type, ws)
        this.reconnectAttempts.set(type, 0)
        
        // Notify listeners about connection status
        this.notifyListeners(type, {
          type: 'connection_status',
          status: 'connected'
        })
      }
      
      ws.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data)
          this.notifyListeners(type, data)
        } catch (error) {
          console.error('Error parsing WebSocket message:', error)
        }
      }
      
      ws.onclose = () => {
        console.log(`WebSocket disconnected: ${type}`)
        this.connections.delete(type)
        
        // Notify listeners about disconnection
        this.notifyListeners(type, {
          type: 'connection_status',
          status: 'disconnected'
        })
        
        this.scheduleReconnect(type)
      }
      
      ws.onerror = (error) => {
        console.error(`WebSocket error (${type}):`, error)
        
        // Notify listeners about error
        this.notifyListeners(type, {
          type: 'connection_status',
          status: 'error',
          error: error
        })
      }
      
    } catch (error) {
      console.error(`Failed to create WebSocket connection (${type}):`, error)
      this.scheduleReconnect(type)
    }
  }
  
  disconnect(type) {
    const ws = this.connections.get(type)
    if (ws) {
      ws.close()
      this.connections.delete(type)
      this.reconnectAttempts.delete(type)
    }
  }
  
  send(type, data) {
    const ws = this.connections.get(type)
    if (ws && ws.readyState === WebSocket.OPEN) {
      ws.send(JSON.stringify(data))
      return true
    }
    return false
  }
  
  onMessage(type, callback) {
    if (!this.listeners.has(type)) {
      this.listeners.set(type, [])
    }
    this.listeners.get(type).push(callback)
  }
  
  offMessage(type, callback) {
    const listeners = this.listeners.get(type)
    if (listeners) {
      const index = listeners.indexOf(callback)
      if (index > -1) {
        listeners.splice(index, 1)
      }
    }
  }
  
  notifyListeners(type, data) {
    const listeners = this.listeners.get(type)
    if (listeners) {
      listeners.forEach(callback => {
        try {
          callback(data)
        } catch (error) {
          console.error('Error in WebSocket listener:', error)
        }
      })
    }
  }
  
  scheduleReconnect(type) {
    const attempts = this.reconnectAttempts.get(type) || 0
    
    if (attempts < this.maxReconnectAttempts) {
      const delay = this.reconnectDelay * Math.pow(2, attempts) // Exponential backoff
      
      console.log(`Scheduling WebSocket reconnect for ${type} in ${delay}ms (attempt ${attempts + 1}/${this.maxReconnectAttempts})`)
      
      setTimeout(() => {
        this.reconnectAttempts.set(type, attempts + 1)
        this.connect(type)
      }, delay)
    } else {
      console.error(`Max reconnection attempts reached for WebSocket: ${type}`)
    }
  }
  
  isConnected(type) {
    const ws = this.connections.get(type)
    return ws && ws.readyState === WebSocket.OPEN
  }
  
  getConnectionStatus() {
    const status = {}
    for (const [type, ws] of this.connections) {
      status[type] = {
        connected: ws.readyState === WebSocket.OPEN,
        readyState: ws.readyState,
        reconnectAttempts: this.reconnectAttempts.get(type) || 0
      }
    }
    return status
  }
  
  disconnectAll() {
    for (const type of this.connections.keys()) {
      this.disconnect(type)
    }
    this.listeners.clear()
  }
}

// Create singleton instance
const websocketService = new WebSocketService()

export default websocketService
