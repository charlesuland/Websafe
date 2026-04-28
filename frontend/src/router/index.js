import { createRouter, createWebHistory } from 'vue-router'
import LandingPage from '../views/LandingPage.vue'
import LoginView from '../views/LoginView.vue'
import RegisterView from '@/views/RegisterView.vue'
import DashboardLayout from '@/components/DashboardLayout.vue'
import DashboardView from '@/views/DashboardView.vue'
import ProductsView from '@/views/ProductsView.vue'
import PublishedPage from '@/views/PublishedPage.vue'
import EditorView from '@/views/EditorView.vue'

import SecurityDashboard from '@/views/SecurityDashboard.vue'
import AboutUsView from '@/views/AboutUsView.vue'

import SettingsView from '@/views/SettingsView.vue'

import CheckoutView from '@/views/CheckoutView.vue'



const routes = [
  {
    path: '/',
    component: LandingPage
  },
  {
    path: '/login',
    component: LoginView
  },
  {
    path: '/register',
    component: RegisterView
  },
  {
    path: '/about',
    component: AboutUsView
  },
  {
    path: '/dashboard',
    component: DashboardLayout,
    meta: {requiresAuth: true},
    children: [
      {
        path: '',
        component: DashboardView
      },
      {
        path: 'products',
        component: ProductsView
      },
      {
        path: 'security',
        component: SecurityDashboard
      },
      {
        path:'settings',
        component: SettingsView
      },
    ]
  },
  {
    path: '/editor/:projectId',
    component: EditorView,
    meta: {requiresAuth: true}
  },
  {
    path: '/site/:projectSlug/:pageName',
    component: PublishedPage
  },
  {
    path: '/checkout/:routerId',
    component: CheckoutView
  }
]
const router = createRouter({
  history: createWebHistory(),
  routes
})


// client side navigation guard
router.beforeEach((to) => {
  const requiresAuth = to.matched.some(record => record.meta.requiresAuth)
  const token = localStorage.getItem('token')

  if (requiresAuth) {
    if (!token) return '/login'

    // Check expiry without a library
    try {
      const payload = JSON.parse(atob(token.split('.')[1]))
      if (payload.exp * 1000 < Date.now()) {
        localStorage.removeItem('token')
        return '/login'
      }
    } catch {
      // Malformed token
      localStorage.removeItem('token')
      return '/login'
    }
  }
})

export default router