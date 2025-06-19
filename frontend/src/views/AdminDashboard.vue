<template>
  <div class="admin-dashboard">
    <!-- Header -->
    <header class="dashboard-header">
      <div class="header-content">        <div class="brand-section">
          <div class="logo-icon">🤖</div>
          <div class="brand-text">
            <h1>🚀 ARTBOT CONTROL HUB 🚀</h1>
            <p>Administrator Control Center</p>
          </div>
        </div>
        <div class="header-actions">
          <div class="user-profile">
            <div class="avatar admin">AD</div>
            <div class="user-details">
              <span class="user-name">Administrator</span>
              <span class="user-role">Full Access</span>
            </div>
          </div>
          <button @click="handleLogout" class="logout-btn">
            <span class="logout-icon">🚪</span>
            Logout
          </button>
        </div>
      </div>
    </header>

    <!-- Status Overview -->
    <section class="status-overview">
      <div class="status-grid">
        <div class="status-card system-performance">
          <div class="card-icon">🚀</div>
          <div class="card-content">
            <h3>System Performance</h3>
            <div class="status-number">98.5%</div>
            <p class="status-subtitle">Overall uptime</p>
          </div>
        </div>
        <div class="status-card total-robots">
          <div class="card-icon">🤖</div>
          <div class="card-content">
            <h3>Total Robots</h3>
            <div class="status-number">{{ robotsList.length }}</div>
            <p class="status-subtitle">Fleet size</p>
          </div>
        </div>
        <div class="status-card active-sessions">
          <div class="card-icon">👥</div>
          <div class="card-content">
            <h3>Active Sessions</h3>
            <div class="status-number">3</div>
            <p class="status-subtitle">Connected users</p>
          </div>
        </div>
        <div class="status-card data-throughput">
          <div class="card-icon">📊</div>
          <div class="card-content">
            <h3>Data Throughput</h3>
            <div class="status-number">2.4 MB/s</div>
            <p class="status-subtitle">Network traffic</p>
          </div>
        </div>
      </div>
    </section>

    <!-- Robot Fleet -->
    <section class="robots-section">      <div class="section-header">
        <h2>🤖 Advanced Fleet Management</h2>
        <div class="header-controls">
          <div class="fleet-summary">
            <span class="summary-item active">{{ activeRobotsCount }} Active</span>
            <span class="summary-item idle">{{ idleRobotsCount }} Idle</span>
            <span class="summary-item offline">{{ offlineRobotsCount }} Offline</span>
          </div>
          <div class="fleet-actions">
            <button class="action-btn primary">Add Robot</button>
            <button class="action-btn secondary">Bulk Actions</button>
            <button class="action-btn secondary">Export Data</button>
          </div>        </div>
      </div>
      
      <!-- Loading State -->
      <div v-if="isLoading" class="loading-state">
        <div class="loading-spinner">⏳</div>
        <p>Loading robots...</p>
      </div>
      
      <!-- Empty State -->
      <div v-else-if="safeRobots.length === 0" class="empty-state">
        <div class="empty-icon">🤖</div>
        <h3>No Robots Available</h3>
        <p>No robots are currently connected to the system.</p>
      </div>
      
      <!-- Robots Grid -->
      <div v-else class="robots-grid">
        <div 
          v-for="robot in safeRobots" 
          :key="robot.id" 
          class="robot-card admin"
          :class="[robot.status.toLowerCase(), { 'low-battery': robot.battery < 20 }]"
        >
          <div class="robot-header">
            <div class="robot-identity">
              <div class="robot-avatar">{{ robot.name.slice(-3) }}</div>
              <div class="robot-info">
                <h3>{{ robot.name }}</h3>
                <p class="robot-location">📍 {{ robot.location }}</p>
                <p class="robot-id">ID: {{ robot.id }}</p>
              </div>
            </div>
            <div class="robot-status-badge" :class="robot.status.toLowerCase()">
              <div class="status-dot"></div>
              {{ robot.status }}
            </div>
          </div>
          
          <div class="robot-metrics">
            <div class="metric-card battery" :class="{ 'low': robot.battery < 20, 'critical': robot.battery < 10 }">
              <div class="metric-icon">🔋</div>
              <div class="metric-info">
                <span class="metric-label">Battery</span>
                <span class="metric-value">{{ robot.battery }}%</span>
              </div>
              <div class="battery-bar">
                <div class="battery-fill" :style="{ width: robot.battery + '%' }"></div>
              </div>
            </div>
            
            <div class="metric-card uptime">
              <div class="metric-icon">⏰</div>
              <div class="metric-info">
                <span class="metric-label">Last Seen</span>
                <span class="metric-value">{{ formatTime(robot.lastSeen) }}</span>
              </div>
            </div>
            
            <div class="metric-card cpu">
              <div class="metric-icon">💻</div>
              <div class="metric-info">
                <span class="metric-label">CPU Usage</span>
                <span class="metric-value">{{ Math.floor(Math.random() * 40 + 20) }}%</span>
              </div>
            </div>
            
            <div class="metric-card memory">
              <div class="metric-icon">🧠</div>
              <div class="metric-info">
                <span class="metric-label">Memory</span>
                <span class="metric-value">{{ Math.floor(Math.random() * 60 + 30) }}%</span>
              </div>
            </div>
          </div>

          <div class="robot-actions admin">
            <div class="primary-actions">
              <button @click="sendCommand(robot.id, 'start')" :disabled="robot.status === 'OFFLINE'" class="action-btn primary-btn start-btn">
                <span class="btn-icon">▶️</span>
                Start
              </button>
              <button @click="sendCommand(robot.id, 'stop')" :disabled="robot.status === 'OFFLINE'" class="action-btn primary-btn stop-btn">
                <span class="btn-icon">⏸️</span>
                Stop
              </button>
            </div>
            <div class="secondary-actions">
              <button @click="sendCommand(robot.id, 'reboot')" :disabled="robot.status === 'OFFLINE'" class="action-btn secondary-btn">
                <span class="btn-icon">🔄</span>
                Reboot
              </button>
              <button @click="configureRobot(robot.id)" class="action-btn secondary-btn">
                <span class="btn-icon">⚙️</span>
                Configure
              </button>
              <button @click="viewLogs(robot.id)" class="action-btn secondary-btn">
                <span class="btn-icon">📊</span>
                Logs
              </button>
              <button @click="deleteRobot(robot.id)" class="action-btn danger-btn">
                <span class="btn-icon">🗑️</span>
                Delete
              </button>
            </div>
          </div>        </div>
      </div>
    </section>

    <!-- Activity Feed -->
    <section class="activity-section">
      <div class="section-header">
        <h2>📈 System Activity & Monitoring</h2>
        <div class="admin-controls">
          <button class="action-btn secondary" @click="exportLogs">📤 Export Logs</button>
          <button class="action-btn secondary" @click="clearLogs">🗑️ Clear History</button>
          <button class="view-all-btn">View All</button>
        </div>
      </div>
      <div class="activity-feed">
        <div 
          v-for="log in recentLogs" 
          :key="log.id" 
          class="activity-item"
          :class="log.level.toLowerCase()"
        >
          <div class="activity-icon" :class="log.level.toLowerCase()">
            {{ log.level === 'INFO' ? 'ℹ️' : log.level === 'WARNING' ? '⚠️' : '🚨' }}
          </div>
          <div class="activity-content">
            <div class="activity-header">
              <span class="activity-robot">{{ log.robotId }}</span>
              <span class="activity-time">{{ formatTime(log.timestamp) }}</span>
            </div>
            <p class="activity-message">{{ log.message }}</p>
          </div>
          <div class="activity-actions">
            <button class="action-btn tiny" @click="viewLogDetails(log.id)">Details</button>
          </div>
        </div>
      </div>
    </section>

    <!-- Admin-Only Analytics Section -->
    <section class="analytics-section">
      <div class="section-header">
        <h2>📊 System Analytics & Management</h2>
        <div class="analytics-controls">
          <select class="time-filter">
            <option value="1h">Last Hour</option>
            <option value="24h" selected>Last 24 Hours</option>
            <option value="7d">Last 7 Days</option>
            <option value="30d">Last 30 Days</option>
          </select>
        </div>
      </div>
      
      <div class="analytics-grid">
        <!-- Performance Metrics -->
        <div class="analytics-card">
          <div class="card-header">
            <h3>⚡ Performance Metrics</h3>
            <span class="status-indicator healthy">Optimal</span>
          </div>
          <div class="metrics-list">
            <div class="metric-row">
              <span class="metric-label">Average Response Time</span>
              <span class="metric-value">127ms</span>
            </div>
            <div class="metric-row">
              <span class="metric-label">System Load</span>
              <span class="metric-value">23%</span>
            </div>
            <div class="metric-row">
              <span class="metric-label">Memory Usage</span>
              <span class="metric-value">1.2GB / 4GB</span>
            </div>
            <div class="metric-row">
              <span class="metric-label">Network Latency</span>
              <span class="metric-value">8ms</span>
            </div>
          </div>
        </div>

        <!-- Fleet Statistics -->
        <div class="analytics-card">
          <div class="card-header">
            <h3>🤖 Fleet Statistics</h3>
            <span class="status-indicator active">{{ robotsList.length }} Total</span>
          </div>
          <div class="stats-grid">
            <div class="stat-item">
              <div class="stat-number">{{ Math.round(robotsList.length * 0.85) }}</div>
              <div class="stat-label">Operational Hours</div>
            </div>
            <div class="stat-item">
              <div class="stat-number">98.5%</div>
              <div class="stat-label">Uptime</div>
            </div>
            <div class="stat-item">
              <div class="stat-number">{{ Math.round(robotsList.length * 0.72) }}</div>
              <div class="stat-label">Tasks Completed</div>
            </div>
            <div class="stat-item">
              <div class="stat-number">0</div>
              <div class="stat-label">Critical Errors</div>
            </div>
          </div>
        </div>

        <!-- System Health -->
        <div class="analytics-card full-width">
          <div class="card-header">
            <h3>🏥 System Health Dashboard</h3>
            <div class="health-controls">
              <button class="action-btn secondary tiny" @click="runDiagnostics">🔍 Run Diagnostics</button>
              <button class="action-btn secondary tiny" @click="restartSystem">🔄 Restart System</button>
            </div>
          </div>
          <div class="health-indicators">
            <div class="health-item healthy">
              <div class="health-icon">💚</div>
              <div class="health-info">
                <span class="health-name">Database Connection</span>
                <span class="health-status">Healthy</span>
              </div>
            </div>
            <div class="health-item healthy">
              <div class="health-icon">💚</div>
              <div class="health-info">
                <span class="health-name">WebSocket Services</span>
                <span class="health-status">Connected</span>
              </div>
            </div>
            <div class="health-item healthy">
              <div class="health-icon">💚</div>
              <div class="health-info">
                <span class="health-name">API Gateway</span>
                <span class="health-status">Responsive</span>
              </div>
            </div>
            <div class="health-item warning">
              <div class="health-icon">⚠️</div>
              <div class="health-info">
                <span class="health-name">Storage Space</span>
                <span class="health-status">78% Used</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>
  </div>
</template><script>
import { mapState, mapActions } from 'pinia'
import { useRobotsStore } from '@/stores/robots'
import { useAuthStore } from '@/stores/auth'

export default {
  name: 'AdminDashboard',
  data() {
    return {
      recentLogs: [
        { id: 1, timestamp: new Date(), robotId: 'ART-001', level: 'INFO', message: 'System initialized successfully' },
        { id: 2, timestamp: new Date(Date.now() - 60000), robotId: 'ART-002', level: 'WARNING', message: 'Battery level below 25%' },
        { id: 3, timestamp: new Date(Date.now() - 120000), robotId: 'ART-003', level: 'INFO', message: 'Navigation route completed' },
        { id: 4, timestamp: new Date(Date.now() - 180000), robotId: 'ART-001', level: 'INFO', message: 'Software update applied' },
        { id: 5, timestamp: new Date(Date.now() - 240000), robotId: 'ART-004', level: 'ERROR', message: 'Connection timeout detected' }
      ]
    }
  },  computed: {
    ...mapState(useRobotsStore, ['robots', 'isLoading']),
    ...mapState(useAuthStore, ['isAuthenticated']),
    robotsList() {
      return Object.values(this.robots || {})
    },
    safeRobots() {
      return Array.isArray(this.robotsList) ? this.robotsList : []
    },
    activeRobotsCount() {
      return this.safeRobots.filter(robot => robot.status === 'ACTIVE').length
    },
    idleRobotsCount() {
      return this.safeRobots.filter(robot => robot.status === 'IDLE').length
    },
    offlineRobotsCount() {
      return this.safeRobots.filter(robot => robot.status === 'OFFLINE').length
    }
  },methods: {
    ...mapActions(useRobotsStore, ['sendCommand', 'fetchRobots']),
    ...mapActions(useAuthStore, ['logout']),
    formatTime(timestamp) {
      return new Date(timestamp).toLocaleTimeString()
    },
    handleLogout() {
      this.logout()
      this.$router.push('/')
    },
    viewLogs(robotId) {
      this.$router.push(`/logs/${robotId}`)
    },
    configureRobot(robotId) {
      alert(`Configure robot ${robotId} - Feature coming soon!`)
    },    deleteRobot(robotId) {
      if (confirm(`Are you sure you want to delete robot ${robotId}?`)) {
        alert(`Delete robot ${robotId} - Feature coming soon!`)
      }
    },
    // Admin-only methods
    exportLogs() {
      alert('Exporting system logs... Feature coming soon!')
    },
    clearLogs() {
      if (confirm('Are you sure you want to clear all logs? This action cannot be undone.')) {
        alert('Clearing logs... Feature coming soon!')
      }
    },
    viewLogDetails(logId) {
      alert(`Viewing details for log ${logId} - Feature coming soon!`)
    },
    runDiagnostics() {
      alert('Running system diagnostics... Feature coming soon!')
    },
    restartSystem() {
      if (confirm('Are you sure you want to restart the entire system? This will temporarily interrupt all robot operations.')) {
        alert('System restart initiated... Feature coming soon!')
      }
    }
  },
  async mounted() {
    await this.fetchRobots()
  }
}
</script>

<style scoped>
/* Modern CSS Variables */
:root {
  --primary-blue: #2563eb;
  --primary-blue-dark: #1d4ed8;
  --primary-blue-light: #3b82f6;
  --success-green: #10b981;
  --success-green-light: #34d399;
  --warning-orange: #f59e0b;
  --warning-orange-light: #fbbf24;
  --danger-red: #ef4444;
  --danger-red-light: #f87171;
  --neutral-50: #f9fafb;
  --neutral-100: #f3f4f6;
  --neutral-200: #e5e7eb;
  --neutral-300: #d1d5db;
  --neutral-400: #9ca3af;
  --neutral-500: #6b7280;
  --neutral-600: #4b5563;
  --neutral-700: #374151;
  --neutral-800: #1f2937;
  --neutral-900: #111827;
  --glass-bg: rgba(255, 255, 255, 0.85);
  --glass-border: rgba(255, 255, 255, 0.2);
  --shadow-sm: 0 1px 3px 0 rgba(0, 0, 0, 0.1), 0 1px 2px 0 rgba(0, 0, 0, 0.06);
  --shadow-md: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
  --shadow-lg: 0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05);
  --shadow-xl: 0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04);
}

.admin-dashboard {
  min-height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 0;
  font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
}

/* Header Styles */
.dashboard-header {
  background: var(--glass-bg);
  backdrop-filter: blur(20px);
  border-bottom: 1px solid var(--glass-border);
  padding: 1.5rem 0;
  position: sticky;
  top: 0;
  z-index: 100;
}

.header-content {
  max-width: 1400px;
  margin: 0 auto;
  padding: 0 2rem;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.brand-section {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.logo-icon {
  font-size: 3rem;
  background: linear-gradient(135deg, #fbbf24, #f59e0b);
  background-clip: text;
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  filter: drop-shadow(0 2px 4px rgba(0,0,0,0.1));
}

.brand-text h1 {
  font-size: 2rem;
  font-weight: 800;
  background: linear-gradient(135deg, var(--neutral-800), var(--neutral-600));
  background-clip: text;
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  margin: 0;
  line-height: 1.2;
}

.brand-text p {
  font-size: 0.875rem;
  color: var(--neutral-500);
  margin: 0;
  font-weight: 500;
}

.header-actions {
  display: flex;
  align-items: center;
  gap: 1.5rem;
}

.user-profile {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.avatar {
  width: 2.5rem;
  height: 2.5rem;
  background: linear-gradient(135deg, var(--primary-blue), var(--primary-blue-light));
  color: white;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 600;
  font-size: 0.875rem;
  box-shadow: var(--shadow-md);
}

.avatar.admin {
  background: linear-gradient(135deg, #fbbf24, #f59e0b);
}

.user-details {
  display: flex;
  flex-direction: column;
}

.user-name {
  font-weight: 600;
  color: var(--neutral-800);
  font-size: 0.875rem;
}

.user-role {
  font-size: 0.75rem;
  color: var(--neutral-500);
}

.logout-btn {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  background: var(--danger-red);
  color: white;
  border: none;
  padding: 0.75rem 1.25rem;
  border-radius: 0.75rem;
  cursor: pointer;
  font-weight: 600;
  font-size: 0.875rem;
  transition: all 0.2s ease;
  box-shadow: var(--shadow-sm);
}

.logout-btn:hover {
  background: var(--danger-red-light);
  transform: translateY(-1px);
  box-shadow: var(--shadow-md);
}

.logout-icon {
  font-size: 1rem;
}

/* Status Overview */
.status-overview {
  max-width: 1400px;
  margin: 0 auto;
  padding: 2rem;
}

.status-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 1.5rem;
}

.status-card {
  background: var(--glass-bg);
  backdrop-filter: blur(20px);
  border: 1px solid var(--glass-border);
  border-radius: 1.25rem;
  padding: 2rem;
  box-shadow: var(--shadow-lg);
  transition: all 0.3s ease;
  position: relative;
  overflow: hidden;
  display: flex;
  align-items: center;
  gap: 1.5rem;
}

.status-card::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 4px;
  background: linear-gradient(90deg, var(--primary-blue), var(--primary-blue-light));
}

.status-card.system-performance::before {
  background: linear-gradient(90deg, #fbbf24, #f59e0b);
}

.status-card.total-robots::before {
  background: linear-gradient(90deg, #fbbf24, #f59e0b);
}

.status-card.active-sessions::before {
  background: linear-gradient(90deg, #fbbf24, #f59e0b);
}

.status-card.data-throughput::before {
  background: linear-gradient(90deg, #fbbf24, #f59e0b);
}

.status-card:hover {
  transform: translateY(-4px);
  box-shadow: var(--shadow-xl);
  border-color: rgba(255, 255, 255, 0.4);
}

.card-icon {
  font-size: 3rem;
  filter: drop-shadow(0 2px 4px rgba(0,0,0,0.1));
}

.card-content h3 {
  font-size: 0.875rem;
  font-weight: 600;
  color: var(--neutral-600);
  margin: 0 0 0.5rem 0;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.status-number {
  font-size: 2.5rem;
  font-weight: 800;
  color: var(--neutral-800);
  margin: 0 0 0.25rem 0;
  line-height: 1;
}

.status-subtitle {
  font-size: 0.75rem;
  color: var(--neutral-500);
  margin: 0;
}

/* Section Headers */
.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 2rem;
}

.section-header h2 {
  font-size: 1.5rem;
  font-weight: 700;
  color: white;
  margin: 0;
  text-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.header-controls {
  display: flex;
  flex-direction: column;
  gap: 1rem;
  align-items: flex-end;
}

.fleet-summary {
  display: flex;
  gap: 1rem;
  align-items: center;
}

.summary-item {
  padding: 0.5rem 1rem;
  border-radius: 2rem;
  font-size: 0.75rem;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  transition: all 0.2s ease;
}

.summary-item:hover {
  transform: translateY(-1px);
  box-shadow: var(--shadow-md);
}

.summary-item.active {
  background: rgba(16, 185, 129, 0.2);
  color: var(--success-green-light);
  border: 1px solid rgba(16, 185, 129, 0.3);
}

.summary-item.idle {
  background: rgba(245, 158, 11, 0.2);
  color: var(--warning-orange-light);
  border: 1px solid rgba(245, 158, 11, 0.3);
}

.summary-item.offline {
  background: rgba(239, 68, 68, 0.2);
  color: var(--danger-red-light);
  border: 1px solid rgba(239, 68, 68, 0.3);
}

.fleet-actions {
  display: flex;
  gap: 1rem;
}

/* Robots Section */
.robots-section {
  max-width: 1400px;
  margin: 0 auto;
  padding: 0 2rem 2rem;
}

.robots-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(450px, 1fr));
  gap: 2rem;
}

.robot-card {
  background: var(--glass-bg);
  backdrop-filter: blur(20px);
  border: 1px solid var(--glass-border);
  border-radius: 1.5rem;
  padding: 2rem;
  box-shadow: var(--shadow-lg);
  transition: all 0.3s ease;
  position: relative;
  overflow: hidden;
}

.robot-card::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 4px;
}

.robot-card.active::before {
  background: linear-gradient(90deg, var(--success-green), var(--success-green-light));
}

.robot-card.idle::before {
  background: linear-gradient(90deg, var(--warning-orange), var(--warning-orange-light));
}

.robot-card.offline::before {
  background: linear-gradient(90deg, var(--neutral-400), var(--neutral-500));
}

.robot-card:hover {
  transform: translateY(-2px);
  box-shadow: var(--shadow-xl);
  border-color: rgba(255, 255, 255, 0.4);
}

.robot-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.5rem;
}

.robot-identity {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.robot-avatar {
  width: 3rem;
  height: 3rem;
  background: linear-gradient(135deg, var(--primary-blue), var(--primary-blue-light));
  color: white;
  border-radius: 1rem;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 700;
  font-size: 0.875rem;
  box-shadow: var(--shadow-md);
}

.robot-info h3 {
  font-size: 1.25rem;
  font-weight: 700;
  color: var(--neutral-800);
  margin: 0;
}

.robot-location {
  font-size: 0.875rem;
  color: var(--neutral-500);
  margin: 0.25rem 0 0 0;
}

.robot-id {
  font-size: 0.75rem;
  color: var(--neutral-400);
  margin: 0.125rem 0 0 0;
  font-family: monospace;
}

.robot-status-badge {
  padding: 0.5rem 1rem;
  border-radius: 2rem;
  font-size: 0.75rem;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.status-dot {
  width: 0.5rem;
  height: 0.5rem;
  border-radius: 50%;
}

.robot-status-badge.active {
  background: rgba(16, 185, 129, 0.1);
  color: var(--success-green);
  border: 1px solid rgba(16, 185, 129, 0.2);
}

.robot-status-badge.active .status-dot {
  background: var(--success-green);
}

.robot-status-badge.idle {
  background: rgba(245, 158, 11, 0.1);
  color: var(--warning-orange);
  border: 1px solid rgba(245, 158, 11, 0.2);
}

.robot-status-badge.idle .status-dot {
  background: var(--warning-orange);
}

.robot-status-badge.offline {
  background: rgba(107, 114, 128, 0.1);
  color: var(--neutral-500);
  border: 1px solid rgba(107, 114, 128, 0.2);
}

.robot-status-badge.offline .status-dot {
  background: var(--neutral-500);
}

.robot-metrics {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1rem;
  margin-bottom: 1.5rem;
}

.metric-card {
  background: rgba(255, 255, 255, 0.5);
  border: 1px solid rgba(255, 255, 255, 0.3);
  border-radius: 1rem;
  padding: 1rem;
  display: flex;
  align-items: center;
  gap: 0.75rem;
  transition: all 0.2s ease;
}

.metric-card:hover {
  background: rgba(255, 255, 255, 0.7);
  transform: translateY(-1px);
}

.metric-icon {
  font-size: 1.5rem;
}

.metric-info {
  flex: 1;
}

.metric-label {
  display: block;
  font-size: 0.75rem;
  color: var(--neutral-500);
  font-weight: 500;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.metric-value {
  display: block;
  font-size: 1rem;
  font-weight: 700;
  color: var(--neutral-800);
}

.battery-bar {
  width: 100%;
  height: 0.25rem;
  background: var(--neutral-200);
  border-radius: 0.125rem;
  overflow: hidden;
  margin-top: 0.5rem;
}

.battery-fill {
  height: 100%;
  background: linear-gradient(90deg, var(--success-green), var(--success-green-light));
  transition: width 0.3s ease;
}

.metric-card.battery.low .battery-fill {
  background: linear-gradient(90deg, var(--warning-orange), var(--warning-orange-light));
}

.metric-card.battery.critical .battery-fill {
  background: linear-gradient(90deg, var(--danger-red), var(--danger-red-light));
}

.robot-actions {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.robot-actions.admin .secondary-actions {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 0.75rem;
}

.primary-actions {
  display: flex;
  gap: 0.75rem;
}

.secondary-actions {
  display: flex;
  gap: 0.75rem;
  flex-wrap: wrap;
}

.action-btn {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.75rem 1rem;
  border: none;
  border-radius: 0.75rem;
  cursor: pointer;
  font-weight: 600;
  font-size: 0.875rem;
  transition: all 0.2s ease;
  justify-content: center;
}

.action-btn.primary {
  background: linear-gradient(135deg, var(--primary-blue), var(--primary-blue-light));
  color: white;
  box-shadow: var(--shadow-sm);
}

.action-btn.primary:hover {
  transform: translateY(-1px);
  box-shadow: var(--shadow-md);
}

.action-btn.secondary {
  background: rgba(255, 255, 255, 0.7);
  color: var(--neutral-700);
  border: 1px solid rgba(255, 255, 255, 0.3);
}

.action-btn.secondary:hover {
  background: rgba(255, 255, 255, 0.9);
  transform: translateY(-1px);
}

.action-btn.secondary-btn {
  background: rgba(255, 255, 255, 0.7);
  color: var(--neutral-700);
  border: 1px solid rgba(255, 255, 255, 0.3);
}

.action-btn.secondary-btn:hover:not(:disabled) {
  background: rgba(255, 255, 255, 0.9);
  transform: translateY(-1px);
}

.action-btn.danger-btn {
  background: linear-gradient(135deg, var(--danger-red), var(--danger-red-light));
  color: white;
}

.action-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
  transform: none !important;
}

.primary-btn {
  flex: 1;
}

.primary-btn.start-btn {
  background: linear-gradient(135deg, var(--success-green), var(--success-green-light));
}

.primary-btn.stop-btn {
  background: linear-gradient(135deg, var(--danger-red), var(--danger-red-light));
}

.btn-icon {
  font-size: 1rem;
}

/* Responsive Design */
@media (max-width: 1024px) {
  .robots-grid {
    grid-template-columns: repeat(auto-fill, minmax(400px, 1fr));
  }
}

@media (max-width: 768px) {
  .header-content {
    flex-direction: column;
    gap: 1rem;
    text-align: center;
    padding: 0 1rem;
  }
  
  .status-overview,
  .robots-section {
    padding: 1rem;
  }
  
  .status-grid {
    grid-template-columns: 1fr;
  }
  
  .robots-grid {
    grid-template-columns: 1fr;
  }
  
  .robot-metrics {
    grid-template-columns: 1fr;
  }
    .fleet-actions {
    flex-direction: column;
  }
  
  .header-controls {
    align-items: center;
    gap: 1.5rem;
  }
  
  .fleet-summary {
    flex-wrap: wrap;
    justify-content: center;
  }
}

@media (max-width: 480px) {
  .brand-text h1 {
    font-size: 1.5rem;
  }
  
  .logo-icon {
    font-size: 2rem;
  }
    .user-profile {
    flex-direction: column;
    gap: 0.5rem;
  }
}

/* Activity Section */
.activity-section {
  max-width: 1400px;
  margin: 0 auto;
  padding: 0 2rem 2rem;
}

.admin-controls {
  display: flex;
  gap: 1rem;
  align-items: center;
}

.activity-feed {
  background: var(--glass-bg);
  backdrop-filter: blur(20px);
  border: 1px solid var(--glass-border);
  border-radius: 1.5rem;
  padding: 1.5rem;
  max-height: 400px;
  overflow-y: auto;
}

.activity-item {
  display: flex;
  align-items: center;
  gap: 1rem;
  padding: 1rem;
  background: rgba(255, 255, 255, 0.5);
  border: 1px solid rgba(255, 255, 255, 0.3);
  border-radius: 1rem;
  margin-bottom: 0.75rem;
  transition: all 0.2s ease;
}

.activity-item:hover {
  background: rgba(255, 255, 255, 0.7);
  transform: translateY(-1px);
}

.activity-item:last-child {
  margin-bottom: 0;
}

.activity-icon {
  font-size: 1.5rem;
  width: 2.5rem;
  height: 2.5rem;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.7);
}

.activity-content {
  flex: 1;
}

.activity-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 0.25rem;
}

.activity-robot {
  font-weight: 600;
  color: var(--primary-blue);
  font-size: 0.875rem;
}

.activity-time {
  font-size: 0.75rem;
  color: var(--neutral-500);
}

.activity-message {
  font-size: 0.875rem;
  color: var(--neutral-700);
  margin: 0;
}

.activity-actions {
  display: flex;
  gap: 0.5rem;
}

.action-btn.tiny {
  padding: 0.5rem 0.75rem;
  font-size: 0.75rem;
}

.view-all-btn {
  background: var(--primary-blue);
  color: white;
  border: none;
  padding: 0.5rem 1rem;
  border-radius: 0.5rem;
  cursor: pointer;
  font-weight: 500;
  font-size: 0.875rem;
  transition: all 0.2s ease;
}

.view-all-btn:hover {
  background: var(--primary-blue-dark);
  transform: translateY(-1px);
}

/* Analytics Section */
.analytics-section {
  max-width: 1400px;
  margin: 0 auto;
  padding: 0 2rem 2rem;
}

.analytics-controls {
  display: flex;
  gap: 1rem;
  align-items: center;
}

.time-filter {
  padding: 0.5rem 1rem;
  border: 1px solid rgba(255, 255, 255, 0.3);
  border-radius: 0.5rem;
  background: rgba(255, 255, 255, 0.7);
  backdrop-filter: blur(10px);
  color: var(--neutral-700);
  font-weight: 500;
  cursor: pointer;
  outline: none;
}

.analytics-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 2rem;
}

.analytics-card {
  background: var(--glass-bg);
  backdrop-filter: blur(20px);
  border: 1px solid var(--glass-border);
  border-radius: 1.5rem;
  padding: 2rem;
  box-shadow: var(--shadow-lg);
  transition: all 0.3s ease;
}

.analytics-card.full-width {
  grid-column: 1 / -1;
}

.analytics-card:hover {
  transform: translateY(-2px);
  box-shadow: var(--shadow-xl);
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.5rem;
}

.card-header h3 {
  font-size: 1.125rem;
  font-weight: 700;
  color: var(--neutral-800);
  margin: 0;
}

.status-indicator {
  padding: 0.25rem 0.75rem;
  border-radius: 1rem;
  font-size: 0.75rem;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.status-indicator.healthy {
  background: rgba(16, 185, 129, 0.1);
  color: var(--success-green);
  border: 1px solid rgba(16, 185, 129, 0.2);
}

.status-indicator.active {
  background: rgba(37, 99, 235, 0.1);
  color: var(--primary-blue);
  border: 1px solid rgba(37, 99, 235, 0.2);
}

.metrics-list {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.metric-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.75rem;
  background: rgba(255, 255, 255, 0.5);
  border-radius: 0.75rem;
  transition: all 0.2s ease;
}

.metric-row:hover {
  background: rgba(255, 255, 255, 0.7);
}

.metric-label {
  font-size: 0.875rem;
  color: var(--neutral-600);
  font-weight: 500;
}

.metric-value {
  font-size: 0.875rem;
  color: var(--neutral-800);
  font-weight: 700;
}

.stats-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1rem;
}

.stat-item {
  text-align: center;
  padding: 1rem;
  background: rgba(255, 255, 255, 0.5);
  border-radius: 1rem;
  transition: all 0.2s ease;
}

.stat-item:hover {
  background: rgba(255, 255, 255, 0.7);
  transform: translateY(-1px);
}

.stat-number {
  font-size: 1.5rem;
  font-weight: 800;
  color: var(--primary-blue);
  margin-bottom: 0.25rem;
}

.stat-label {
  font-size: 0.75rem;
  color: var(--neutral-500);
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.health-controls {
  display: flex;
  gap: 0.75rem;
}

.health-indicators {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 1rem;
}

.health-item {
  display: flex;
  align-items: center;
  gap: 1rem;
  padding: 1rem;
  background: rgba(255, 255, 255, 0.5);
  border-radius: 1rem;
  transition: all 0.2s ease;
}

.health-item:hover {
  background: rgba(255, 255, 255, 0.7);
}

.health-item.healthy {
  border-left: 4px solid var(--success-green);
}

.health-item.warning {
  border-left: 4px solid var(--warning-orange);
}

.health-item.error {
  border-left: 4px solid var(--danger-red);
}

.health-icon {
  font-size: 1.5rem;
}

.health-info {
  flex: 1;
}

.health-name {
  display: block;
  font-weight: 600;
  color: var(--neutral-800);
  font-size: 0.875rem;
}

.health-status {
  display: block;
  font-size: 0.75rem;
  color: var(--neutral-500);  margin-top: 0.125rem;
}

/* Loading and Empty States */
.loading-state,
.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 4rem 2rem;
  text-align: center;
  background: var(--glass-bg);
  backdrop-filter: blur(20px);
  border: 1px solid var(--glass-border);
  border-radius: 1.5rem;
  margin: 2rem 0;
}

.loading-spinner,
.empty-icon {
  font-size: 4rem;
  margin-bottom: 1rem;
  animation: pulse 2s infinite;
}

.empty-state h3 {
  font-size: 1.5rem;
  font-weight: 700;
  color: var(--neutral-800);
  margin: 0 0 0.5rem 0;
}

.empty-state p,
.loading-state p {
  font-size: 1rem;
  color: var(--neutral-500);
  margin: 0;
}

@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.5; }
}

/* Enhanced Responsive Design */
@media (max-width: 1024px) {
  .analytics-grid {
    grid-template-columns: 1fr;
  }
  
  .stats-grid {
    grid-template-columns: 1fr 1fr;
  }
  
  .health-indicators {
    grid-template-columns: 1fr 1fr;
  }
}

@media (max-width: 768px) {
  .admin-controls {
    flex-direction: column;
    gap: 0.5rem;
  }
  
  .analytics-controls {
    flex-direction: column;
  }
  
  .card-header {
    flex-direction: column;
    gap: 1rem;
    align-items: flex-start;
  }
  
  .health-controls {
    flex-direction: column;
    gap: 0.5rem;
  }
  
  .stats-grid {
    grid-template-columns: 1fr;
  }
  
  .health-indicators {
    grid-template-columns: 1fr;
  }
}
</style>
