import { createRouter, createWebHistory } from 'vue-router'

import Login from './views/Login.vue'
import Dashboard from './views/Dashboard.vue'

// Customers
import Customers from './views/Customers.vue'
import CustomerForm from './views/CustomerForm.vue'

// Lines (خدمات)
import Lines from './views/Lines.vue'
import LineForm from './views/LineForm.vue'

// Reservations
import Reservations from './views/Reservations.vue'
import ReservationForm from './views/ReservationForm.vue'
import ReservationDetail from './views/ReservationDetail.vue'

// Schedules (برنامه کاری)
import Schedules from './views/Schedules.vue'
import ScheduleForm from './views/ScheduleForm.vue'

const routes = [
  { 
    path: '/login', 
    component: Login,
    meta: { requiresAuth: false }
  },
  { 
    path: '/', 
    component: Dashboard, 
    meta: { requiresAuth: true } 
  },

  // ==================== Customers ====================
  { 
    path: '/customers', 
    component: Customers, 
    meta: { requiresAuth: true } 
  },
  { 
    path: '/customers/new', 
    component: CustomerForm, 
    meta: { requiresAuth: true } 
  },
  { 
    path: '/customers/:id/edit', 
    component: CustomerForm, 
    meta: { requiresAuth: true } 
  },

  // ==================== Lines ====================
  { 
    path: '/lines', 
    component: Lines, 
    meta: { requiresAuth: true } 
  },
  { 
    path: '/lines/new', 
    component: LineForm, 
    meta: { requiresAuth: true } 
  },
  { 
    path: '/lines/:id/edit', 
    component: LineForm, 
    meta: { requiresAuth: true } 
  },

  // ==================== Reservations ====================
  { 
    path: '/reservations', 
    component: Reservations, 
    meta: { requiresAuth: true } 
  },
  { 
    path: '/reservations/new', 
    component: ReservationForm, 
    meta: { requiresAuth: true } 
  },
  { 
    path: '/reservations/:id', 
    component: ReservationDetail, 
    meta: { requiresAuth: true } 
  },
  { 
    path: '/reservations/:id/edit', 
    component: ReservationForm, 
    meta: { requiresAuth: true } 
  },

  // ==================== Schedules ====================
  { 
    path: '/schedules', 
    component: Schedules, 
    meta: { requiresAuth: true } 
  },
  { 
    path: '/schedules/new', 
    component: ScheduleForm, 
    meta: { requiresAuth: true } 
  },
  { 
    path: '/schedules/:id/edit', 
    component: ScheduleForm, 
    meta: { requiresAuth: true } 
  },
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

router.beforeEach(async (to, from, next) => {
  if (to.meta.requiresAuth) {
    try {
      const res = await fetch('/api/auth/me', { 
        credentials: 'include' 
      })
      
      if (!res.ok) {
        return next('/login')
      }
    } catch (err) {
      console.error('Auth check failed:', err)
      return next('/login')
    }
  }
  
  next()
})

export default router