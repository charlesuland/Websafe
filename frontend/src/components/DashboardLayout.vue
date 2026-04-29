```vue
<script setup>
import { ref, onMounted } from 'vue'
import { useRouter, useRoute, useRoute } from 'vue-router'
import { onMounted } from 'vue'
import { apiFetchProjects } from '@/DatabaseFunctions'
import { logoutSession } from '@/auth.js'

const router = useRouter()
const route = useRoute()
const route = useRoute()

const activeTab = ref('projects')

// Project picker modal state
const showProjectPicker = ref(false)
const projects = ref([])
const loadingProjects = ref(false)

function navigateTo(tab) {
  activeTab.value = tab

  if (tab === 'projects') {
    router.push('/dashboard')
  } else if (tab === 'products') {
    router.push('/dashboard/products')
  } else if (tab === 'analytics') {
    // Future analytics page
  } else if (tab === 'settings') {
    openProjectPicker()
  } else if (tab === 'security') {
    router.push('/dashboard/security')
  }
}

async function openProjectPicker() {
  showProjectPicker.value = true
  loadingProjects.value = true
  try {
    projects.value = await apiFetchProjects()
  } catch (err) {
    console.error('Failed to load projects:', err)
  } finally {
    loadingProjects.value = false
  }
}

function selectProject(projectId) {
  showProjectPicker.value = false
  router.push(`/dashboard/settings/${projectId}`)
}

function closePicker() {
  showProjectPicker.value = false
  // If we weren't already on settings, don't change active tab
  const path = route.path
  if (!path.startsWith('/dashboard/settings')) {
    activeTab.value = path === '/dashboard' ? 'projects'
      : path === '/dashboard/products' ? 'products'
      : path === '/dashboard/security' ? 'security'
      : 'projects'
  }
}

onMounted(() => {
  const path = route.path

  if (path === '/dashboard')
    activeTab.value = 'projects'
  else if (path === '/dashboard/products')
    activeTab.value = 'products'
  else if (path === '/dashboard/security')
    activeTab.value = 'security'
  else if (path === '/dashboard/settings')
    activeTab.value = 'settings'
})

function logout() {
  localStorage.removeItem('token')
  router.push('/')
}
</script>

<template>
  <div class="dashboard-layout">
    
    <!-- Skip Link -->
    <a href="#main-content" class="skip-link">Skip to main content</a>

    <header class="topbar" role="banner">
      <h1>WebSafe</h1>
      <div class="user">
        <button class="logout-btn" @click="logout" aria-label="Log out of account">
          Log Out
        </button>
      </div>
    </header>

    <div class="body">
      <aside class="sidebar" role="navigation">
        <button
          :class="{ active: activeTab === 'projects' }"
          @click="navigateTo('projects')"
        >
          Projects
        </button>

        <button
          :class="{ active: activeTab === 'analytics' }"
          @click="navigateTo('analytics')"
        >
          Analytics
        </button>

        <button
          :class="{ active: activeTab === 'settings' }"
          @click="navigateTo('settings')"
        >
          Settings
        </button>

        <button
          :class="{ active: activeTab === 'products' }"
          @click="navigateTo('products')"
        >
          E-Commerce Products
        </button>

        <button
          :class="{ active: activeTab === 'security' }"
          @click="navigateTo('security')"
        >
          Security
        </button>
      </aside>

      <main id="main-content" class="content" role="main" tabindex="-1">
        <router-view />
      </main>
    </div>

    <!-- Project picker modal -->
    <div v-if="showProjectPicker" class="picker-overlay" @click.self="closePicker">
      <div class="picker-modal">
        <div class="picker-header">
          <span class="picker-title">Which project are you configuring?</span>
          <button class="picker-close" @click="closePicker">✕</button>
        </div>

        <div v-if="loadingProjects" class="picker-loading">
          Loading projects...
        </div>

        <div v-else-if="projects.length === 0" class="picker-empty">
          You don't have any projects yet.
        </div>

        <div v-else class="picker-list">
          <button
            v-for="project in projects"
            :key="project.id"
            class="picker-item"
            @click="selectProject(project.id)"
          >
            <span class="picker-item-name">{{ project.name }}</span>
            <span class="picker-item-status" :class="project.is_live ? 'live' : 'draft'">
              {{ project.is_live ? 'Live' : 'Draft' }}
            </span>
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.dashboard-layout {
  display: flex;
  flex-direction: column;
  height: 100vh;
}

.skip-link {
  position: absolute;
  top: -40px;
  left: 10px;
  background: #ffffff;
  color: #000000;
  padding: 8px 12px;
  z-index: 1000;
  border-radius: 4px;
  text-decoration: none;
}

.skip-link:focus {
  top: 10px;
}

 
.topbar {
  height: 80px;
  background: #0b0b0b;
  color: #EAEAEA;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 10px 30px;
}
 
.body {
  display: flex;
  flex: 1;
}
 
.sidebar {
  width: 220px;
  background: #001a3d;
  padding: 20px;
  display: flex;
  flex-direction: column;
  gap: 10px;
}
 
.sidebar button {
  background: transparent;
  color: #E0E0E0;
  border: none;
  text-align: left;
  padding: 12px;
  cursor: pointer;
  border-radius: 6px;
  font-weight: 500;
  transition: background-color 0.2s, color 0.2s;
}
 
.sidebar button:hover {
  background: rgba(255, 255, 255, 0.15);
  color: #ffffff;
}
 
.sidebar button.active {
  background: #2563eb;
  color: #ffffff;
}

.sidebar button:focus-visible {
  outline: 2px solid #60a5fa;
  outline-offset: 2px;
}
 
.content {
  flex: 1;
  background-color: #0a0a0a;
  color: #EAEAEA;
  overflow-y: auto;
}

.logout-btn {
  background: transparent;
  color: #EAEAEA;
  border: 1px solid rgba(255, 255, 255, 0.6);
  padding: 8px 16px;
  border-radius: 8px;
  cursor: pointer;
  font-size: 0.9rem;
  transition: background 0.2s, border-color 0.2s;
}
 
.logout-btn:hover {
  background: rgba(255, 255, 255, 0.15);
  border-color: #ffffff;
}

.logout-btn:focus-visible {
  outline: 2px solid #60a5fa;
  outline-offset: 2px;
}

button:focus-visible {
  outline: 2px solid #60a5fa;
  outline-offset: 2px;
}
 
/* ── project picker modal ── */
.picker-overlay {
  position: fixed;
  inset: 0;
  background: rgba(15, 23, 42, 0.4);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}
 
.picker-modal {
  background: #fff;
  border-radius: 14px;
  width: 360px;
  max-height: 480px;
  display: flex;
  flex-direction: column;
  box-shadow: 0 20px 60px rgba(15, 23, 42, 0.18);
  overflow: hidden;
}
 
.picker-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 18px 20px 14px;
  border-bottom: 1px solid #e2e8f0;
}
 
.picker-title {
  font-size: 0.95rem;
  font-weight: 600;
  color: #0f172a;
}
 
.picker-close {
  border: none;
  background: none;
  font-size: 0.9rem;
  color: #94a3b8;
  cursor: pointer;
  padding: 2px 6px;
  border-radius: 4px;
}
 
.picker-close:hover {
  background: #f1f5f9;
  color: #475569;
}
 
.picker-loading,
.picker-empty {
  padding: 32px 20px;
  text-align: center;
  font-size: 0.9rem;
  color: #64748b;
}
 
.picker-list {
  overflow-y: auto;
  padding: 10px;
  display: flex;
  flex-direction: column;
  gap: 6px;
}
 
.picker-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 12px 14px;
  border: 1px solid #e2e8f0;
  border-radius: 10px;
  background: #fff;
  cursor: pointer;
  transition: border-color 0.15s, background 0.15s;
  text-align: left;
}
 
.picker-item:hover {
  border-color: #2563eb;
  background: #eff6ff;
}
 
.picker-item-name {
  font-size: 0.92rem;
  font-weight: 500;
  color: #0f172a;
}
 
.picker-item-status {
  font-size: 0.75rem;
  font-weight: 600;
  padding: 3px 8px;
  border-radius: 99px;
  text-transform: uppercase;
  letter-spacing: 0.06em;
}
 
.picker-item-status.live {
  background: #dcfce7;
  color: #15803d;
}
 
.picker-item-status.draft {
  background: #f1f5f9;
  color: #64748b;
}
</style>