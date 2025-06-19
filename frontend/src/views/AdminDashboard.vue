<template>
  <div class="admin-dashboard">
    <!-- Header -->
    <DashboardHeader
      subtitle="Administrator Control Center"
      :user-name="userName"
      user-role="admin"
      @logout="handleLogout"
    />

    <!-- Status Overview -->
    <StatusOverview :status-cards="statusCards" />

    <!-- Robot Fleet -->
    <RobotsGrid
      title="🤖 Advanced Fleet Management"
      :robots="safeRobots"
      :is-loading="isLoading"
      mode="admin"
      :show-admin-controls="true"
      @robot-command="sendCommand"
      @configure-robot="configureRobot"
      @view-logs="viewLogs"
      @delete-robot="deleteRobot"
      @add-robot="addRobot"
      @bulk-actions="bulkActions"
      @export-data="exportData"
    />

    <!-- Activity Feed -->
    <ActivityFeed
      title="📈 System Activity & Monitoring"
      :activities="recentLogs"
      :show-controls="true"
      :show-actions="true"
      @export-logs="exportLogs"
      @clear-logs="clearLogs"
      @view-all="viewAllLogs"
      @view-details="viewLogDetails"
    />

    <!-- Admin Analytics -->
    <AdminAnalytics
      :total-robots="robotsList.length"
      @run-diagnostics="runDiagnostics"
      @restart-system="restartSystem"
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
import AdminAnalytics from '@/components/admin/AdminAnalytics.vue'

export default {
  name: 'AdminDashboard',
  components: {
    DashboardHeader,
    StatusOverview,
    RobotsGrid,
    ActivityFeed,
    AdminAnalytics
  },
  data() {
    return {
      userName: 'Administrator',
      recentLogs: [
        { 
          id: 1, 
          timestamp: new Date(), 
          robotId: 'ART-001', 
          level: 'INFO', 
          message: 'System initialized successfully' 
        },
        { 
          id: 2, 
          timestamp: new Date(Date.now() - 60000), 
          robotId: 'ART-002', 
          level: 'WARNING', 
          message: 'Battery level below 25%' 
        },
        { 
          id: 3, 
          timestamp: new Date(Date.now() - 120000), 
          robotId: 'ART-003', 
          level: 'INFO', 
          message: 'Navigation route completed' 
        },
        { 
          id: 4, 
          timestamp: new Date(Date.now() - 180000), 
          robotId: 'ART-001', 
          level: 'INFO', 
          message: 'Software update applied' 
        },
        { 
          id: 5, 
          timestamp: new Date(Date.now() - 240000), 
          robotId: 'ART-004', 
          level: 'ERROR', 
          message: 'Connection timeout detected' 
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
    
    statusCards() {
      return [
        {
          id: 'system-performance',
          type: 'system-performance',
          icon: '🚀',
          title: 'System Performance',
          value: '98.5%',
          subtitle: 'Overall uptime'
        },
        {
          id: 'total-robots',
          type: 'total-robots',
          icon: '🤖',
          title: 'Total Robots',
          value: this.robotsList.length,
          subtitle: 'Fleet size'
        },
        {
          id: 'active-sessions',
          type: 'active-sessions',
          icon: '👥',
          title: 'Active Sessions',
          value: '3',
          subtitle: 'Connected users'
        },
        {
          id: 'data-throughput',
          type: 'data-throughput',
          icon: '📊',
          title: 'Data Throughput',
          value: '2.4 MB/s',
          subtitle: 'Network traffic'
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
    
    // Robot management methods
    viewLogs(robotId) {
      this.$router.push(`/logs/${robotId}`)
    },
    
    configureRobot(robotId) {
      alert(`Configure robot ${robotId} - Feature coming soon!`)
    },
    
    deleteRobot(robotId) {
      if (confirm(`Are you sure you want to delete robot ${robotId}?`)) {
        alert(`Delete robot ${robotId} - Feature coming soon!`)
      }
    },
    
    addRobot() {
      alert('Add new robot - Feature coming soon!')
    },
    
    bulkActions() {
      alert('Bulk actions - Feature coming soon!')
    },
    
    exportData() {
      alert('Export robot data - Feature coming soon!')
    },
    
    // Activity feed methods
    exportLogs() {
      alert('Exporting system logs... Feature coming soon!')
    },
    
    clearLogs() {
      if (confirm('Are you sure you want to clear all logs? This action cannot be undone.')) {
        alert('Clearing logs... Feature coming soon!')
      }
    },
    
    viewAllLogs() {
      this.$router.push('/logs')
    },
    
    viewLogDetails(logId) {
      alert(`Viewing details for log ${logId} - Feature coming soon!`)
    },
    
    // Analytics methods
    runDiagnostics() {
      alert('Running system diagnostics... Feature coming soon!')
    },
    
    restartSystem() {
      if (confirm('Are you sure you want to restart the entire system? This will temporarily interrupt all robot operations.')) {
        alert('System restart initiated... Feature coming soon!')
      }
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

.admin-dashboard {
  min-height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 0;
  font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
}

/* Responsive Design */
@media (max-width: 768px) {
  .admin-dashboard {
    padding: 0;
  }
}
</style>
