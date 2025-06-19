<template>
  <section class="status-overview">
    <div class="status-grid">
      <div
        v-for="card in statusCards"
        :key="card.id"
        class="status-card"
        :class="card.type"
      >
        <div class="card-icon">{{ card.icon }}</div>
        <div class="card-content">
          <h3>{{ card.title }}</h3>
          <div class="status-number">{{ card.value }}</div>
          <p class="status-subtitle">{{ card.subtitle }}</p>
        </div>
      </div>
    </div>
  </section>
</template>

<script>
export default {
  name: 'StatusOverview',
  props: {
    statusCards: {
      type: Array,
      required: true
    }
  }
}
</script>

<style scoped>
.status-overview {
  max-width: 1400px;
  margin: 0 auto;
  padding: 2rem;
}

.status-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 1.5rem;
  align-items: stretch;
}

.status-card {
  background: var(--glass-bg);
  backdrop-filter: blur(20px);
  border: 1px solid var(--glass-border);
  border-radius: 1.25rem;
  padding: 1.75rem;
  box-shadow: var(--shadow-lg);
  transition: all 0.3s ease;
  position: relative;
  overflow: hidden;
  display: flex;
  align-items: center;
  gap: 1.25rem;
  min-height: 120px;
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
  background: linear-gradient(90deg, var(--warning-orange), var(--warning-orange-light));
}

.status-card:hover {
  transform: translateY(-5px);
  box-shadow: var(--shadow-xl);
}

.card-icon {
  font-size: 3rem;
  opacity: 0.8;
}

.card-content {
  flex: 1;
  min-width: 0; /* Allow flex child to shrink below content size */
  overflow: hidden;
}

.card-content h3 {
  font-size: 0.875rem;
  font-weight: 600;
  color: var(--neutral-600);
  margin: 0 0 0.5rem 0;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.status-number {
  font-size: 1.875rem;
  font-weight: 800;
  color: var(--neutral-800);
  margin: 0 0 0.25rem 0;
  line-height: 1.2;
  word-wrap: break-word;
  overflow-wrap: break-word;
  max-width: 100%;
}

/* Special styling for text-based status values */
.status-card.system-health .status-number {
  font-size: 1.5rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.1em;
}

.status-card.uptime .status-number {
  font-size: 1.625rem;
  font-weight: 700;
}

.status-subtitle {
  font-size: 0.75rem;
  color: var(--neutral-500);
  margin: 0;
}

/* Responsive Design */
@media (max-width: 768px) {
  .status-overview {
    padding: 1rem;
  }
  
  .status-grid {
    grid-template-columns: 1fr;
    gap: 1.5rem;
  }
  
  .status-card {
    padding: 1.5rem;
    gap: 1rem;
    min-height: 100px;
  }
  
  .card-icon {
    font-size: 2rem;
  }
  
  .status-number {
    font-size: 1.5rem;
  }
  
  .card-content h3 {
    font-size: 0.75rem;
  }
}
</style>
