<template>
  <section class="activity-section">
    <div class="section-header">
      <h2>📈 {{ title }}</h2>
      <div class="activity-controls" v-if="showControls">
        <button class="action-btn secondary" @click="$emit('export-logs')">📤 Export Logs</button>
        <button class="action-btn secondary" @click="$emit('clear-logs')">🗑️ Clear History</button>
        <button class="view-all-btn" @click="$emit('view-all')">View All</button>
      </div>
    </div>
    
    <div class="activity-feed">
      <div v-if="activities.length === 0" class="empty-state">
        <div class="empty-icon">📝</div>
        <h3>No Recent Activity</h3>
        <p>System activity will appear here as it happens.</p>
      </div>
      
      <div 
        v-else
        v-for="activity in activities" 
        :key="activity.id" 
        class="activity-item"
        :class="activity.level?.toLowerCase()"
      >
        <div class="activity-icon" :class="activity.level?.toLowerCase()">
          {{ getActivityIcon(activity.level) }}
        </div>
        <div class="activity-content">
          <div class="activity-header">
            <span class="activity-robot">{{ activity.robotId || activity.robot_id || 'System' }}</span>
            <span class="activity-time">{{ formatTime(activity.timestamp) }}</span>
          </div>
          <p class="activity-message">{{ activity.message }}</p>
        </div>
        <div class="activity-actions" v-if="showActions">
          <button class="action-btn tiny" @click="$emit('view-details', activity.id)">Details</button>
        </div>
      </div>
    </div>
  </section>
</template>

<script>
export default {
  name: 'ActivityFeed',
  props: {
    title: {
      type: String,
      default: 'System Activity & Monitoring'
    },
    activities: {
      type: Array,
      default: () => []
    },
    showControls: {
      type: Boolean,
      default: false
    },
    showActions: {
      type: Boolean,
      default: false
    }
  },
  methods: {
    formatTime(timestamp) {
      if (!timestamp) return ''
      return new Date(timestamp).toLocaleTimeString()
    },
    getActivityIcon(level) {
      const iconMap = {
        'INFO': 'ℹ️',
        'WARNING': '⚠️',
        'ERROR': '🚨',
        'SUCCESS': '✅'
      }
      return iconMap[level?.toUpperCase()] || 'ℹ️'
    }
  }
}
</script>

<style scoped>
.activity-section {
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

.activity-controls {
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
  box-shadow: var(--shadow-lg);
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
  display: inline-flex;
  align-items: center;
  gap: 0.25rem;
  padding: 0.5rem 0.75rem;
  border: none;
  border-radius: 0.5rem;
  cursor: pointer;
  font-weight: 500;
  font-size: 0.75rem;
  transition: all 0.2s ease;
  text-decoration: none;
}

.action-btn.secondary {
  background: rgba(255, 255, 255, 0.7);
  color: var(--neutral-700);
  border: 1px solid var(--glass-border);
}

.action-btn.secondary:hover {
  background: rgba(255, 255, 255, 0.9);
  transform: translateY(-1px);
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

.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 3rem 2rem;
  text-align: center;
}

.empty-icon {
  font-size: 3rem;
  margin-bottom: 1rem;
  opacity: 0.5;
}

.empty-state h3 {
  font-size: 1.25rem;
  font-weight: 600;
  color: var(--neutral-600);
  margin: 0 0 0.5rem 0;
}

.empty-state p {
  font-size: 0.875rem;
  color: var(--neutral-500);
  margin: 0;
}

/* Responsive Design */
@media (max-width: 768px) {
  .activity-section {
    padding: 1rem;
  }
  
  .section-header {
    flex-direction: column;
    gap: 1rem;
    align-items: flex-start;
  }
  
  .activity-controls {
    flex-direction: column;
    gap: 0.5rem;
    width: 100%;
  }
  
  .activity-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 0.25rem;
  }
  
  .activity-item {
    padding: 1rem;
  }
}
</style>
