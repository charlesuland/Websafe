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
import AnalyticsView from '@/views/AnalyticsView.vue'

import SettingsView from '@/views/SettingsView.vue'
import OrdersView from '@/views/OrdersView.vue'
import { ensureAuthenticated } from '@/auth.js'

import CheckoutView from '@/views/CheckoutView.vue'
import BuySubscriptionPage from '@/views/BuySubscriptionPage.vue'



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
        path: 'orders',
        component: OrdersView
      },
      {
        path: 'analytics',
        component: AnalyticsView
      },
      {
        path: 'security',
        component: SecurityDashboard
      },
      {
        path:'settings/:projectId',
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
    path: '/checkout/:projectId',
    component: CheckoutView
  }, {
    path: '/subscriptions/',
    component: BuySubscriptionPage
  }
]
const router = createRouter({
  history: createWebHistory(),
  routes
})


// client side navigation guard
router.beforeEach(async (to) => {
  const requiresAuth = to.matched.some(record => record.meta.requiresAuth)

  if (requiresAuth) {
    const authenticated = await ensureAuthenticated()
    if (!authenticated) {
      return '/login'
    }
  }
})

export default router
