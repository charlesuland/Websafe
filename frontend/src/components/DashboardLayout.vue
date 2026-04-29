```vue
<script setup>
import { ref, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { logoutSession } from '@/auth.js'

const router = useRouter()
const route = useRoute()

const activeTab = ref('projects')

function navigateTo(tab) {
  activeTab.value = tab

  if (tab === 'projects') {
    router.push('/dashboard')
  } else if (tab === 'products') {
    router.push('/dashboard/products')
  } else if (tab === 'analytics') {
    // Future analytics page
  } else if (tab === 'settings') {
    router.push('/dashboard/settings')
  } else if (tab === 'security') {
    router.push('/dashboard/security')
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

async function logout() {
  await logoutSession()
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
</style>