<template>
  <div class="status-card" :class="type">
    <div class="card-icon">{{ icon }}</div>
    <div class="card-content">
      <h3>{{ title }}</h3>
      <div class="status-number" v-if="typeof value === 'number' || !isNaN(value)">{{ value }}</div>
      <div class="status-indicator" v-else :class="value.toLowerCase()">{{ value }}</div>
      <p class="status-subtitle">{{ subtitle }}</p>
    </div>
  </div>
</template>

<script>
export default {
  name: 'StatusCard',
  props: {
    icon: {
      type: String,
      required: true
    },
    title: {
      type: String,
      required: true
    },
    value: {
      type: [String, Number],
      required: true
    },
    subtitle: {
      type: String,
      required: true
    },
    type: {
      type: String,
      default: 'default'
    }
  }
}
</script>

<style scoped>
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
  background: linear-gradient(90deg, var(--success-green), var(--success-green-light));
}

.status-card.data-throughput::before {
  background: linear-gradient(90deg, var(--primary-blue), var(--primary-blue-light));
}

.status-card.active-robots::before {
  background: linear-gradient(90deg, var(--success-green), var(--success-green-light));
}

.status-card.system-health::before {
  background: linear-gradient(90deg, var(--success-green), var(--success-green-light));
}

.status-card.connected-agents::before {
  background: linear-gradient(90deg, var(--primary-blue), var(--primary-blue-light));
}

.status-card.uptime::before {
  background: linear-gradient(90deg, #fbbf24, #f59e0b);
}

.status-card:hover {
  transform: translateY(-2px);
  box-shadow: var(--shadow-xl);
}

.card-icon {
  font-size: 3rem;
  flex-shrink: 0;
}

.card-content {
  flex: 1;
}

.card-content h3 {
  font-size: 1rem;
  font-weight: 600;
  color: var(--neutral-700);
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

.status-indicator {
  font-size: 1.5rem;
  font-weight: 700;
  padding: 0.5rem 1rem;
  border-radius: 0.75rem;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  margin: 0 0 0.25rem 0;
  display: inline-block;
}

.status-indicator.healthy {
  background: rgba(16, 185, 129, 0.1);
  color: var(--success-green);
  border: 1px solid rgba(16, 185, 129, 0.2);
}

.status-indicator.warning {
  background: rgba(245, 158, 11, 0.1);
  color: var(--warning-orange);
  border: 1px solid rgba(245, 158, 11, 0.2);
}

.status-indicator.critical {
  background: rgba(239, 68, 68, 0.1);
  color: var(--danger-red);
  border: 1px solid rgba(239, 68, 68, 0.2);
}

.status-subtitle {
  font-size: 0.75rem;
  color: var(--neutral-500);
  margin: 0;
}
</style>
