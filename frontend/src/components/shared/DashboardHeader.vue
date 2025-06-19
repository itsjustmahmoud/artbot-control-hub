<template>
  <header class="dashboard-header">
    <div class="header-content">
      <div class="brand-section">
        <div class="logo-icon">🤖</div>
        <div class="brand-text">
          <h1>🚀 ARTBOT CONTROL HUB 🚀</h1>
          <p>{{ subtitle }}</p>
        </div>
      </div>
      <div class="header-actions">
        <div class="user-profile">
          <div class="avatar" :class="userRole">{{ userInitials }}</div>
          <div class="user-details">
            <span class="user-name">{{ userName }}</span>
            <span class="user-role">{{ userRoleDisplay }}</span>
          </div>
        </div>
        <button @click="handleLogout" class="logout-btn">
          <span class="logout-icon">🚪</span>
          Logout
        </button>
      </div>
    </div>
  </header>
</template>

<script>
export default {
  name: 'DashboardHeader',
  props: {
    subtitle: {
      type: String,
      default: 'Control Center'
    },
    userName: {
      type: String,
      default: 'User'
    },
    userRole: {
      type: String,
      default: 'user'
    }
  },
  computed: {
    userInitials() {
      return this.userName.split(' ').map(name => name.charAt(0)).join('').toUpperCase()
    },
    userRoleDisplay() {
      const roleDisplayMap = {
        'admin': 'Full Access',
        'museum': 'Operator',
        'user': 'User'
      }
      return roleDisplayMap[this.userRole] || 'User'
    }
  },
  methods: {
    handleLogout() {
      this.$emit('logout')
    }
  }
}
</script>

<style scoped>
.dashboard-header {
  background: var(--glass-bg);
  backdrop-filter: blur(20px);
  border-bottom: 1px solid var(--glass-border);
  padding: 1.5rem 0;
  position: sticky;
  top: 0;
  z-index: 100;
}

.header-content {
  max-width: 1400px;
  margin: 0 auto;
  padding: 0 2rem;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.brand-section {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.logo-icon {
  font-size: 3rem;
  background: linear-gradient(135deg, #fbbf24, #f59e0b);
  background-clip: text;
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  filter: drop-shadow(0 2px 4px rgba(0,0,0,0.1));
}

.brand-text h1 {
  font-size: 2rem;
  font-weight: 800;
  background: linear-gradient(135deg, var(--neutral-800), var(--neutral-600));
  background-clip: text;
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  margin: 0;
  line-height: 1.2;
}

.brand-text p {
  font-size: 0.875rem;
  color: var(--neutral-500);
  margin: 0;
  font-weight: 500;
}

.header-actions {
  display: flex;
  align-items: center;
  gap: 1.5rem;
}

.user-profile {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.avatar {
  width: 2.5rem;
  height: 2.5rem;
  background: linear-gradient(135deg, var(--primary-blue), var(--primary-blue-light));
  color: white;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 600;
  font-size: 0.875rem;
  box-shadow: var(--shadow-md);
}

.avatar.admin {
  background: linear-gradient(135deg, #fbbf24, #f59e0b);
}

.avatar.museum {
  background: linear-gradient(135deg, var(--success-green), var(--success-green-light));
}

.user-details {
  display: flex;
  flex-direction: column;
}

.user-name {
  font-weight: 600;
  color: var(--neutral-800);
  font-size: 0.875rem;
}

.user-role {
  font-size: 0.75rem;
  color: var(--neutral-500);
}

.logout-btn {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.75rem 1rem;
  background: rgba(239, 68, 68, 0.1);
  color: var(--danger-red);
  border: 1px solid rgba(239, 68, 68, 0.2);
  border-radius: var(--radius-lg);
  cursor: pointer;
  font-weight: 600;
  font-size: 0.875rem;
  transition: all var(--transition-fast);
}

.logout-btn:hover {
  background: rgba(239, 68, 68, 0.2);
  transform: translateY(-1px);
}

.logout-icon {
  font-size: 1rem;
}

/* Responsive Design */
@media (max-width: 768px) {
  .header-content {
    flex-direction: column;
    gap: 1rem;
    text-align: center;
    padding: 0 1rem;
  }
  
  .brand-text h1 {
    font-size: 1.5rem;
  }
  
  .logo-icon {
    font-size: 2rem;
  }
  
  .user-profile {
    flex-direction: column;
    gap: 0.5rem;
  }
}
</style>
