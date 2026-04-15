<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()

const activeTab = ref('projects')

function navigateTo(tab) {
  activeTab.value = tab

  router.push(`/${tab}`)

  if (tab === 'projects') {
    router.push('/dashboard')
  } else if (tab === 'products') {
    router.push('/dashboard/products')
  } else if (tab === 'analytics') {
    // Future analytics page
  } else if (tab === 'settings') {
    router.push('/dashboard/settings')
  } else if (tab === 'security') {
    router.push('/security')
  }
}

// Set active tab based on current route
import { onMounted } from 'vue'
import { useRoute } from 'vue-router'

const route = useRoute()

onMounted(() => {
  const path = route.path
  if (path === '/dashboard')          activeTab.value = 'projects'
  else if (path === '/dashboard/products')  activeTab.value = 'products'
  else if (path === '/dashboard/security')  activeTab.value = 'security'
  else if (path === '/dashboard/settings')  activeTab.value = 'settings'
})
</script>

<template>
  <div class="dashboard-layout">
    <header class="topbar">
      <h1>WebSafe</h1>
      <div class="user">Account</div>
    </header>

    <div class="body">
      <aside class="sidebar">
        <button
          :class="{ active: activeTab === 'dashboard' }"
          @click="navigateTo('dashboard')"
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

      <main class="content">
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

.topbar {
  height: 60px;
  background: #111;
  color: white;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 20px;
}

.body {
  display: flex;
  flex: 1;
}

.sidebar {
  width: 220px;
  background: #1e1e1e;
  padding: 20px;
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.sidebar button {
  background: transparent;
  color: white;
  border: none;
  text-align: left;
  padding: 10px;
  cursor: pointer;
  border-radius: 4px;
  transition: background-color 0.2s;
}

.sidebar button:hover {
  background: rgba(255, 255, 255, 0.1);
}

.sidebar button.active {
  background: rgb(90, 140, 255);
  color: white;
}

.content {
  flex: 1;
  background: #f5f5f5;
  overflow-y: auto;
}
</style>