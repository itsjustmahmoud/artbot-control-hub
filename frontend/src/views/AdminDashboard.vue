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
    <StatusOverview :status-cards="statusCards" />    <!-- Robot Fleet -->
    <RobotsGrid
      title="🤖 Advanced Fleet Management"
      :robots="safeRobots"
      :is-loading="isLoading"
      mode="admin"
      :show-admin-controls="true"
      @workspace-start="startWorkspace"
      @workspace-stop="stopWorkspace"
      @restart-create3="restartCreate3"
      @reboot-create3="rebootCreate3"
      @view-workspace-logs="viewWorkspaceLogs"
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
      runningWorkspacesCount() {
      return this.safeRobots.filter(robot => robot.workspace_status === 'running').length
    },
    
    connectedCreate3Count() {
      return this.safeRobots.filter(robot => robot.create3_connected).length
    },
    
    averageCpuUsage() {
      const cpuValues = this.safeRobots.map(robot => robot.cpu_usage || 0).filter(cpu => cpu > 0)
      return cpuValues.length > 0 ? Math.round(cpuValues.reduce((a, b) => a + b, 0) / cpuValues.length) : 0
    },
    
    averageTemperature() {
      const tempValues = this.safeRobots.map(robot => robot.temperature || 0).filter(temp => temp > 0)
      return tempValues.length > 0 ? Math.round(tempValues.reduce((a, b) => a + b, 0) / tempValues.length) : 0
    },
    
    statusCards() {
      return [
        {
          id: 'workspace-performance',
          type: 'workspace-performance',
          icon: '⚙️',
          title: 'Workspace Performance',
          value: `${this.runningWorkspacesCount}/${this.robotsList.length}`,
          subtitle: 'Running workspaces'
        },
        {
          id: 'system-health',
          type: 'system-health',
          icon: '🌡️',
          title: 'System Health',
          value: `${this.averageCpuUsage}% / ${this.averageTemperature}°C`,
          subtitle: 'Avg CPU / Temperature'
        },
        {
          id: 'create3-connectivity',
          type: 'create3-connectivity',
          icon: '🤖',
          title: 'Create3 Connectivity',
          value: `${this.connectedCreate3Count}/${this.robotsList.length}`,
          subtitle: 'Connected robots'
        },
        {
          id: 'fleet-size',
          type: 'fleet-size',
          icon: '📊',
          title: 'Fleet Overview',
          value: this.robotsList.length,
          subtitle: 'Total managed robots'
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
    },

    // New role-based workspace and Create3 controls
    async startWorkspace(robotId) {
      try {
        await this.sendWorkspaceCommand(robotId, 'start')
        this.$toast?.success(`Started workspace on robot ${robotId}`)
      } catch (error) {
        console.error('Failed to start workspace:', error)
        this.$toast?.error(`Failed to start workspace on robot ${robotId}`)
      }
    },
    
    async stopWorkspace(robotId) {
      try {
        await this.sendWorkspaceCommand(robotId, 'stop')
        this.$toast?.success(`Stopped workspace on robot ${robotId}`)
      } catch (error) {
        console.error('Failed to stop workspace:', error)
        this.$toast?.error(`Failed to stop workspace on robot ${robotId}`)
      }
    },
    
    async restartCreate3(robotId) {
      if (confirm(`Are you sure you want to restart Create3 on robot ${robotId}?`)) {
        try {
          await this.sendCreate3Command(robotId, 'restart')
          this.$toast?.success(`Restarted Create3 on robot ${robotId}`)
        } catch (error) {
          console.error('Failed to restart Create3:', error)
          this.$toast?.error(`Failed to restart Create3 on robot ${robotId}`)
        }
      }
    },
    
    async rebootCreate3(robotId) {
      if (confirm(`Are you sure you want to reboot Create3 on robot ${robotId}? This will cause a temporary disconnect.`)) {
        try {
          await this.sendCreate3Command(robotId, 'reboot')
          this.$toast?.success(`Rebooted Create3 on robot ${robotId}`)
        } catch (error) {
          console.error('Failed to reboot Create3:', error)
          this.$toast?.error(`Failed to reboot Create3 on robot ${robotId}`)
        }
      }
    },
    
    async viewWorkspaceLogs(robotId) {
      try {
        const logs = await this.getWorkspaceLogs(robotId)
        // Show logs in a modal or navigate to logs page
        this.$router.push(`/admin/robots/${robotId}/workspace-logs`)
      } catch (error) {
        console.error('Failed to get workspace logs:', error)
        this.$toast?.error(`Failed to get workspace logs for robot ${robotId}`)
      }
    },
    
    async sendWorkspaceCommand(robotId, action) {
      const robotsStore = useRobotsStore()
      return await robotsStore.sendWorkspaceCommand(robotId, action)
    },
    
    async sendCreate3Command(robotId, action) {
      const robotsStore = useRobotsStore()
      return await robotsStore.sendCreate3Command(robotId, action)
    },
    
    async getWorkspaceLogs(robotId) {
      const robotsStore = useRobotsStore()
      return await robotsStore.getWorkspaceLogs(robotId)
    },
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
