import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

// Import views
import PasswordLogin from '@/views/PasswordLogin.vue'
import MuseumDashboard from '@/views/MuseumDashboard.vue'
import AdminDashboard from '@/views/AdminDashboard.vue'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    {
      path: '/',
      name: 'login',
      component: PasswordLogin
    },    {
      path: '/museum',
      name: 'museum',
      component: MuseumDashboard,
      meta: { requiresAuth: true, role: 'MUSEUM' }
    },
    {
      path: '/admin',
      name: 'admin', 
      component: AdminDashboard,
      meta: { requiresAuth: true, role: 'ADMIN' }
    },
    {
      path: '/logout',
      name: 'logout',
      redirect: '/'
    }
  ]
})

// Navigation guard for authentication
router.beforeEach((to, from, next) => {
  const authStore = useAuthStore()
  
  if (to.meta.requiresAuth) {
    if (!authStore.isAuthenticated) {
      next('/')
      return
    }
    
    // Check role-based access
    if (to.meta.role && !authStore.hasRole(to.meta.role)) {
      // Redirect to appropriate dashboard based on user's role
      if (authStore.accessLevel === 'ADMIN') {
        next('/admin')
      } else {
        next('/museum')
      }
      return
    }
  }
  
  // If user is authenticated and trying to access login, redirect to dashboard
  if (to.name === 'login' && authStore.isAuthenticated) {
    if (authStore.accessLevel === 'ADMIN') {
      next('/admin')
    } else {
      next('/museum')
    }
    return
  }
  
  next()
})

export default router
