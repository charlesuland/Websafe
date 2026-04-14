import { createRouter, createWebHistory } from 'vue-router'
import LandingPage from '../views/LandingPage.vue'
import LoginView from '../views/LoginView.vue'
import RegisterView from '@/views/RegisterView.vue'
import DashboardView from '@/views/DashboardView.vue'
import PublishedPage from '@/views/PublishedPage.vue'
import EditorView from '@/views/EditorView.vue'
import ProductsView from '@/views/ProductsView.vue'
import AboutUsView from '@/views/AboutUsView.vue'

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
    path: '/dashboard',
    component: DashboardView,
    meta: {requiresAuth: true} //marks a route as protected so you can't use URL to get into it
  },
  {
    path: '/about',
    component: AboutUsView
  },
  {
    path: '/products',
    component: ProductsView,
    meta: {requiresAuth: true}
  },
  {
    path: '/editor/:projectId',
    component: EditorView,
    meta: {requiresAuth: true}
  },
  {
    path: '/site/:projectSlug/:pageName',
    component: PublishedPage
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

  if (requiresAuth && !token) {
    return '/login'
  }
})





export default router