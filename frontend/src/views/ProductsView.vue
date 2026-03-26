<script setup>
import { ref, onMounted } from 'vue'

const products = ref([])
const projects = ref([])
const loading = ref(true)

const editingProduct = ref(null)
const showModal = ref(false)

const token = localStorage.getItem('token')

onMounted(async () => {
  await fetchProducts()
  await fetchProjects()
  loading.value = false
})

async function fetchProducts() {
  const res = await fetch('/api/products', {
    headers: { Authorization: `Bearer ${token}` }
  })
  products.value = await res.json()
}

async function fetchProjects() {
  const res = await fetch('/api/projects', {
    headers: { Authorization: `Bearer ${token}` }
  })
  projects.value = await res.json()
}

function openCreate() {
  editingProduct.value = {
    name: '',
    description: '',
    price_cents: 0
  }
  showModal.value = true
}

function openEdit(product) {
  editingProduct.value = { ...product }
  showModal.value = true
}

async function saveProduct() {
  const method = editingProduct.value.id ? 'PUT' : 'POST'
  const url = editingProduct.value.id
    ? `/api/products/${editingProduct.value.id}`
    : `/api/products`

  const res = await fetch(url, {
    method,
    headers: {
      'Content-Type': 'application/json',
      Authorization: `Bearer ${token}`
    },
    body: JSON.stringify(editingProduct.value)
  })

  if (!res.ok) {
    console.error(await res.text())
    return
  }

  showModal.value = false
  await fetchProducts()
}

async function deleteProduct(id) {
  if (!confirm("Delete this product?")) return

  await fetch(`/api/products/${id}`, {
    method: 'DELETE',
    headers: { Authorization: `Bearer ${token}` }
  })

  products.value = products.value.filter(p => p.id !== id)
}

async function assignToProject(productId, event) {
  const projectId = event.target.value

  await fetch(`/api/projects/${projectId}/products`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      Authorization: `Bearer ${token}`
    },
    body: JSON.stringify({
      product_ids: [productId]
    })
  })
}
</script>

<template>
  <div class="products-page">

    <div class="header">
      <h2>Products</h2>
      <button class="primary" @click="openCreate">+ New Product</button>
    </div>


    <div v-if="loading">Loading...</div>


    <div v-else class="grid">
      <div v-for="product in products" :key="product.id" class="card">

        <div class="card-body">
          <h3>{{ product.name }}</h3>
          <p>{{ product.description }}</p>
          <strong>${{ (product.price_cents / 100).toFixed(2) }}</strong>
        </div>

        <select @change="assignToProject(product.id, $event)">
          <option disabled selected>Assign to project</option>
          <option v-for="p in projects" :key="p.id" :value="p.id">
            {{ p.name }}
          </option>
        </select>

        <div class="actions">
          <button @click="openEdit(product)">Edit</button>
          <button @click="deleteProduct(product.id)">Delete</button>
        </div>
      </div>
    </div>

    <div v-if="showModal" class="modal">
      <div class="modal-content">
        <h3>{{ editingProduct.id ? 'Edit Product' : 'New Product' }}</h3>

        <input v-model="editingProduct.name" placeholder="Name" />
        <textarea v-model="editingProduct.description" placeholder="Description"></textarea>
        <input
          type="number"
          v-model="editingProduct.price_cents"
          placeholder="Price (cents)"
        />

        <div class="modal-actions">
          <button @click="saveProduct">Save</button>
          <button @click="showModal = false">Cancel</button>
        </div>
      </div>
    </div>

  </div>
</template>

<style scoped>
.products-page {
  padding: 30px;
  background: #f5f5f5;
  min-height: 100vh;
}

.header {
  display: flex;
  justify-content: space-between;
  margin-bottom: 20px;
}

.primary {
  background: #2f7df6;
  color: white;
  border: none;
  padding: 10px 16px;
  border-radius: 8px;
}

.grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(220px, 1fr));
  gap: 20px;
}

.card {
  background: white;
  padding: 16px;
  border-radius: 10px;
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.actions {
  display: flex;
  gap: 10px;
}

.modal {
  position: fixed;
  inset: 0;
  background: rgba(0,0,0,0.5);
  display: flex;
  justify-content: center;
  align-items: center;
}

.modal-content {
  background: white;
  padding: 20px;
  border-radius: 10px;
  width: 300px;
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.modal-actions {
  display: flex;
  justify-content: space-between;
}
</style>