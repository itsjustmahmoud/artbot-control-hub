<template>
  <section class="activity-section">
    <div class="section-header">
      <h2>📈 System Activity & Monitoring</h2>
      <div v-if="showAdminControls" class="admin-controls">
        <button class="action-btn secondary" @click="$emit('export-logs')">📤 Export Logs</button>
        <button class="action-btn secondary" @click="$emit('clear-logs')">🗑️ Clear History</button>
        <button class="view-all-btn">View All</button>
      </div>
    </div>
    <div class="activity-feed">
      <div 
        v-for="log in logs" 
        :key="log.id" 
        class="activity-item"
        :class="log.level.toLowerCase()"
      >
        <div class="activity-icon" :class="log.level.toLowerCase()">
          {{ getLogIcon(log.level) }}
        </div>
        <div class="activity-content">
          <div class="activity-header">
            <span class="activity-robot">{{ log.robotId }}</span>
            <span class="activity-time">{{ formatTime(log.timestamp) }}</span>
          </div>
          <p class="activity-message">{{ log.message }}</p>
        </div>
        <div v-if="showAdminControls" class="activity-actions">
          <button class="action-btn tiny" @click="$emit('view-log-details', log.id)">Details</button>
        </div>
      </div>
    </div>
  </section>
</template>

<script>
export default {
  name: 'ActivityFeed',
  props: {
    logs: {
      type: Array,
      default: () => []
    },
    showAdminControls: {
      type: Boolean,
      default: false
    }
  },
  methods: {
    formatTime(timestamp) {
      return new Date(timestamp).toLocaleTimeString()
    },
    getLogIcon(level) {
      const iconMap = {
        'INFO': 'ℹ️',
        'WARNING': '⚠️',
        'ERROR': '🚨',
        'DEBUG': '🔍'
      }
      return iconMap[level] || 'ℹ️'
    }
  },
  emits: ['export-logs', 'clear-logs', 'view-log-details']
}
</script>

<style scoped>
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

.action-btn {
  padding: 0.5rem 1rem;
  border-radius: 0.5rem;
  font-size: 0.875rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s ease;
  border: none;
}

.action-btn.secondary {
  background: rgba(255, 255, 255, 0.7);
  color: var(--neutral-700);
  border: 1px solid rgba(255, 255, 255, 0.3);
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

.view-all-btn:hover,
.action-btn:hover {
  transform: translateY(-1px);
  box-shadow: var(--shadow-md);
}

@media (max-width: 768px) {
  .admin-controls {
    flex-direction: column;
    gap: 0.5rem;
  }
  
  .activity-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 0.25rem;
  }
}
</style>
