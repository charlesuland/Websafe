<script setup>
import { useRoute, useRouter } from 'vue-router'
import { ref, onMounted, watch, computed } from 'vue'
import SiteRenderer from '@/components/SiteRenderer.vue'
import ProductCardBlock from '@/components/blocks/ProductCardBlock.vue'

const route = useRoute()
const router = useRouter()
const layout = ref([])
const products = ref([])
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

    if (isShopPage.value) {
      // Load products for shop page
      const res = await fetch(`/api/projects/${route.params.projectSlug}/products`)
      if (!res.ok) {
        throw new Error(`Failed to load products: ${res.status}`)
      }
      const data = await res.json()
      products.value = data.products || []
      hasProducts.value = true
      projectName.value = data.project_name || ''
      layout.value = [] // No layout for shop page
    } else {
      // Load regular page layout
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
      products.value = []
    }
  } catch (err) {
    console.error('Error loading published page:', err)
    error.value = err.message
  } finally {
    loading.value = false
  }
}

function goBack() {
  router.push('/dashboard')
}

onMounted(loadPage)
watch([() => route.params.projectSlug, () => route.params.pageName], loadPage)
</script>

<template>
  <div class="published-site">
    <!-- Minimal header for navigation back to dashboard -->
    <header class="site-header">
      <div class="header-content">
        <button @click="goBack" class="back-button">
          ← Back to Dashboard
        </button>
      </div>
    </header>

    <!-- Loading state -->
    <div v-if="loading" class="loading-state">
      <div class="spinner"></div>
      <p>Loading page...</p>
    </div>

    <!-- Error state -->
    <div v-else-if="error" class="error-state">
      <h2>Page Not Found</h2>
      <p>{{ error }}</p>
      <button @click="goBack" class="back-button">Return to Dashboard</button>
    </div>

    <!-- Main content -->
    <main v-else class="site-content">
      <div v-if="isShopPage" class="shop-container">
        <h1 class="shop-title">{{ projectName }} Shop</h1>
        <div class="products-grid">
          <ProductCardBlock
            v-for="product in products"
            :key="product.id"
            :productId="product.id"
            :name="product.name"
            :description="product.description"
            :price="product.sale_price"
            :imageUrl="product.image_url"
            :altText="product.alt_text"
            :inStock="product.stock > 0"
          />
        </div>
      </div>
      <div v-else class="site-container">
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
  background-color: #ffffff;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
}

.site-header {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(10px);
  border-bottom: 1px solid #e0e0e0;
  z-index: 1000;
  padding: 8px 0;
}

.header-content {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 20px;
}

.back-button {
  background: #f8f9fa;
  border: 1px solid #ddd;
  padding: 6px 12px;
  border-radius: 6px;
  cursor: pointer;
  font-size: 14px;
  color: #333;
  transition: background-color 0.2s ease;
}

.back-button:hover {
  background: #e9ecef;
}

.site-content {
  padding-top: 60px; /* Account for fixed header */
  min-height: calc(100vh - 60px);
  display: flex;
  flex-direction: column;
}

.site-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
  width: 100%;
  box-sizing: border-box;
  flex: 1;
  display: grid;
  grid-template-columns: repeat(12, 1fr);
  grid-auto-rows: 80px;
  min-height: 800px;
  background-color: #ffffff;
}

.loading-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  min-height: 50vh;
  gap: 20px;
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
  padding: 20px;
}

.error-state h2 {
  color: #dc3545;
  margin-bottom: 10px;
}

.error-state p {
  color: #666;
  margin-bottom: 20px;
}

.shop-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
}

.shop-title {
  text-align: center;
  margin-bottom: 30px;
  font-size: 2rem;
  color: #333;
}

.products-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 20px;
  margin-top: 20px;
}

/* Responsive design */
@media (max-width: 768px) {
  .site-content {
    padding-top: 50px;
  }

  .site-container {
    padding: 15px;
  }

  .site-header {
    padding: 6px 0;
  }

  .header-content {
    padding: 0 15px;
  }

  .back-button {
    padding: 5px 10px;
    font-size: 13px;
  }
}

@media (max-width: 480px) {
  .site-container {
    padding: 10px;
  }
}
</style>