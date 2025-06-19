<template>
  <div class="login-page">
    <div class="login-container">
      <!-- Background Elements -->
      <div class="bg-elements">
        <div class="bg-circle circle-1"></div>
        <div class="bg-circle circle-2"></div>
        <div class="bg-circle circle-3"></div>
      </div>

      <!-- Login Card -->
      <div class="login-card">
        <!-- Header -->
        <div class="login-header">
          <div class="logo-section">
            <div class="logo-icon">🤖</div>
            <h1>🚀 ARTBOT CONTROL HUB 🚀</h1>
            <p class="tagline">Museum Exhibition Robot Management System</p>
          </div>
        </div>

        <!-- Login Form -->
        <form @submit.prevent="handleLogin" class="login-form">
          <div class="form-group">
            <label for="password" class="form-label">
              🔐 Access Password
            </label>
            <div class="input-wrapper">
              <input
                id="password"
                v-model="password"
                type="password"
                required
                class="form-input"
                placeholder="Enter your access password"
                :disabled="authStore.isLoading"
              />
              <div class="input-icon">🔑</div>
            </div>
          </div>

          <!-- Error Message -->
          <div v-if="authStore.error" class="error-message">
            <div class="error-icon">⚠️</div>
            <span>{{ authStore.error }}</span>
          </div>          <!-- Submit Button -->
          <button
            type="submit"
            class="submit-btn"
            :disabled="authStore.isLoading || !password"
          >
            <span v-if="authStore.isLoading" class="loading-spinner">⏳</span>
            <span v-else class="btn-icon">🚀</span>
            {{ authStore.isLoading ? 'Validating Access...' : 'Access Control Hub' }}
          </button>
        </form>

        <!-- Footer -->
        <div class="login-footer">
          <div class="version-info">
            <span class="version">Artbot Control Hub v2.0.0</span>
            <span class="copyright">© 2025 Museum Robotics</span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

export default {
  name: 'PasswordLogin',
  setup() {
    const password = ref('')
    const router = useRouter()
    const authStore = useAuthStore()

    const handleLogin = async () => {
      try {
        const result = await authStore.login(password.value)
        
        // Clear password field
        password.value = ''
        
        // Redirect based on access level
        if (result.access_level === 'ADMIN') {
          router.push('/admin')
        } else {
          router.push('/museum')
        }
        
      } catch (error) {
        // Error is handled by the store
        password.value = ''
      }
    }

    return {
      password,
      authStore,
      handleLogin
    }
  }
}
</script>

<style scoped>
/* Modern CSS Variables */
:root {
  --primary-blue: #2563eb;
  --primary-blue-dark: #1d4ed8;
  --primary-blue-light: #3b82f6;
  --success-green: #10b981;
  --warning-orange: #f59e0b;
  --danger-red: #ef4444;
  --neutral-50: #f9fafb;
  --neutral-100: #f3f4f6;
  --neutral-200: #e5e7eb;
  --neutral-300: #d1d5db;
  --neutral-400: #9ca3af;
  --neutral-500: #6b7280;
  --neutral-600: #4b5563;
  --neutral-700: #374151;
  --neutral-800: #1f2937;
  --neutral-900: #111827;
  --glass-bg: rgba(255, 255, 255, 0.85);
  --glass-border: rgba(255, 255, 255, 0.2);
  --shadow-sm: 0 1px 3px 0 rgba(0, 0, 0, 0.1), 0 1px 2px 0 rgba(0, 0, 0, 0.06);
  --shadow-md: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
  --shadow-lg: 0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05);
  --shadow-xl: 0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04);
}

.login-page {
  min-height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 2rem;
  font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
  position: relative;
  overflow: hidden;
}

.login-container {
  position: relative;
  z-index: 10;
  width: 100%;
  max-width: 480px;
}

/* Background Elements */
.bg-elements {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  pointer-events: none;
}

.bg-circle {
  position: absolute;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(20px);
  animation: float 6s ease-in-out infinite;
}

.circle-1 {
  width: 200px;
  height: 200px;
  top: 10%;
  left: -10%;
  animation-delay: 0s;
}

.circle-2 {
  width: 150px;
  height: 150px;
  top: 60%;
  right: -5%;
  animation-delay: 2s;
}

.circle-3 {
  width: 100px;
  height: 100px;
  bottom: 20%;
  left: 20%;
  animation-delay: 4s;
}

@keyframes float {
  0%, 100% { transform: translateY(0px) rotate(0deg); }
  50% { transform: translateY(-20px) rotate(180deg); }
}

/* Login Card */
.login-card {
  background: var(--glass-bg);
  backdrop-filter: blur(20px);
  border: 1px solid var(--glass-border);
  border-radius: 2rem;
  padding: 3rem;
  box-shadow: var(--shadow-xl);
  position: relative;
  overflow: hidden;
}

.login-card::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 4px;
  background: linear-gradient(90deg, #fbbf24, #f59e0b, #3b82f6, #8b5cf6);
}

/* Header */
.login-header {
  text-align: center;
  margin-bottom: 2.5rem;
}

.logo-section .logo-icon {
  font-size: 4rem;
  margin-bottom: 1rem;
  display: block;
  background: linear-gradient(135deg, #fbbf24, #f59e0b);
  background-clip: text;
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  filter: drop-shadow(0 2px 4px rgba(0,0,0,0.1));
}

.logo-section h1 {
  font-size: 2.25rem;
  font-weight: 800;
  background: linear-gradient(135deg, var(--neutral-800), var(--neutral-600));
  background-clip: text;
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  margin: 0 0 0.5rem 0;
  line-height: 1.2;
}

.tagline {
  font-size: 0.875rem;
  color: var(--neutral-500);
  margin: 0;
  font-weight: 500;
}

/* Form */
.login-form {
  margin-bottom: 3rem;
}

.form-group {
  margin-bottom: 2.5rem;
}

.form-label {
  display: block;
  font-size: 0.875rem;
  font-weight: 600;
  color: var(--neutral-700);
  margin-bottom: 0.75rem;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.input-wrapper {
  position: relative;
}

.form-input {
  width: 100%;
  padding: 1rem 1rem 1rem 3rem;
  border: 2px solid rgba(255, 255, 255, 0.3);
  border-radius: 1rem;
  background: rgba(255, 255, 255, 0.7);
  backdrop-filter: blur(10px);
  font-size: 1rem;
  font-weight: 500;
  color: var(--neutral-800);
  transition: all 0.3s ease;
  outline: none;
}

.form-input:focus {
  border-color: var(--primary-blue);
  background: rgba(255, 255, 255, 0.9);
  box-shadow: 0 0 0 3px rgba(37, 99, 235, 0.1);
}

.form-input:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.input-icon {
  position: absolute;
  left: 1rem;
  top: 50%;
  transform: translateY(-50%);
  font-size: 1.25rem;
  pointer-events: none;
}

.submit-btn {
  width: 100%;
  padding: 1.25rem 2rem;
  background: linear-gradient(135deg, #2563eb, #3b82f6, #1d4ed8);
  color: white;
  border: 2px solid rgba(255, 255, 255, 0.2);
  border-radius: 1.25rem;
  font-size: 1.1rem;
  font-weight: 800;
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.75rem;
  box-shadow: 0 8px 25px rgba(37, 99, 235, 0.3), 0 4px 15px rgba(0, 0, 0, 0.1);
  text-transform: uppercase;
  letter-spacing: 0.1em;
  position: relative;
  overflow: hidden;
}

.submit-btn::before {
  content: '';
  position: absolute;
  top: 0;
  left: -100%;
  width: 100%;
  height: 100%;
  background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.2), transparent);
  transition: left 0.5s ease;
}

.submit-btn:hover:not(:disabled) {
  transform: translateY(-3px);
  box-shadow: 0 12px 35px rgba(37, 99, 235, 0.4), 0 6px 20px rgba(0, 0, 0, 0.15);
  border-color: rgba(255, 255, 255, 0.4);
  background: linear-gradient(135deg, #1d4ed8, #2563eb, #3b82f6);
}

.submit-btn:hover:not(:disabled)::before {
  left: 100%;
}

.submit-btn:active:not(:disabled) {
  transform: translateY(-1px);
  box-shadow: 0 6px 20px rgba(37, 99, 235, 0.3), 0 3px 10px rgba(0, 0, 0, 0.1);
}

.submit-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
  transform: none !important;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
}

.btn-icon,
.loading-spinner {
  font-size: 1.5rem;
  filter: drop-shadow(0 1px 2px rgba(0, 0, 0, 0.3));
}

.loading-spinner {
  animation: spin 1s linear infinite;
}

@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

/* Error Message */
.error-message {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  background: rgba(239, 68, 68, 0.1);
  border: 1px solid rgba(239, 68, 68, 0.2);
  color: var(--danger-red);
  padding: 1rem;
  border-radius: 1rem;
  margin-bottom: 1.5rem;
  font-weight: 500;
}

.error-icon {
  font-size: 1.25rem;
}

/* Footer */
.login-footer {
  text-align: center;
  padding-top: 2rem;
  border-top: 1px solid rgba(255, 255, 255, 0.3);
}

.version-info {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.version {
  font-size: 0.75rem;
  font-weight: 600;
  color: var(--neutral-600);
}

.copyright {
  font-size: 0.625rem;
  color: var(--neutral-400);
}

/* Responsive Design */
@media (max-width: 768px) {
  .login-page {
    padding: 1rem;
  }
  
  .login-card {
    padding: 2rem;
  }
  
  .logo-section h1 {
    font-size: 1.75rem;
  }
  
  .logo-section .logo-icon {
    font-size: 3rem;
  }
}

@media (max-width: 480px) {
  .login-card {
    padding: 1.5rem;
  }
  
  .logo-section h1 {
    font-size: 1.5rem;
  }
}
</style>
