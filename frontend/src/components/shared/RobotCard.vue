<template>
  <div 
    class="robot-card"
    :class="[
      robot.status?.toLowerCase(), 
      { 'low-battery': robot.battery < 20 },
      mode
    ]"
  >
    <div class="robot-header">
      <div class="robot-identity">
        <div class="robot-avatar">{{ robot.name?.slice(-3) || 'BOT' }}</div>
        <div class="robot-info">
          <h3>{{ robot.name || 'Unknown Robot' }}</h3>
          <p class="robot-location">📍 {{ robot.location || 'Unknown' }}</p>
          <p class="robot-id">ID: {{ robot.id }}</p>
        </div>
      </div>
      <div class="robot-status-badge" :class="robot.status?.toLowerCase()">
        <div class="status-dot"></div>
        {{ robot.status || 'UNKNOWN' }}
      </div>
    </div>
      <div class="robot-metrics">
      <!-- Essential Metrics: Battery Level -->
      <div class="metric-card battery" :class="{ 'low': robot.battery_level < 20, 'critical': robot.battery_level < 10 }">
        <div class="metric-icon">🔋</div>
        <div class="metric-info">
          <span class="metric-label">Battery</span>
          <span class="metric-value">{{ robot.battery_level || 0 }}%</span>
        </div>
        <div class="battery-bar">
          <div class="battery-fill" :style="{ width: (robot.battery_level || 0) + '%' }"></div>
        </div>
      </div>
      
      <!-- Essential Metrics: CPU & Temperature -->
      <div class="metric-card cpu-temp">
        <div class="metric-icon">🌡️</div>
        <div class="metric-info">
          <span class="metric-label">CPU / Temp</span>
          <span class="metric-value">{{ robot.cpu_usage || 0 }}% / {{ robot.temperature || 0 }}°C</span>
        </div>
      </div>
      
      <!-- Essential Metrics: Memory Usage -->
      <div class="metric-card memory">
        <div class="metric-icon">🧠</div>
        <div class="metric-info">
          <span class="metric-label">Memory</span>
          <span class="metric-value">{{ robot.memory_usage || 0 }}%</span>
        </div>
      </div>
      
      <!-- Essential Metrics: Connectivity Status -->
      <div class="metric-card connectivity">
        <div class="metric-icon">�</div>
        <div class="metric-info">
          <span class="metric-label">Connectivity</span>
          <div class="connectivity-status">
            <span class="status-item" :class="{ 'connected': robot.oak_camera_connected }">
              📷 {{ robot.oak_camera_connected ? 'OAK' : 'No OAK' }}
            </span>
            <span class="status-item" :class="{ 'connected': robot.create3_connected }">
              🤖 {{ robot.create3_connected ? 'Create3' : 'No Create3' }}
            </span>
          </div>
        </div>
      </div>
      
      <!-- Essential Metrics: Workspace Status -->
      <div class="metric-card workspace">
        <div class="metric-icon">⚙️</div>
        <div class="metric-info">
          <span class="metric-label">Workspace</span>
          <span class="metric-value" :class="robot.workspace_status">
            {{ robot.workspace_status === 'running' ? '▶️ Running' : '⏸️ Stopped' }}
          </span>
        </div>
      </div>
      
      <!-- Essential Metrics: Uptime -->
      <div class="metric-card uptime">
        <div class="metric-icon">⏰</div>
        <div class="metric-info">
          <span class="metric-label">Uptime</span>
          <span class="metric-value">{{ formatUptime(robot.uptime_seconds) }}</span>
        </div>
      </div>
    </div>    <div class="robot-actions" :class="mode">
      <!-- Museum Staff & Admin: Workspace Controls -->
      <div class="primary-actions">
        <button 
          @click="$emit('workspace-start', robot.id)" 
          :disabled="robot.status === 'OFFLINE' || robot.workspace_status === 'running'"
          class="action-btn primary-btn start-btn"
        >
          <span class="btn-icon">▶️</span>
          Start Workspace
        </button>
        <button 
          @click="$emit('workspace-stop', robot.id)" 
          :disabled="robot.status === 'OFFLINE' || robot.workspace_status === 'stopped'"
          class="action-btn primary-btn stop-btn"
        >
          <span class="btn-icon">⏸️</span>
          Stop Workspace
        </button>
      </div>
      
      <!-- Admin Only: Advanced Controls -->
      <div v-if="mode === 'admin'" class="secondary-actions">
        <button 
          @click="$emit('restart-create3', robot.id)" 
          :disabled="robot.status === 'OFFLINE' || !robot.create3_connected"
          class="action-btn secondary-btn"
        >
          <span class="btn-icon">🔄</span>
          Restart Create3
        </button>
        <button 
          @click="$emit('reboot-create3', robot.id)" 
          :disabled="robot.status === 'OFFLINE' || !robot.create3_connected"
          class="action-btn secondary-btn"
        >
          <span class="btn-icon">�</span>
          Reboot Create3
        </button>
        <button 
          @click="$emit('view-workspace-logs', robot.id)" 
          :disabled="robot.status === 'OFFLINE'"
          class="action-btn secondary-btn"
        >
          <span class="btn-icon">📋</span>
          Workspace Logs        </button>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'RobotCard',
  props: {
    robot: {
      type: Object,
      required: true
    },
    mode: {
      type: String,
      default: 'museum', // 'admin' or 'museum'
      validator: value => ['admin', 'museum'].includes(value)
    }
  },  methods: {
    formatTime(timestamp) {
      if (!timestamp) return 'Never'
      return new Date(timestamp).toLocaleTimeString()
    },
    
    formatUptime(seconds) {
      if (!seconds || seconds === 0) return '0m'
      
      const hours = Math.floor(seconds / 3600)
      const minutes = Math.floor((seconds % 3600) / 60)
      
      if (hours > 0) {
        return `${hours}h ${minutes}m`
      } else {
        return `${minutes}m`
      }
    }
  }
}
</script>

<style scoped>
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
  background: linear-gradient(90deg, var(--danger-red), var(--danger-red-light));
}

.robot-card:hover {
  transform: translateY(-2px);
}

.robot-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
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
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 700;
  font-size: 0.875rem;
  box-shadow: var(--shadow-sm);
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
  background: var(--neutral-500);
}

.robot-status-badge.active {
  background: rgba(16, 185, 129, 0.2);
  color: var(--success-green);
  border: 1px solid rgba(16, 185, 129, 0.3);
}

.robot-status-badge.active .status-dot {
  background: var(--success-green);
}

.robot-status-badge.idle {
  background: rgba(245, 158, 11, 0.2);
  color: var(--warning-orange);
  border: 1px solid rgba(245, 158, 11, 0.3);
}

.robot-status-badge.idle .status-dot {
  background: var(--warning-orange);
}

.robot-status-badge.offline {
  background: rgba(239, 68, 68, 0.2);
  color: var(--danger-red);
  border: 1px solid rgba(239, 68, 68, 0.3);
}

.robot-status-badge.offline .status-dot {
  background: var(--danger-red);
}

.robot-metrics {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
  gap: 1rem;
  margin: 1.5rem 0;
}

.robot-card.admin .robot-metrics {
  grid-template-columns: 1fr 1fr;
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

.primary-actions,
.secondary-actions {
  display: flex;
  gap: 0.75rem;
}

.robot-actions.admin .secondary-actions {
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
  text-decoration: none;
}

.action-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.action-btn:disabled:hover {
  transform: none;
}

.primary-btn {
  flex: 1;
  color: white;
  box-shadow: var(--shadow-sm);
}

.primary-btn:hover:not(:disabled) {
  transform: translateY(-1px);
  box-shadow: var(--shadow-md);
}

.primary-btn.start-btn {
  background: linear-gradient(135deg, var(--success-green), var(--success-green-light));
}

.primary-btn.stop-btn {
  background: linear-gradient(135deg, var(--danger-red), var(--danger-red-light));
}

.secondary-btn {
  background: rgba(255, 255, 255, 0.7);
  color: var(--neutral-700);
  border: 1px solid var(--glass-border);
}

.secondary-btn:hover:not(:disabled) {
  background: rgba(255, 255, 255, 0.9);
  transform: translateY(-1px);
}

.danger-btn {
  background: rgba(239, 68, 68, 0.1);
  color: var(--danger-red);
  border: 1px solid rgba(239, 68, 68, 0.2);
}

.danger-btn:hover:not(:disabled) {
  background: rgba(239, 68, 68, 0.2);
  transform: translateY(-1px);
}

.btn-icon {
  font-size: 1rem;
}

/* New metric card styles for essential data */
.connectivity-status {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.status-item {
  font-size: 0.75rem;
  color: var(--danger-red);
  font-weight: 500;
}

.status-item.connected {
  color: var(--success-green);
}

.metric-card.cpu-temp .metric-value {
  font-size: 0.875rem;
}

.metric-card.workspace .metric-value.running {
  color: var(--success-green);
  font-weight: 600;
}

.metric-card.workspace .metric-value.stopped {
  color: var(--warning-orange);
  font-weight: 600;
}

/* Responsive Design */
@media (max-width: 768px) {
  .robot-card {
    padding: 1.5rem;
  }
  
  .robot-header {
    flex-direction: column;
    gap: 1rem;
    align-items: flex-start;
  }
  
  .robot-metrics {
    grid-template-columns: 1fr;
  }
  
  .primary-actions,
  .secondary-actions {
    flex-direction: column;
  }
}
</style>
