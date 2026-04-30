<script setup>
import { ref, onMounted } from 'vue'
import { apiFetch } from '@/auth.js'
import { 
  apiFetchAllProducts,
  apiCreateProduct,
  apiFetchProjects,
  apiUpdateProduct,
  apiDeleteProduct,
  apiUploadProductImage
} from '@/DatabaseFunctions.js'
import router from '@/router'
import ProductCard from '@/components/ProductCard.vue'
import CreateConnectCard from '@/components/CreateConnectCard.vue'

const projectsWithProducts = ref([])
const loading = ref(true)
const selectedFile = ref(null)
const editingProduct = ref(null)
const showEditMenu = ref(false)
const currentImagePreview = ref(null)
const vendorPayoutsEnabled = ref(false)

onMounted(async () => {
  try {
    const userProjects = await apiFetchProjects()
    const projectsData = await Promise.all(
      userProjects.map(async (project) => {
        const products = await apiFetchAllProducts(project.id)
        return { project, products }
      })
    )
    projectsWithProducts.value = projectsData
  } catch (error) {
    console.error("Error loading products:", error)
    alert("Failed to load products.")
    router.push('/dashboard')
  } finally {
    loading.value = false
  }

  const vendorRes = await apiFetch('/api/vendors/me')
  if (vendorRes.ok) {
    const vendor = await vendorRes.json()
    vendorPayoutsEnabled.value = vendor.payouts_enabled
}
})

function getPayload(source) {
  return {
    project_id: source.project_id,
    name: source.name,
    description: source.description,

    sale_price: Math.max(0, Math.round((source.sale_price || 0) * 100)),
    //shipping_price: Math.max(0, Math.round((source.shipping_price || 0) * 100)),

    alt_text: source.alt_text,
    stock: Math.max(0, parseInt(source.stock) || 0)
  }
}

function openCreate(project) {
  editingProduct.value = {
    project_id: project.id,
    name: '',
    description: '',
    sale_price: 0,
    shipping_price: 0,
    alt_text: '',
    stock: 0
  }
  selectedFile.value = null
  currentImagePreview.value = null
  showEditMenu.value = true
}

function openEdit(product, project) {
  editingProduct.value = { 
    ...product, 
    project_id: project.id,
    sale_price: (product.sale_price || 0) / 100,
    //shipping_price: (product.shipping_price || 0) / 100,
    stock: Math.max(0, product.stock || 0)
  }

  selectedFile.value = null
  currentImagePreview.value = product.image_url || null
  showEditMenu.value = true
}


function clampPrice(field) {
  if (editingProduct.value[field] < 0) {
    editingProduct.value[field] = 0
  } else {
    // Round to 2 decimal places
    editingProduct.value[field] = Math.round(editingProduct.value[field] * 100) / 100
  }
}

function clampStock() {
  if (editingProduct.value.stock < 0) {
    editingProduct.value.stock = 0
  } else {
    editingProduct.value.stock = Math.floor(editingProduct.value.stock)
  }
}


async function saveProduct() {
  try {
    let product

    const payload = getPayload(editingProduct.value)

    // CREATE
    if (!editingProduct.value.id) {
      product = await apiCreateProduct(payload)

      const section = projectsWithProducts.value.find(
        p => p.project.id === product.project_id
      )
      section?.products.push(product)
    }

    // UPDATE
    else {
      product = await apiUpdateProduct(
        editingProduct.value.id,
        payload
      )

      const section = projectsWithProducts.value.find(
        p => p.project.id === product.project_id
      )

      const idx = section?.products.findIndex(p => p.id === product.id)
      if (idx !== -1) section.products[idx] = product
    }

    // IMAGE UPLOAD
    if (selectedFile.value && product?.id) {
      const updated = await apiUploadProductImage(
        product.id,
        selectedFile.value,
        editingProduct.value.alt_text || ''
      )

      const section = projectsWithProducts.value.find(
        p => p.project.id === product.project_id
      )

      const idx = section?.products.findIndex(p => p.id === product.id)
      if (idx !== -1) section.products[idx] = updated
    }

    showEditMenu.value = false
    selectedFile.value = null
    currentImagePreview.value = null

  } catch (err) {
    console.error("Save failed:", err)
    alert("Save failed")
  }
}

async function togglePublished(product) {
  if (!vendorPayoutsEnabled.value) {
    alert('You must connect a Stripe account before publishing products.')
    return
  }

  const newStatus = !product.is_published

  await apiFetch(`/api/products/${product.id}/toggle-published`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ is_published: newStatus })
  })

  product.is_published = newStatus
}

async function deleteProduct(productId, project) {
  if (!confirm("Delete this product?")) return

  await apiDeleteProduct(productId)

  const section = projectsWithProducts.value.find(p => p.project.id === project.id)
  section.products = section.products.filter(p => p.id !== productId)
}

function setPreview(file) {
  if (currentImagePreview.value) URL.revokeObjectURL(currentImagePreview.value)
  currentImagePreview.value = URL.createObjectURL(file)
}

function handleDrop(e) {
  const file = e.dataTransfer.files[0]
  if (!file?.type.startsWith('image')) return alert("Image only")
  selectedFile.value = file
  setPreview(file)
}

function handleFileSelect(e) {
  const file = e.target.files[0]
  if (!file?.type.startsWith('image')) return alert("Image only")
  selectedFile.value = file
  setPreview(file)
}
</script>

<template>
  <main class="products-content" aria-labelledby="products-title">
    <CreateConnectCard />
    <header class="content-header">
      <div>
        <h2 id="products-title">Products</h2>
        <p class="intro-text">Manage product catalogs, stock, pricing, and images for each project.</p>
      </div>
    </header>

    <div v-if="loading" class="loading-state" role="status" aria-live="polite">Loading products…</div>

    <section
      v-for="p in projectsWithProducts"
      :key="p.project.id"
      class="project-section"
      :aria-labelledby="`project-products-${p.project.id}`"
    >
      <div class="project-section-header">
        <div>
          <h3 :id="`project-products-${p.project.id}`" class="project-section-title">{{ p.project.name }}</h3>
          <p class="project-section-sub">Product management for this storefront.</p>
        </div>
        <button class="primary" type="button" @click="openCreate(p.project)">Create Product</button>
      </div>

      <div v-if="p.products.length === 0" class="empty-products" role="status">
        No products yet for this project.
      </div>

      <div v-else class="grid" :aria-label="`${p.project.name} products`">
        <ProductCard
          v-for="product in p.products"
          :key="product.id"
          :product="product"
          :project="p.project"
          @edit="() => openEdit(product, p.project)"
          @delete="() => deleteProduct(product.id, p.project)"
          @toggle-published="() => togglePublished(product)"
        />
      </div>
    </section>


    <!-- Edit/Create Product Modal -->
    <div v-if="showEditMenu" class="edit-menu" role="presentation">
      <div
        class="edit-menu-content"
        role="dialog"
        aria-modal="true"
        :aria-labelledby="editingProduct.id ? 'edit-product-title' : 'new-product-title'"
      >
        <h3 :id="editingProduct.id ? 'edit-product-title' : 'new-product-title'">
          {{ editingProduct.id ? 'Edit Product' : 'New Product' }}
        </h3>

        <label class="field-group">
          <span class="edit-menu-field-header">Product Name</span>
          <input v-model="editingProduct.name" placeholder="Name" />
        </label>

        <label class="field-group">
          <span class="edit-menu-field-header">Product Description</span>
          <textarea v-model="editingProduct.description" placeholder="Description"></textarea>
        </label>

        <label class="field-group">
          <span class="edit-menu-field-header">Sale Price ($)</span>
          <input
            type="number"
            min="0"
            step="0.01"
            v-model.number="editingProduct.sale_price"
            @input="clampPrice('sale_price')"
            placeholder="Price ($)"
          />
        </label>

        <!-- <label class="field-group">
          <span class="edit-menu-field-header">Shipping Price ($)</span>
          <input
            type="number"
            min="0"
            step="0.01"
            v-model.number="editingProduct.shipping_price"
            @input="clampPrice('shipping_price')"
            placeholder="Shipping Price ($)"
          />
        </label> -->

        <label class="field-group">
          <span class="edit-menu-field-header">Stock Available</span>
          <input
            type="number"
            min="0"
            step="1"
            v-model.number="editingProduct.stock"
            @input="clampStock('stock')"
            placeholder="Stock"
          />
        </label>

        <button
          type="button"
          class="drop-zone"
          @dragover.prevent
          @click="$refs.fileInput.click()"
          @drop.prevent="handleDrop"
        >
          <p v-if="!currentImagePreview">Drag and drop an image here or press to upload.</p>
          <img
            v-if="currentImagePreview"
            :src="currentImagePreview"
            :alt="editingProduct.alt_text"
            class="preview-image"
          />
          <input type="file" @change="handleFileSelect" hidden ref="fileInput" />
        </button>

        <label v-if="currentImagePreview" class="field-group">
          <span class="edit-menu-field-header">Alt Text</span>
          <input
            type="text"
            v-model="editingProduct.alt_text"
            placeholder="Alt text for the image"
          />
        </label>

        <div class="edit-menu-actions">
          <button type="button" class="save-action" @click="saveProduct">Save</button>
          <button type="button" class="cancel-action" @click="showEditMenu = false">Cancel</button>
        </div>
      </div>
    </div>
  </main>
</template>

<style scoped>
.products-content {
  padding: 2rem 2.5rem 3rem;
  color: #d8e4f2;
}

.content-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 1rem;
  margin-bottom: 1.5rem;
}

.content-header h2 {
  margin: 0;
  font-size: clamp(1.7rem, 2vw, 2rem);
  color: #f8fbff;
}

.intro-text {
  margin: 0.45rem 0 0;
  color: #b8cade;
  font-size: 0.98rem;
}

.primary {
  background: #1d61c6;
  color: white;
  border: 1px solid #4f9bff;
  padding: 0.8rem 1rem;
  border-radius: 10px;
  cursor: pointer;
  font-weight: 700;
  transition: background 0.2s;
  min-width: 140px;
}

.primary:hover {
  background: #2464d9;
}

.primary:focus-visible,
.drop-zone:focus-visible,
.edit-menu-actions button:focus-visible {
  outline: 3px solid #f8c35d;
  outline-offset: 3px;
}

.project-section {
  margin-bottom: 40px;
  padding: 22px;
  background: linear-gradient(180deg, #132031 0%, #0f1825 100%);
  border: 1px solid #2a3d58;
  border-radius: 16px;
  box-shadow: 0 18px 36px rgba(0, 0, 0, 0.22);
}

.project-section-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 1rem;
  margin-bottom: 18px;
}

.project-section-title {
  margin: 0;
  font-size: clamp(1.4rem, 1.6vw, 1.8rem);
  color: #f8fbff;
}

.project-section-sub {
  margin: 0.45rem 0 0;
  color: #b8cade;
  font-size: 0.94rem;
}

.preview-image {
  width: 100%;
  max-height: 180px;
  object-fit: contain;
  margin-top: 0;
  border-radius: 10px;
  border: 1px solid #ddd;
}

button {
  border: none;
  border-radius: 8px;
  padding: 8px 14px;
  cursor: pointer;
}

.product-image-container {
  width: 300px;
  aspect-ratio: 4 / 3;
  max-height: 240px;
  background-color: #f8f9fb;
  border-radius: 12px 12px 0 0;
  overflow: hidden;
  display: flex;
  align-items: center;
  justify-content: center;
}

.product-image {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.product-image-placeholder {
  width: 100%;
  aspect-ratio: 4 / 3;
  background-color: #eaeef2;
  border-radius: 12px 12px 0 0;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #7d8a99;
  font-size: 0.95rem;
}

.grid {
  display: grid;
  justify-content: start;
  grid-template-columns: repeat(3, 1fr);
  gap: 18px;
}

.loading-state,
.empty-products {
  color: #c6d4e5;
  text-align: center;
  padding: 1.5rem;
}

.edit-menu {
  position: fixed;
  inset: 0;
  padding: 24px;

  background: rgba(2, 6, 23, 0.75);
  backdrop-filter: blur(6px);

  display: flex;
  justify-content: center;
  align-items: center;

  z-index: 1000;
}

.edit-menu-content {
  background: linear-gradient(180deg, #132031 0%, #0f1825 100%);
  border: 1px solid #2a3d58;

  border-radius: 18px;
  width: min(92vw, 560px);
  max-height: min(90vh, 760px);

  padding: 24px;

  display: flex;
  flex-direction: column;
  gap: 14px;

  box-shadow: 0 24px 60px rgba(0, 0, 0, 0.5);

  overflow-y: auto;
}

.edit-menu-content h3 {
  margin: 0;

  font-size: 1.5rem;
  font-weight: 700;

  color: #f8fbff;
}

.field-group {
  display: flex;
  flex-direction: column;
  gap: 0.45rem;
}

.edit-menu-content input,
.edit-menu-content textarea {
  padding: 12px 14px;

  border: 1px solid #2a3d58;
  border-radius: 12px;

  font-size: 1rem;

  background: #0b1220;
  color: #f8fbff;

  outline: none;
  transition: border-color 0.2s ease, box-shadow 0.2s ease;
}

.edit-menu-content input:focus,
.edit-menu-content textarea:focus {
  border-color: #60a5fa;
  box-shadow: 0 0 0 3px rgba(96, 165, 250, 0.25);
}

.edit-menu-content textarea {
  resize: vertical;
  min-height: 100px;
}

.edit-menu-actions {
  display: flex;
  gap: 10px;
  justify-content: flex-end;
  margin-top: 6px;
}

.edit-menu-actions button {
  padding: 12px 18px;
  border-radius: 12px;
  border: none;
  font-weight: 600;
  cursor: pointer;
  transition: background 0.2s ease;
}

.edit-menu-actions button:first-child {
  background: #2563eb;
  color: #fff;
}

.edit-menu-actions button:first-child:hover {
  background: #1d4ed8;
}

.edit-menu-actions button:last-child {
  background: #f3f4f6;
  color: #111827;
}

.edit-menu-actions button:last-child:hover {
  background: #e5e7eb;
}

.edit-menu-field-header {
  color: #b8cade;
  font-weight: 600;
  font-size: 0.9rem;
}

.drop-zone {
  border: 2px dashed #334155;
  border-radius: 14px;

  padding: 18px;
  min-height: 160px;

  background: rgba(255, 255, 255, 0.03);
  color: #b8cade;

  display: flex;
  align-items: center;
  justify-content: center;
  text-align: center;

  cursor: pointer;
  transition: all 0.2s ease;
}

.drop-zone:hover {
  border-color: #60a5fa;
  background: rgba(96, 165, 250, 0.08);
  color: #f8fbff;
}

.save-action {
  background: #16a34a;
  color: #ffffff;
}

.save-action:hover {
  background: #15803d;
}

.cancel-action {
  background: #1e293b;
  color: #f8fbff;
  border: 1px solid #334155;
}

.cancel-action:hover {
  background: #334155;
}

@media (max-width: 800px) {
  .products-content {
    padding: 18px;
  }

  .project-section {
    padding: 18px;
  }

  .actions {
    gap: 12px;
  }

  .edit-menu-content {
    width: min(96vw, 560px);
    padding: 20px;
  }
}

@media (max-width: 520px) {
  .content-header,
  .project-section-header,
  .edit-menu-actions {
    flex-direction: column;
    align-items: stretch;
  }

  .content-header {
    gap: 12px;
  }

  .primary {
    width: 100%;
  }

  .edit-menu-actions button {
    width: 100%;
  }
}
</style>
