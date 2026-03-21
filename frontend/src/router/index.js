import { createRouter, createWebHistory } from 'vue-router'
import LandingPage from '../views/LandingPage.vue'
import LoginView from '../views/LoginView.vue'
import RegisterView from '@/views/RegisterView.vue'
import DashboardView from '@/views/DashboardView.vue'
import PublishedPage from '@/views/PublishedPage.vue'
import EditorView from '@/views/EditorView.vue'

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
    component: DashboardView
  },
  {
    path: '/editor/:projectId',
    component: EditorView
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

export default router