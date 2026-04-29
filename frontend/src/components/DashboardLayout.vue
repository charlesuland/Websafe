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
  background: #0b1220;
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
  height: 72px;
  background: #0f172a;
  color: #e2e8f0;

  display: flex;
  align-items: center;
  justify-content: space-between;

  padding: 0 28px;

  border-bottom: 1px solid #1e293b;
}

.topbar h1 {
  font-size: 1.3rem;
  font-weight: 700;
  letter-spacing: 0.5px;
}


.body {
  display: flex;
  flex: 1;
  overflow: hidden;
}


.sidebar {
  width: 230px;
  background: linear-gradient(180deg, #0f172a 0%, #020617 100%);
  border-right: 1px solid #1e293b;

  padding: 20px 14px;

  display: flex;
  flex-direction: column;
  gap: 6px;
}

.sidebar button {
  background: transparent;
  color: #cbd5f5;

  border: none;
  text-align: left;

  padding: 12px 14px;
  border-radius: 10px;

  font-weight: 500;
  font-size: 0.95rem;

  cursor: pointer;

  transition: all 0.2s ease;
}

.sidebar button:hover {
  background: rgba(59, 130, 246, 0.15);
  color: #ffffff;
}

.sidebar button.active {
  background: linear-gradient(90deg, #2563eb, #1d4ed8);
  color: #ffffff;

  box-shadow: 0 4px 12px rgba(37, 99, 235, 0.35);
}

.sidebar button:focus-visible {
  outline: 2px solid #60a5fa;
  outline-offset: 2px;
}


.content {
  flex: 1;

  background: #020617;
  color: #e2e8f0;

  overflow-y: auto;

  padding: 20px 24px;
}


.logout-btn {
  background: transparent;
  color: #e2e8f0;

  border: 1px solid #334155;

  padding: 8px 16px;
  border-radius: 10px;

  cursor: pointer;
  font-size: 0.9rem;
  font-weight: 500;

  transition: all 0.2s ease;
}

.logout-btn:hover {
  background: rgba(239, 68, 68, 0.15);
  border-color: #ef4444;
  color: #fecaca;
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