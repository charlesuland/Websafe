<script setup>
import { ref, onMounted } from 'vue'
import { getAuthHeaders } from '@/auth.js'
import { 
  apiFetchAllProducts,
  apiFetchAllPublishedProducts,
  apiCreateProduct,
  apiFetchProjects,
  apiUpdateProduct,
  apiDeleteProduct
} from '@/DatabaseFunctions.js'
import router from '@/router'
import ProductCard from '@/components/ProductCard.vue'

const projectsWithProducts = ref([])
const loading = ref(true)
const selectedFile = ref(null)
const editingProduct = ref(null)
const showEditMenu = ref(false)
const currentImagePreview = ref(null) // For displaying current or selected image
const token = localStorage.getItem('token')

const productImages = ref({}) // Cache for product image URLs

onMounted(async () => {
  const userProjects = await apiFetchProjects()
  const projectsData = []

  for (const project of userProjects) {
    const products = await apiFetchAllProducts(project.id)
    projectsData.push({ 
      project,
      products
    })
  }

  projectsWithProducts.value = projectsData
  
  // Fetch images for all products
  for (const projectData of projectsData) {
    for (const product of projectData.products) {
      await fetchProductImage(product.id)
    }
  }
  
  loading.value = false;
})


async function fetchProductImage(productId) {
  try {
    const res = await fetch(`/api/products/get-product-image?product_id=${productId}`, {
      headers: getAuthHeaders()
    })
    if (res.ok) {
      const data = await res.json()
      productImages.value[productId] = data.image_url
    }
  } catch (error) {
    console.error(`Failed to fetch image for product ${productId}:`, error)
  }
}


function getCurrentProductEdits() {
  const source = editingProduct.value || {}
  return {
    project_id: source.project_id,
    name: source.name,
    description: source.description,
    sale_price: parseInt(source.sale_price) || 0,
    shipping_price: parseInt(source.shipping_price) || 0,
    alt_text: source.alt_text,
    stock: parseInt(source.stock) || 0
  }
}

function getCurrentProductUpdatePayload() {
  const source = editingProduct.value || {}
  return {
    name: source.name,
    description: source.description,
    sale_price: parseInt(source.sale_price) || 0,
    shipping_price: parseInt(source.shipping_price) || 0,
    alt_text: source.alt_text,
    stock: parseInt(source.stock) || 0
  }
}


function openCreate(project) {
  editingProduct.value = {
    project_id: project.id,
    id: null,
    name: '',
    description: '',
    sale_price: 0,
    shipping_price: 0,
    alt_text: '',
    stock: 0
  }
  currentImagePreview.value = null
  showEditMenu.value = true
}


function openEdit(product, project) {
  editingProduct.value = { 
    project_id: project.id || project.project_id, 
    ...product
  }
  // Show existing S3 image if available
  currentImagePreview.value = productImages.value[product.id] || null
  showEditMenu.value = true
}


async function saveProduct() {
  const productData = getCurrentProductEdits()
  const isNewProduct = !editingProduct.value?.id
  let product = null

  try {
    if (isNewProduct) {
      product = await apiCreateProduct(productData)
      const projectSection = projectsWithProducts.value.find(
        p => p.project.id === productData.project_id
      )
      if (projectSection) {
        projectSection.products.push(product)
      }
    } else {
      product = await apiUpdateProduct(editingProduct.value.id, getCurrentProductUpdatePayload())
      const projectSection = projectsWithProducts.value.find(
        p => p.project.id === editingProduct.value.project_id
      )
      if (projectSection) {
        const idx = projectSection.products.findIndex(
          p => p.id === editingProduct.value.id
        )
        if (idx !== -1) {
          projectSection.products[idx] = product
        }
      }
    }

    if (selectedFile.value && product?.id) {
      await uploadProductImage(product.id)
    }

    showEditMenu.value = false
    selectedFile.value = null
    currentImagePreview.value = null
  } catch (error) {
    console.error("Save product error:", error.message)
    alert("Failed to save product: " + error.message)
  }
}


async function uploadProductImage(productId) {
  const formData = new FormData()
  formData.append("file", selectedFile.value)

  const res = await fetch(
    `/api/products/add-product-picture?product_id=${productId}&alt_text=${encodeURIComponent(editingProduct.value.alt_text || '')}`,
    {
      method: "POST",
      headers: { ...getAuthHeaders() },
      body: formData
    }
  )

  if (!res.ok) {
    throw new Error(await res.text())
  }

  await fetchProductImage(productId)
}


async function toggleActive(product, project) {
  const newStatus = !product.is_active
  await fetch(`/api/products/${product.id}/toggle-active`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json', ...getAuthHeaders() },
    body: JSON.stringify({ is_active: newStatus })
  })

  product.is_active = newStatus
}


async function deleteProduct(productId, project) {
  if (!confirm("Delete this product?"))
    return

  const res = await apiDeleteProduct(productId)

  const projectSection = projectsWithProducts.value.find(p => p.project.id === project.id)
  projectSection.products = projectSection.products.filter(p => p.id !== productId)
}


function handleDrop(e) {
  const file = e.dataTransfer.files[0]
  if (file) {
    selectedFile.value = file
    currentImagePreview.value = URL.createObjectURL(file)
  }
}


function handleFileSelect(e) {
  const file = e.target.files[0]
  if (file) {
    selectedFile.value = file
    currentImagePreview.value = URL.createObjectURL(file)
  }
}
</script>



<template>
  <div class="products-content">
    <div class="content-header">
      <h2>Products</h2>
    </div>

    <div v-if="loading">Loading...</div>


    <div v-for="p in projectsWithProducts" :key="p.project.id" class="project-section">
      <h2>{{ p.project.name }}</h2>
      <button @click="openCreate(p.project)">+ New Product</button>

      <div class="grid">
        <ProductCard
          v-for="product in p.products"
          :key="product.id"
          :product="product"
          :image-url="productImages[product.id]"
          :project="p.project"
          @edit="openEdit"
          @delete="deleteProduct"
          @toggle-active="toggleActive"
        />
      </div>
    </div>

    <div v-if="showEditMenu" class="edit-menu">
      <div class="edit-menu-content">
        <h3>{{ editingProduct.project_id ? 'Edit Product' : 'New Product' }}</h3>

        <h4 class="edit-menu-field-header">Name</h4>
        <input v-model="editingProduct.name" placeholder="Name" />

        <h4 class="edit-menu-field-header">Description</h4>
        <textarea v-model="editingProduct.description" placeholder="Description"></textarea>

        <h4 class="edit-menu-field-header">Sale Price</h4>
        <input
          type="number"
          v-model="editingProduct.sale_price"
          placeholder="Price (cents)"
        />

        <h4 class="edit-menu-field-header">Shipping Price</h4>
        <input
          type="number"
          v-model="editingProduct.shipping_price"
          placeholder="Shipping Price (cents)"
        />

        <h4 class="edit-menu-field-header">Stock Available</h4>
        <input
          type="number"
          v-model="editingProduct.stock"
          placeholder="Stock"
        />

        <div 
          class="drop-zone"
          @dragover.prevent
          @click="$refs.fileInput.click()"
          @drop.prevent="handleDrop"
        >
          <p v-if="!currentImagePreview">Drag & drop image here or click to upload</p>
          <img 
            v-if="currentImagePreview" 
            :src="currentImagePreview" 
            alt="Product Preview" 
            class="preview-image"
          />
          <input type="file" @change="handleFileSelect" hidden ref="fileInput" />
          
        </div>
        <h4 v-if="currentImagePreview" class="edit-menu-field-header">Alt Text</h4>
          <input 
            v-if="currentImagePreview"
            type="text"
            v-model="editingProduct.alt_text"
            placeholder="Alt text for the image"

          >

        <div class="edit-menu-actions">
          <button @click="saveProduct">Save</button>
          <button @click="showEditMenu = false">Cancel</button>
        </div>
      </div>
    </div>

  </div>
</template>

<style scoped>
.products-content {
  padding: 30px;
}

.content-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 25px;
  color: rgb(90, 140, 255);
}

.content-header h2 {
  margin: 0;
  font-size: clamp(1.6rem, 2vw, 2rem);
}

.primary {
  background: #2f7df6;
  color: white;
  border: none;
  padding: 10px 20px;
  border-radius: 8px;
  cursor: pointer;
  font-weight: 500;
  transition: background 0.2s;
  min-width: 140px;
}

.primary:hover {
  background: #2464d9;
}

.project-section {
  margin-bottom: 40px;
  padding: 22px;
  background: #ffffff;
  border-radius: 16px;
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.07);
}

.project-section h2 {
  margin-bottom: 16px;
  font-size: clamp(1.4rem, 1.6vw, 1.8rem);
  color: #222;
}

.project-section button {
  margin-bottom: 18px;
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
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 18px;
}

.edit-menu {
  position: fixed;
  inset: 0;
  padding: 24px;
  background: rgba(15, 23, 42, 0.55);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
}

.edit-menu-content {
  background: #ffffff;
  padding: 24px;
  border-radius: 18px;
  width: min(92vw, 560px);
  max-height: min(90vh, 740px);
  display: flex;
  flex-direction: column;
  gap: 16px;
  box-shadow: 0 20px 60px rgba(15, 23, 42, 0.15);
  overflow-y: auto;
}

.edit-menu-content h3 {
  font-size: 1.5rem;
  margin-bottom: 0;
  color: #111827;
}

.edit-menu-content input,
.edit-menu-content textarea {
  padding: 14px 16px;
  border: 1px solid #d1d5db;
  border-radius: 12px;
  font-size: 1rem;
  width: 100%;
  background: #f9fafb;
  box-sizing: border-box;
}

.edit-menu-content textarea {
  resize: vertical;
  min-height: 100px;
}

.edit-menu-actions {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
  justify-content: flex-end;
  margin-top: 10px;
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
  color: #111827;
  margin-top: 10px;
  margin-bottom: 0.5rem;
  font-weight: 600;
}

.drop-zone {
  border: 2px dashed #cbd5e1;
  border-radius: 14px;
  padding: 18px;
  min-height: 160px;
  text-align: center;
  cursor: pointer;
  background: #f8fafc;
  display: flex;
  flex-direction: column;
  justify-content: center;
  gap: 12px;
  transition: background 0.2s ease, border-color 0.2s ease;
}

.drop-zone:hover {
  background: #eef2ff;
  border-color: #2563eb;
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