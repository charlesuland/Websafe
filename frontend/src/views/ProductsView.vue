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

const projectsWithProducts = ref([])

const loading = ref(true)
const creatingProduct = ref(false)

const selectedFile = ref(null)

const editingProduct = ref(false)
const showEditMenu = ref(false)
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
      productImages.value[productId] = data.url
    }
  } catch (error) {
    console.error(`Failed to fetch image for product ${productId}:`, error)
  }
}


function getCurrentProductEdits() {
  const product = {
    project_id: editingProduct.value.project_id, 
    name: editingProduct.value.name,
    description: editingProduct.value.description,
    sale_price: parseInt(editingProduct.value.sale_price) || 0,
    shipping_price: parseInt(editingProduct.value.shipping_price) || 0,
    stock: parseInt(editingProduct.value.stock) || 0,
    product_image: null
  }
  return product
}


function openCreate(project) {
  creatingProduct.value = true

  editingProduct.value = {
    project_id: project.id,
    name: '',
    description: '',
    sale_price: 0,
    shipping_price: 0,
    stock: 0
  }
  showEditMenu.value = true
}


function openEdit(product, project) {
  editingProduct.value = { 
    project_id: project.id || project.project_id, 
    ...product
  }
  // Show existing S3 image if available
  if (productImages.value[product.id]) {
    editingProduct.value.product_image = productImages.value[product.id]
  }
  showEditMenu.value = true
}


async function saveProduct() {
  console.log(editingProduct.value.id)
  const productData = getCurrentProductEdits()
  let product = null

  try {
    if (creatingProduct.value) {
      // New product
      product = await apiCreateProduct(productData)

      const projectSection = projectsWithProducts.value.find(
        p => p.project.id === productData.project_id
      )
      projectSection.products.push(product)

    } else {
      // Existing product
      await apiUpdateProduct(editingProduct.value.id, productData)

      product = { ...editingProduct.value }

      const projectSection = projectsWithProducts.value.find(
        p => p.project.id === editingProduct.value.project_id
      )

      const idx = projectSection.products.findIndex(
        p => p.id === editingProduct.value.id
      )

      projectSection.products[idx] = product
    }

    if (selectedFile.value && product?.id) {
      const formData = new FormData()
      formData.append("file", selectedFile.value)

      const res = await fetch(`/api/products/add-product-picture?product_id=${product.id}`, {
        method: "POST",
        headers: getAuthHeaders(),
        body: formData
      })

      if (!res.ok) {
        console.error("Image upload failed:", await res.text())
      } else {
        // Fetch the new image URL after successful upload
        await fetchProductImage(product.id)
      }
    }

    creatingProduct.value = false
    showEditMenu.value = false
    selectedFile.value = null
  } catch (error) {
    console.error("Save product error:", error)
    alert("Failed to save product: " + error.message)
  }
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
    editingProduct.value.product_image = URL.createObjectURL(file)
  }
}

function handleFileSelect(e) {
  const file = e.target.files[0]
  if (file) {
    selectedFile.value = file
    editingProduct.value.product_image = URL.createObjectURL(file)
  }
}

function exitProductDashboard() {
  router.push('/dashboard')
}
</script>

<template>
  <div class="products-page">

    <div class="header">
      <button class="back-button secondary" @click="exitProductDashboard">Back</button>
      <h2>Products</h2>
    </div>

    <div v-if="loading">Loading...</div>


    <div v-for="p in projectsWithProducts" :key="p.project.id" class="project-section">
      <h2>{{ p.project.name }}</h2>
      <button @click="openCreate(p.project)">+ New Product</button>

      <div class="grid">
        <div v-for="product in p.products" :key="product.id" class="card">
          <div v-if="productImages[product.id]" class="product-image-container">
            <img :src="productImages[product.id]" :alt="product.name" class="product-image" />
          </div>
          <div v-else class="product-image-placeholder">No Image</div>
          
          <h3>{{ product.name }}</h3>
          <p>{{ product.description }}</p>
          <strong>${{ (product.sale_price / 100).toFixed(2) }}</strong>

          <div class="actions">
            <button @click="openEdit(product, p.project)">Edit</button>
            <button @click="deleteProduct(product.id, p.project)">Delete</button>
            <button @click="toggleActive(product, p.project)">
              {{ product.is_active ? 'Deactivate' : 'Activate' }}
            </button>
          </div>
        </div>
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
          <p v-if="!editingProduct.product_image">Drag & drop image here or click to upload</p>
          <img 
            v-if="editingProduct.product_image" 
            :src="editingProduct.product_image" 
            alt="Product Preview" 
            class="preview-image"
          />
          <input type="file" @change="handleFileSelect" hidden ref="fileInput" />
        </div>

        <div class="edit-menu-actions">
          <button @click="saveProduct">Save</button>
          <button @click="showEditMenu = false">Cancel</button>
        </div>
      </div>
    </div>

  </div>
</template>

<style scoped>
.products-page {
  padding: 40px;
  background: #f0f2f5;
  min-height: 100vh;
  font-family: "Segoe UI", Roboto, sans-serif;
}

.header {
  display: flex;
  justify-content: start;
  gap: 20px;
  align-items: center;
  margin-bottom: 30px;
}

.header h2 {
  font-size: 2rem;
  color: #333;
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
}

.primary:hover {
  background: #2464d9;
}

.project-section {
  margin-bottom: 40px;
  padding: 20px;
  background: #ffffff;
  border-radius: 12px;
  box-shadow: 0 3px 8px rgba(0, 0, 0, 0.05);
}

.project-section h2 {
  margin-bottom: 15px;
  font-size: 1.5rem;
  color: #444;
}

.project-section button {
  margin-bottom: 20px;
}

.preview-image {
  max-width: 100%;
  max-height: 150px;
  object-fit: contain;
  margin-top: 0px;
  border-radius: 8px;
  border: 1px solid #ccc;
}

button {
    border: none;
    border-radius: 8px;
    padding: 8px 14px;
    cursor: pointer;
  }

.secondary {
  background: #2f7df6;
}

.back-button {
  color: white;
  font-weight: 500;
}

.product-image-container {
  width: 100%;
  height: 200px;
  background-color: #f0f0f0;
  border-radius: 8px 8px 0 0;
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
  height: 200px;
  background-color: #e0e0e0;
  border-radius: 8px 8px 0 0;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #999;
  font-size: 0.9rem;
}

.grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(220px, 1fr));
  gap: 20px;
}

.card {
  background: #ffffff;
  padding: 0;
  border-radius: 10px;
  display: flex;
  flex-direction: column;
  gap: 0;
  border: 1px solid #e0e0e0;
  transition: transform 0.2s, box-shadow 0.2s;
  overflow: hidden;
}

.card:hover {
  transform: translateY(-3px);
  box-shadow: 0 6px 12px rgba(0,0,0,0.1);
}

.card h3 {
  font-size: 1.2rem;
  color: #222;
  padding: 12px 16px 0 16px;
}

.card p {
  font-size: 0.95rem;
  color: #555;
  min-height: 40px;
  padding: 0 16px;
}

.card strong {
  font-size: 1.1rem;
  color: #2f7df6;
  padding: 0 16px;
}

.actions {
  display: flex;
  padding: 0 16px 16px 16px;
  gap: 10px;
  margin-top: auto;
}

.actions button {
  padding: 6px 10px;
  border-radius: 6px;
  border: none;
  cursor: pointer;
  font-size: 0.85rem;
  font-weight: 500;
  transition: background 0.2s, color 0.2s;
}

.actions button:hover {
  opacity: 0.9;
}

.actions button:nth-child(1) {
  background: rgb(152, 152, 152);
  color: #fff;
}

.actions button:nth-child(2) {
  background: #e74c3c;
  color: #fff;
}

.actions button:nth-child(3) {
  background: #2f7df6;
  color: #fff;
}

.edit-menu {
  position: fixed;
  inset: 0;
  background: rgba(0,0,0,0.55);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
}

.edit-menu-content {
  background: white;
  padding: 25px 30px;
  border-radius: 14px;
  width: 500px;
  display: flex;
  flex-direction: column;
  gap: 12px;
  box-shadow: 0 6px 20px rgba(0,0,0,0.2);
}

.edit-menu-content h3 {
  font-size: 1.4rem;
  margin-bottom: 10px;
  color: #333;
}

.edit-menu-content input,
.edit-menu-content textarea {
  padding: 10px;
  border: 1px solid #ccc;
  border-radius: 8px;
  font-size: 0.95rem;
  width: 100%;
}

.edit-menu-content textarea {
  resize: vertical;
  min-height: 60px;
}

.edit-menu-actions {
  display: flex;
  justify-content: space-between;
  margin-top: 10px;
}

.edit-menu-actions button {
  padding: 8px 14px;
  border-radius: 8px;
  border: none;
  font-weight: 500;
  cursor: pointer;
  transition: background 0.2s;
}

.edit-menu-actions button:first-child {
  background: #2f7df6;
  color: #fff;
}

.edit-menu-actions button:first-child:hover {
  background: #2464d9;
}

.edit-menu-actions button:last-child {
  background: #e0e0e0;
  color: #333;
}

.edit-menu-actions button:last-child:hover {
  background: #d6d6d6;
}

.edit-menu-field-header {
  color: black;
  margin-top: 10px;
  margin-bottom: 0px;
}

.drop-zone {
  border: 2px dashed #aaa;
  border-radius: 10px;
  padding: 20px;
  text-align: center;
  cursor: pointer;
  background: #fafafa;
  transition: 0.2s;
}

.drop-zone:hover {
  background: #f0f0f0;
  border-color: #2f7df6;
}
</style>