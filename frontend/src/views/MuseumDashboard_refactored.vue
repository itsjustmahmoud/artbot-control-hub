<template>
  <div class="museum-dashboard">
    <!-- Header -->
    <DashboardHeader
      subtitle="Museum Operations Center"
      :user-name="userName"
      user-role="museum"
      @logout="handleLogout"
    />

    <!-- Status Overview -->
    <StatusOverview :status-cards="statusCards" />

    <!-- Robot Fleet -->
    <RobotsGrid
      title="🤖 Robot Fleet Management"
      :robots="safeRobots"
      :is-loading="isLoading"
      mode="museum"
      @robot-command="sendCommand"
      @view-logs="viewLogs"
    />

    <!-- Activity Feed -->
    <ActivityFeed
      title="📈 Recent System Activity"
      :activities="recentLogs"
    />
  </div>
</template>

<script>
import { mapState, mapActions } from 'pinia'
import { useRobotsStore } from '@/stores/robots'
import { useAuthStore } from '@/stores/auth'

// Import components
import DashboardHeader from '@/components/shared/DashboardHeader.vue'
import StatusOverview from '@/components/shared/StatusOverview.vue'
import RobotsGrid from '@/components/shared/RobotsGrid.vue'
import ActivityFeed from '@/components/shared/ActivityFeed.vue'

export default {
  name: 'MuseumDashboard',
  components: {
    DashboardHeader,
    StatusOverview,
    RobotsGrid,
    ActivityFeed
  },
  data() {
    return {
      userName: 'Museum Staff',
      systemStatus: 'HEALTHY',
      recentLogs: [
        { 
          id: 1, 
          timestamp: new Date(), 
          robotId: 'ART-001', 
          level: 'INFO', 
          message: 'Person following mode activated' 
        },
        { 
          id: 2, 
          timestamp: new Date(Date.now() - 60000), 
          robotId: 'ART-002', 
          level: 'INFO', 
          message: 'Battery charging completed' 
        },
        { 
          id: 3, 
          timestamp: new Date(Date.now() - 120000), 
          robotId: 'ART-003', 
          level: 'INFO', 
          message: 'Navigation completed' 
        }
      ]
    }
  },
  computed: {
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
    },
    
    connectedAgentsCount() {
      return this.safeRobots.filter(robot => robot.status !== 'OFFLINE').length
    },
    
    statusCards() {
      return [
        {
          id: 'active-robots',
          type: 'active-robots',
          icon: '🟢',
          title: 'Active Robots',
          value: this.activeRobotsCount,
          subtitle: 'Currently operational'
        },
        {
          id: 'system-health',
          type: 'system-health',
          icon: this.systemStatus === 'HEALTHY' ? '💚' : this.systemStatus === 'WARNING' ? '⚠️' : '🔴',
          title: 'System Health',
          value: this.systemStatus,
          subtitle: 'Overall system status'
        },
        {
          id: 'connected-agents',
          type: 'connected-agents',
          icon: '🔗',
          title: 'Connected Agents',
          value: this.connectedAgentsCount,
          subtitle: 'Agents online'
        },
        {
          id: 'uptime',
          type: 'uptime',
          icon: '⏱️',
          title: 'System Uptime',
          value: '24h 16m',
          subtitle: 'Since last restart'
        }
      ]
    }
  },
  
  methods: {
    ...mapActions(useRobotsStore, ['sendCommand', 'fetchRobots']),
    ...mapActions(useAuthStore, ['logout']),
    
    handleLogout() {
      this.logout()
      this.$router.push('/')
    },
    
    viewLogs(robotId) {
      // Navigate to detailed logs view
      this.$router.push(`/logs/${robotId}`)
    }
  },
  
  async mounted() {
    await this.fetchRobots()
  }
}
</script>

<style scoped>
/* Import CSS variables */
@import '@/styles/variables.css';

.museum-dashboard {
  min-height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 0;
  font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
}

/* Responsive Design */
@media (max-width: 768px) {
  .museum-dashboard {
    padding: 0;
  }
}
</style>
