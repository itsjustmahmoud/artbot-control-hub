<template>
  <section class="robots-section">
    <div class="section-header">
      <h2>{{ title }}</h2>
      <div class="header-controls">
        <div class="fleet-summary">
          <span class="summary-item active">{{ activeCount }} Active</span>
          <span class="summary-item idle">{{ idleCount }} Idle</span>
          <span class="summary-item offline">{{ offlineCount }} Offline</span>
        </div>
        <div v-if="showActions" class="fleet-actions">
          <slot name="actions">
            <button class="action-btn primary">Add Robot</button>
            <button class="action-btn secondary">Bulk Actions</button>
            <button class="action-btn secondary">Export Data</button>
          </slot>
        </div>
      </div>
    </div>
    
    <!-- Loading State -->
    <div v-if="isLoading" class="loading-state">
      <div class="loading-spinner">⏳</div>
      <p>Loading robots...</p>
    </div>
    
    <!-- Empty State -->
    <div v-else-if="robots.length === 0" class="empty-state">
      <div class="empty-icon">🤖</div>
      <h3>No Robots Available</h3>
      <p>No robots are currently connected to the system.</p>
    </div>
    
    <!-- Robots Grid -->
    <div v-else class="robots-grid">
      <RobotCard
        v-for="robot in robots"
        :key="robot.id"
        :robot="robot"
        :variant="variant"
        @send-command="$emit('send-command', $event)"
        @configure="$emit('configure', $event)"
        @view-logs="$emit('view-logs', $event)"
        @delete="$emit('delete', $event)"
      />
    </div>
  </section>
</template>

<script>
import RobotCard from './RobotCard.vue'

export default {
  name: 'RobotFleet',
  components: {
    RobotCard
  },
  props: {
    robots: {
      type: Array,
      default: () => []
    },
    isLoading: {
      type: Boolean,
      default: false
    },
    title: {
      type: String,
      default: '🤖 Robot Fleet Management'
    },
    variant: {
      type: String,
      default: 'museum',
      validator: value => ['admin', 'museum'].includes(value)
    },
    showActions: {
      type: Boolean,
      default: false
    }
  },
  computed: {
    activeCount() {
      return this.robots.filter(robot => robot.status === 'ACTIVE' || robot.status === 'active').length
    },
    idleCount() {
      return this.robots.filter(robot => robot.status === 'IDLE' || robot.status === 'idle').length
    },
    offlineCount() {
      return this.robots.filter(robot => robot.status === 'OFFLINE' || robot.status === 'offline').length
    }
  },
  emits: ['send-command', 'configure', 'view-logs', 'delete']
}
</script>

<style scoped>
.robots-section {
  max-width: 1400px;
  margin: 0 auto;
  padding: 0 2rem 2rem;
}

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

.action-btn {
  padding: 0.5rem 1rem;
  border-radius: 0.5rem;
  font-size: 0.875rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s ease;
  border: none;
}

.action-btn.primary {
  background: var(--primary-blue);
  color: white;
}

.action-btn.secondary {
  background: rgba(255, 255, 255, 0.7);
  color: var(--neutral-700);
  border: 1px solid rgba(255, 255, 255, 0.3);
}

.action-btn:hover {
  transform: translateY(-1px);
  box-shadow: var(--shadow-md);
}

.robots-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(450px, 1fr));
  gap: 2rem;
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

/* Responsive Design */
@media (max-width: 1024px) {
  .robots-grid {
    grid-template-columns: repeat(auto-fill, minmax(400px, 1fr));
  }
}

@media (max-width: 768px) {
  .robots-section {
    padding: 1rem;
  }
  
  .section-header {
    flex-direction: column;
    gap: 1rem;
    align-items: flex-start;
  }
  
  .header-controls {
    align-items: flex-start;
    gap: 1.5rem;
  }
  
  .fleet-summary {
    flex-direction: column;
    gap: 0.5rem;
  }
  
  .fleet-actions {
    flex-direction: column;
  }
  
  .robots-grid {
    grid-template-columns: 1fr;
  }
}
</style>
