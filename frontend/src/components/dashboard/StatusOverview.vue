<template>
  <section class="status-overview">
    <div class="status-grid">
      <StatusCard
        v-for="card in statusCards"
        :key="card.id"
        :icon="card.icon"
        :title="card.title"
        :value="card.value"
        :subtitle="card.subtitle"
        :type="card.type"
      />
    </div>
  </section>
</template>

<script>
import StatusCard from './StatusCard.vue'

export default {
  name: 'StatusOverview',
  components: {
    StatusCard
  },
  props: {
    robotCount: {
      type: Number,
      default: 0
    },
    activeRobots: {
      type: Number,
      default: 0
    },
    systemPerformance: {
      type: Number,
      default: 98.5
    },
    activeSessions: {
      type: Number,
      default: 0
    },
    dataThroughput: {
      type: String,
      default: '0 MB/s'
    },
    systemHealth: {
      type: String,
      default: 'HEALTHY'
    },
    connectedAgents: {
      type: Number,
      default: 0
    },
    uptime: {
      type: String,
      default: '0h 0m'
    },
    variant: {
      type: String,
      default: 'admin',
      validator: value => ['admin', 'museum'].includes(value)
    }
  },
  computed: {
    statusCards() {
      if (this.variant === 'museum') {
        return [
          {
            id: 'active-robots',
            icon: '🟢',
            title: 'Active Robots',
            value: this.activeRobots,
            subtitle: 'Currently operational',
            type: 'active-robots'
          },
          {
            id: 'system-health',
            icon: this.systemHealthIcon,
            title: 'System Health',
            value: this.systemHealth,
            subtitle: 'Overall system status',
            type: 'system-health'
          },
          {
            id: 'connected-agents',
            icon: '🔗',
            title: 'Connected Agents',
            value: this.connectedAgents,
            subtitle: 'Agents online',
            type: 'connected-agents'
          },
          {
            id: 'uptime',
            icon: '⏱️',
            title: 'System Uptime',
            value: this.uptime,
            subtitle: 'Since last restart',
            type: 'uptime'
          }
        ]
      } else {
        return [
          {
            id: 'system-performance',
            icon: '🚀',
            title: 'System Performance',
            value: `${this.systemPerformance}%`,
            subtitle: 'Overall uptime',
            type: 'system-performance'
          },
          {
            id: 'total-robots',
            icon: '🤖',
            title: 'Total Robots',
            value: this.robotCount,
            subtitle: 'Fleet size',
            type: 'total-robots'
          },
          {
            id: 'active-sessions',
            icon: '👥',
            title: 'Active Sessions',
            value: this.activeSessions,
            subtitle: 'Connected users',
            type: 'active-sessions'
          },
          {
            id: 'data-throughput',
            icon: '📊',
            title: 'Data Throughput',
            value: this.dataThroughput,
            subtitle: 'Network traffic',
            type: 'data-throughput'
          }
        ]
      }
    },
    systemHealthIcon() {
      const iconMap = {
        'HEALTHY': '💚',
        'WARNING': '⚠️',
        'CRITICAL': '🔴'
      }
      return iconMap[this.systemHealth] || '💚'
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
}

@media (max-width: 768px) {
  .status-overview {
    padding: 1rem;
  }
  
  .status-grid {
    grid-template-columns: 1fr;
  }
}
</style>
