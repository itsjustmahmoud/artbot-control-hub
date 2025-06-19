<template>
  <div class="robot-card" :class="[robot.status.toLowerCase(), { 'low-battery': robot.battery < 20 }, variant]">
    <div class="robot-header">
      <div class="robot-identity">
        <div class="robot-avatar">{{ robot.name ? robot.name.slice(-3) : '???' }}</div>
        <div class="robot-info">
          <h3>{{ robot.name || 'Unknown Robot' }}</h3>
          <p class="robot-location">📍 {{ robot.location || 'Unknown Location' }}</p>
          <p class="robot-id" v-if="showId">ID: {{ robot.id }}</p>
        </div>
      </div>
      <div class="robot-status-badge" :class="robot.status.toLowerCase()">
        <div class="status-dot"></div>
        {{ robot.status }}
      </div>
    </div>
    
    <div class="robot-metrics">
      <MetricCard
        icon="🔋"
        label="Battery"
        :value="`${robot.battery || 0}%`"
        :class="{ 'low': robot.battery < 20, 'critical': robot.battery < 10 }"
      >
        <div class="battery-bar">
          <div class="battery-fill" :style="{ width: (robot.battery || 0) + '%' }"></div>
        </div>
      </MetricCard>
      
      <MetricCard
        icon="⏰"
        label="Last Seen"
        :value="formatTime(robot.lastSeen || robot.last_update)"
      />
      
      <MetricCard
        v-if="showAdvancedMetrics"
        icon="💻"
        label="CPU Usage"
        :value="`${robot.cpu_usage || Math.floor(Math.random() * 40 + 20)}%`"
      />
      
      <MetricCard
        v-if="showAdvancedMetrics"
        icon="🧠"
        label="Memory"
        :value="`${robot.memory_usage || Math.floor(Math.random() * 60 + 30)}%`"
      />
    </div>

    <div class="robot-actions" :class="variant">
      <div class="primary-actions">
        <button 
          @click="$emit('send-command', robot.id, 'start')" 
          :disabled="robot.status === 'OFFLINE'" 
          class="action-btn primary-btn start-btn"
        >
          <span class="btn-icon">▶️</span>
          Start
        </button>
        <button 
          @click="$emit('send-command', robot.id, 'stop')" 
          :disabled="robot.status === 'OFFLINE'" 
          class="action-btn primary-btn stop-btn"
        >
          <span class="btn-icon">⏸️</span>
          Stop
        </button>
      </div>
      
      <div v-if="showAdvancedActions" class="secondary-actions">
        <button 
          @click="$emit('send-command', robot.id, 'reboot')" 
          :disabled="robot.status === 'OFFLINE'" 
          class="action-btn secondary-btn"
        >
          <span class="btn-icon">🔄</span>
          Reboot
        </button>
        <button @click="$emit('configure', robot.id)" class="action-btn secondary-btn">
          <span class="btn-icon">⚙️</span>
          Configure
        </button>
        <button @click="$emit('view-logs', robot.id)" class="action-btn secondary-btn">
          <span class="btn-icon">📊</span>
          Logs
        </button>
        <button @click="$emit('delete', robot.id)" class="action-btn danger-btn">
          <span class="btn-icon">🗑️</span>
          Delete
        </button>
      </div>
    </div>
  </div>
</template>

<script>
import MetricCard from './MetricCard.vue'

export default {
  name: 'RobotCard',
  components: {
    MetricCard
  },
  props: {
    robot: {
      type: Object,
      required: true
    },
    variant: {
      type: String,
      default: 'museum',
      validator: value => ['admin', 'museum'].includes(value)
    }
  },
  computed: {
    showId() {
      return this.variant === 'admin'
    },
    showAdvancedMetrics() {
      return this.variant === 'admin'
    },
    showAdvancedActions() {
      return this.variant === 'admin'
    }
  },
  methods: {
    formatTime(timestamp) {
      if (!timestamp) return 'Unknown'
      return new Date(timestamp).toLocaleTimeString()
    }
  },
  emits: ['send-command', 'configure', 'view-logs', 'delete']
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
  background: linear-gradient(90deg, var(--neutral-400), var(--neutral-500));
}

.robot-card:hover {
  transform: translateY(-2px);
  box-shadow: var(--shadow-xl);
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
  background: var(--neutral-500);
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
}

.action-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.action-btn.primary-btn {
  flex: 1;
}

.action-btn.primary-btn.start-btn {
  background: linear-gradient(135deg, var(--success-green), var(--success-green-light));
  color: white;
}

.action-btn.primary-btn.stop-btn {
  background: linear-gradient(135deg, var(--danger-red), var(--danger-red-light));
  color: white;
}

.action-btn.secondary-btn {
  background: rgba(255, 255, 255, 0.7);
  color: var(--neutral-700);
  border: 1px solid rgba(255, 255, 255, 0.3);
}

.action-btn.danger-btn {
  background: rgba(239, 68, 68, 0.1);
  color: var(--danger-red);
  border: 1px solid rgba(239, 68, 68, 0.2);
}

.action-btn:hover:not(:disabled) {
  transform: translateY(-1px);
  box-shadow: var(--shadow-md);
}

.btn-icon {
  font-size: 1rem;
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

.robot-card.low-battery .battery-fill {
  background: linear-gradient(90deg, var(--warning-orange), var(--warning-orange-light));
}

.robot-card.critical .battery-fill {
  background: linear-gradient(90deg, var(--danger-red), var(--danger-red-light));
}

/* Responsive Design */
@media (max-width: 768px) {
  .robot-metrics {
    grid-template-columns: 1fr;
  }
  
  .primary-actions,
  .secondary-actions {
    flex-direction: column;
  }
}
</style>
