<template>
  <section class="analytics-section">
    <div class="section-header">
      <h2>📊 System Analytics & Management</h2>
      <div class="analytics-controls">
        <select class="time-filter">
          <option value="1h">Last Hour</option>
          <option value="24h" selected>Last 24 Hours</option>
          <option value="7d">Last 7 Days</option>
          <option value="30d">Last 30 Days</option>
        </select>
      </div>
    </div>
    
    <div class="analytics-grid">
      <!-- Performance Metrics -->
      <div class="analytics-card">
        <div class="card-header">
          <h3>⚡ Performance Metrics</h3>
          <span class="status-indicator healthy">Optimal</span>
        </div>
        <div class="metrics-list">
          <div class="metric-row">
            <span class="metric-label">Average Response Time</span>
            <span class="metric-value">127ms</span>
          </div>
          <div class="metric-row">
            <span class="metric-label">System Load</span>
            <span class="metric-value">23%</span>
          </div>
          <div class="metric-row">
            <span class="metric-label">Memory Usage</span>
            <span class="metric-value">1.2GB / 4GB</span>
          </div>
          <div class="metric-row">
            <span class="metric-label">Network Latency</span>
            <span class="metric-value">8ms</span>
          </div>
        </div>
      </div>

      <!-- Fleet Statistics -->
      <div class="analytics-card">
        <div class="card-header">
          <h3>🤖 Fleet Statistics</h3>
          <span class="status-indicator active">{{ robotCount }} Total</span>
        </div>
        <div class="stats-grid">
          <div class="stat-item">
            <div class="stat-number">{{ Math.round(robotCount * 0.85) }}</div>
            <div class="stat-label">Operational Hours</div>
          </div>
          <div class="stat-item">
            <div class="stat-number">98.5%</div>
            <div class="stat-label">Uptime</div>
          </div>
          <div class="stat-item">
            <div class="stat-number">{{ Math.round(robotCount * 0.72) }}</div>
            <div class="stat-label">Tasks Completed</div>
          </div>
          <div class="stat-item">
            <div class="stat-number">0</div>
            <div class="stat-label">Critical Errors</div>
          </div>
        </div>
      </div>

      <!-- System Health -->
      <div class="analytics-card full-width">
        <div class="card-header">
          <h3>🏥 System Health Dashboard</h3>
          <div class="health-controls">
            <button class="action-btn secondary tiny" @click="runDiagnostics">🔍 Run Diagnostics</button>
            <button class="action-btn secondary tiny" @click="restartSystem">🔄 Restart System</button>
          </div>
        </div>
        <div class="health-indicators">
          <div class="health-item healthy">
            <div class="health-icon">💚</div>
            <div class="health-info">
              <span class="health-name">Database Connection</span>
              <span class="health-status">Healthy</span>
            </div>
          </div>
          <div class="health-item healthy">
            <div class="health-icon">💚</div>
            <div class="health-info">
              <span class="health-name">WebSocket Services</span>
              <span class="health-status">Connected</span>
            </div>
          </div>
          <div class="health-item healthy">
            <div class="health-icon">💚</div>
            <div class="health-info">
              <span class="health-name">API Gateway</span>
              <span class="health-status">Responsive</span>
            </div>
          </div>
          <div class="health-item warning">
            <div class="health-icon">⚠️</div>
            <div class="health-info">
              <span class="health-name">Storage Space</span>
              <span class="health-status">78% Used</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  </section>
</template>

<script>
export default {
  name: 'AnalyticsSection',
  props: {
    robotCount: {
      type: Number,
      default: 0
    }
  },
  methods: {
    runDiagnostics() {
      alert('Running system diagnostics... Feature coming soon!')
    },
    restartSystem() {
      if (confirm('Are you sure you want to restart the entire system? This will temporarily interrupt all robot operations.')) {
        alert('System restart initiated... Feature coming soon!')
      }
    }
  }
}
</script>

<style scoped>
.analytics-section {
  max-width: 1400px;
  margin: 0 auto;
  padding: 0 2rem 2rem;
}

.analytics-controls {
  display: flex;
  gap: 1rem;
  align-items: center;
}

.time-filter {
  padding: 0.5rem 1rem;
  border: 1px solid rgba(255, 255, 255, 0.3);
  border-radius: 0.5rem;
  background: rgba(255, 255, 255, 0.7);
  backdrop-filter: blur(10px);
  color: var(--neutral-700);
  font-weight: 500;
  cursor: pointer;
  outline: none;
}

.analytics-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 2rem;
}

.analytics-card {
  background: var(--glass-bg);
  backdrop-filter: blur(20px);
  border: 1px solid var(--glass-border);
  border-radius: 1.5rem;
  padding: 2rem;
  box-shadow: var(--shadow-lg);
  transition: all 0.3s ease;
}

.analytics-card.full-width {
  grid-column: 1 / -1;
}

.analytics-card:hover {
  transform: translateY(-2px);
  box-shadow: var(--shadow-xl);
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.5rem;
}

.card-header h3 {
  font-size: 1.25rem;
  font-weight: 700;
  color: var(--neutral-800);
  margin: 0;
}

.status-indicator {
  padding: 0.5rem 1rem;
  border-radius: 0.75rem;
  font-size: 0.75rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.status-indicator.healthy {
  background: rgba(16, 185, 129, 0.1);
  color: var(--success-green);
  border: 1px solid rgba(16, 185, 129, 0.2);
}

.status-indicator.active {
  background: rgba(37, 99, 235, 0.1);
  color: var(--primary-blue);
  border: 1px solid rgba(37, 99, 235, 0.2);
}

.metrics-list {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.metric-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.75rem;
  background: rgba(255, 255, 255, 0.5);
  border-radius: 0.75rem;
  transition: all 0.2s ease;
}

.metric-row:hover {
  background: rgba(255, 255, 255, 0.7);
  transform: translateY(-1px);
}

.metric-label {
  font-size: 0.875rem;
  color: var(--neutral-600);
  font-weight: 500;
}

.metric-value {
  font-size: 0.875rem;
  color: var(--neutral-800);
  font-weight: 700;
}

.stats-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1rem;
}

.stat-item {
  text-align: center;
  padding: 1rem;
  background: rgba(255, 255, 255, 0.5);
  border-radius: 1rem;
  transition: all 0.2s ease;
}

.stat-item:hover {
  background: rgba(255, 255, 255, 0.7);
  transform: translateY(-1px);
}

.stat-number {
  font-size: 1.5rem;
  font-weight: 800;
  color: var(--primary-blue);
  margin-bottom: 0.25rem;
}

.stat-label {
  font-size: 0.75rem;
  color: var(--neutral-600);
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.health-controls {
  display: flex;
  gap: 0.5rem;
}

.health-indicators {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 1rem;
}

.health-item {
  display: flex;
  align-items: center;
  gap: 1rem;
  padding: 1rem;
  background: rgba(255, 255, 255, 0.5);
  border-radius: 1rem;
  transition: all 0.2s ease;
}

.health-item:hover {
  background: rgba(255, 255, 255, 0.7);
  transform: translateY(-1px);
}

.health-icon {
  font-size: 1.5rem;
}

.health-info {
  flex: 1;
}

.health-name {
  display: block;
  font-weight: 600;
  color: var(--neutral-800);
  font-size: 0.875rem;
}

.health-status {
  display: block;
  font-size: 0.75rem;
  color: var(--neutral-500);
  margin-top: 0.125rem;
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

.action-btn:hover {
  transform: translateY(-1px);
  box-shadow: var(--shadow-md);
}

/* Responsive Design */
@media (max-width: 1024px) {
  .analytics-grid {
    grid-template-columns: 1fr;
  }
  
  .stats-grid {
    grid-template-columns: 1fr 1fr;
  }
  
  .health-indicators {
    grid-template-columns: 1fr 1fr;
  }
}

@media (max-width: 768px) {
  .analytics-controls {
    flex-direction: column;
  }
  
  .card-header {
    flex-direction: column;
    gap: 1rem;
    align-items: flex-start;
  }
  
  .health-controls {
    flex-direction: column;
    gap: 0.5rem;
  }
  
  .stats-grid {
    grid-template-columns: 1fr;
  }
  
  .health-indicators {
    grid-template-columns: 1fr;
  }
}
</style>
