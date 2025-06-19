<template>
  <div class="metric-card" :class="$attrs.class">
    <div class="metric-icon">{{ icon }}</div>
    <div class="metric-info">
      <span class="metric-label">{{ label }}</span>
      <span class="metric-value">{{ value }}</span>
    </div>
    <slot></slot>
  </div>
</template>

<script>
export default {
  name: 'MetricCard',
  props: {
    icon: {
      type: String,
      required: true
    },
    label: {
      type: String,
      required: true
    },
    value: {
      type: [String, Number],
      required: true
    }
  },
  inheritAttrs: false
}
</script>

<style scoped>
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
</style>
