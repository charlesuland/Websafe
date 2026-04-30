<script setup>
import { useRoute } from 'vue-router'
import { ref, onMounted, watch, computed } from 'vue'
import SiteRenderer from '@/components/SiteRenderer.vue'

const route = useRoute()
const layout = ref([])
const hasProducts = ref(false)
const projectName = ref('')
const loading = ref(true)
const error = ref(null)
const isShopPage = computed(() => route.params.pageName === 'Shop')

async function loadPage() {
  console.log("Loading page with params:", route.params)
  
  // Wait for route params to be available
  if (!route.params.projectSlug || !route.params.pageName) {
    console.log("Route params not available yet, skipping load")
    return
  }
  
  try {
    loading.value = true
    error.value = null

    const res = await fetch(
      `/api/site/${route.params.projectSlug}/${route.params.pageName}`
    )

    if (!res.ok) {
      throw new Error(`Failed to load page: ${res.status}`)
    }

    const data = await res.json()
    layout.value = data.layout
    hasProducts.value = data.has_products
    projectName.value = data.project_name
  } catch (err) {
    console.error('Error loading published page:', err)
    error.value = err.message
  } finally {
    loading.value = false
  }
}

onMounted(loadPage)
watch([() => route.params.projectSlug, () => route.params.pageName], loadPage)
</script>

<template>
  <div class="published-site">
  

    <div v-if="loading" class="loading-state">
      <div class="spinner"></div>
      <p>Loading page...</p>
    </div>

    <div v-else-if="error" class="error-state">
      <h2>Page Not Found</h2>
      <p>{{ error }}</p>
    </div>

    <main v-else class="site-content">
      <div class="site-title" v-if="isShopPage">
        <h1>{{ projectName }} Shop</h1>
      </div>
      <div class="site-container" :class="{ 'shop-layout': isShopPage }">
        <SiteRenderer
          v-for="comp in layout"
          :key="comp.id"
          :componentData="comp"
          :projectId="route.params.projectSlug"
          :hasProducts="hasProducts"
          :style="{
            gridColumn: comp.col + ' / span ' + comp.colSpan,
            gridRow: comp.row + ' / span ' + comp.rowSpan
          }"
        />
      </div>
    </main>
  </div>
</template>

<style scoped>
.published-site {
  min-height: 100vh;
  background:
    radial-gradient(circle at top left, rgba(37, 99, 235, 0.16), transparent 28%),
    radial-gradient(circle at top right, rgba(16, 185, 129, 0.12), transparent 24%),
    linear-gradient(180deg, #f4f8ff 0%, #eef3f7 48%, #f8fafc 100%);
  font-family: Georgia, 'Times New Roman', serif;
}

.site-header {
  position: sticky;
  top: 0;
  z-index: 1000;
  padding: 20px 0 0;
}

.header-content {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 20px;
}

.site-badge {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 4px;
  padding: 14px 18px;
  border: 1px solid rgba(148, 163, 184, 0.24);
  border-radius: 20px;
  background: rgba(255, 255, 255, 0.72);
  backdrop-filter: blur(18px);
  box-shadow: 0 18px 48px rgba(15, 23, 42, 0.08);
  color: #0f172a;
}

.badge-label {
  font-family: 'Segoe UI', sans-serif;
  font-size: 0.72rem;
  font-weight: 700;
  letter-spacing: 0.12em;
  text-transform: uppercase;
  color: #2563eb;
}

.site-content {
  padding: 26px 0 40px;
  min-height: calc(100vh - 80px);
  display: flex;
  flex-direction: column;
}

.site-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 28px;
  width: 100%;
  box-sizing: border-box;
  flex: 1;
  display: grid;
  grid-template-columns: repeat(12, 1fr);
  grid-auto-rows: 80px;
  min-height: 800px;
  background: linear-gradient(180deg, rgba(255, 255, 255, 0.98), rgba(248, 250, 252, 0.96));
  border: 1px solid rgba(148, 163, 184, 0.22);
  border-radius: 30px;
  box-shadow: 0 28px 80px rgba(15, 23, 42, 0.08);
}

.shop-layout {
  align-content: start;
}

.loading-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  min-height: 50vh;
  gap: 20px;
  color: #334155;
}

.spinner {
  width: 40px;
  height: 40px;
  border: 4px solid #f3f3f3;
  border-top: 4px solid #007bff;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.error-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  min-height: 50vh;
  text-align: center;
  padding: 20px 24px;
}

.error-state h2 {
  color: #dc3545;
  margin-bottom: 10px;
}

.error-state p {
  color: #666;
  margin-bottom: 20px;
}

.site-title {
  max-width: 1200px;
  margin: 0 auto;
  padding: 18px 20px 16px;
  text-align: center;
}

.eyebrow {
  margin: 0 0 8px;
  font-family: 'Segoe UI', sans-serif;
  font-size: 0.78rem;
  font-weight: 700;
  letter-spacing: 0.18em;
  text-transform: uppercase;
  color: #2563eb;
}

.site-title h1 {
  margin: 0;
  font-size: clamp(2.2rem, 5vw, 3.8rem);
  line-height: 0.95;
  color: #0f172a;
}

.subtitle {
  max-width: 620px;
  margin: 14px auto 0;
  font-family: 'Segoe UI', sans-serif;
  font-size: 1rem;
  line-height: 1.6;
  color: #475569;
}

@media (max-width: 768px) {
  .header-pill {
    flex-direction: column;
    align-items: stretch;
  }

  .site-content {
    padding-top: 18px;
  }

  .site-container {
    padding: 15px;
    border-radius: 22px;
  }

  .site-header {
    padding-top: 14px;
  }

  .header-content {
    padding: 0 15px;
  }
}

@media (max-width: 480px) {
  .site-container {
    padding: 10px;
  }

  .site-title h1 {
    font-size: 2rem;
  }
}
</style>
