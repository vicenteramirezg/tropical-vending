import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '../store/auth'

// Layouts
import DefaultLayout from '../layouts/DefaultLayout.vue'
import AuthLayout from '../layouts/AuthLayout.vue'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    {
      path: '/',
      component: DefaultLayout,
      meta: { requiresAuth: true },
      children: [
        {
          path: '',
          name: 'dashboard',
          component: () => import('../views/Dashboard.vue'),
          meta: { title: 'Dashboard' }
        },
        {
          path: 'locations',
          name: 'locations',
          component: () => import('../views/Locations.vue'),
          meta: { title: 'Locations' }
        },
        {
          path: 'machines',
          name: 'machines',
          component: () => import('../views/Machines.vue'),
          meta: { title: 'Machines' }
        },
        {
          path: 'products',
          name: 'products',
          component: () => import('../views/Products.vue'),
          meta: { title: 'Products' }
        },
        {
          path: 'restocks',
          name: 'restocks',
          component: () => import('../views/Restocks.vue'),
          meta: { title: 'Visits' }
        },
        {
          path: 'purchases',
          name: 'purchases',
          component: () => import('../views/Purchases.vue'),
          meta: { title: 'Wholesale Purchases' }
        },
        {
          path: 'analytics',
          name: 'analytics',
          component: () => import('../views/Analytics.vue'),
          meta: { title: 'Analytics' }
        }
      ]
    },
    {
      path: '/',
      component: AuthLayout,
      meta: { hideForAuth: true },
      children: [
        {
          path: '/login',
          name: 'login',
          component: () => import('../views/auth/Login.vue'),
          meta: { title: 'Login' }
        }
      ]
    },
    {
      path: '/home',
      name: 'home',
      component: () => import('../views/Home.vue'),
      meta: { title: 'Home' }
    },
    {
      // Catch-all route for 404
      path: '/:pathMatch(.*)*',
      name: 'not-found',
      component: () => import('../views/NotFound.vue')
    }
  ]
})

// Handle authentication
router.beforeEach((to, from, next) => {
  const authStore = useAuthStore()
  const isAuthenticated = authStore.isAuthenticated
  
  // Set page title
  document.title = to.meta.title ? `${to.meta.title} | Tropical Vending` : 'Tropical Vending'
  
  // Check authenticated routes
  if (to.meta.requiresAuth && !isAuthenticated) {
    next({ name: 'login' })
  } else if (to.meta.hideForAuth && isAuthenticated) {
    next({ name: 'dashboard' })
  } else {
    next()
  }
})

export default router 