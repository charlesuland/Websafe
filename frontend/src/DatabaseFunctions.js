import { getAuthHeaders } from '@/auth.js'

// =========================
// PROJECTS
// =========================

async function apiFetchProjects() {
  const res = await fetch('/api/projects/', {
    headers: { ...getAuthHeaders() }
  })

  if (!res.ok) throw new Error(await res.text())
  return await res.json()
}

async function apiCreateProject(projectName) {
  const res = await fetch('/api/projects/create', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      ...getAuthHeaders()
    },
    body: JSON.stringify({ name: projectName })
  })

  if (!res.ok) throw new Error(await res.text())
  return await res.json()
}

async function apiDeleteProject(project_id) {
  const res = await fetch(`/api/projects/${project_id}/delete`, {
    method: 'DELETE',
    headers: { ...getAuthHeaders() }
  })

  if (!res.ok) throw new Error(await res.text())
  return await res.json()
}

// =========================
// PRODUCTS
// =========================

async function apiFetchProduct(product_id) {
  const res = await fetch(`/api/products/get-product?product_id=${product_id}`, {
    headers: { ...getAuthHeaders() }
  })

  if (!res.ok) throw new Error(await res.text())
  return await res.json()
}

async function apiFetchAllProducts(projectId) {
  const res = await fetch(`/api/products/get-all-products?project_id=${projectId}`, {
    headers: { ...getAuthHeaders() }
  })

  if (!res.ok) throw new Error(await res.text())
  return await res.json()
}

async function apiFetchAllPublishedProducts(projectId) {
  const res = await fetch(`/api/products/get-all-published-products?project_id=${projectId}`, {
    headers: { ...getAuthHeaders() }
  })

  if (!res.ok) throw new Error(await res.text())
  return await res.json()
}

async function apiUpdateProduct(productId, product) {
  const res = await fetch(`/api/products/update-product/${productId}`, {
    method: 'PUT',
    headers: {
      'Content-Type': 'application/json',
      ...getAuthHeaders()
    },
    body: JSON.stringify(product)
  })

  if (!res.ok) {
    throw new Error(await res.text())
  }

  return await res.json()
}

async function apiCreateProduct(product) {
  const res = await fetch('/api/products/create-product', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      ...getAuthHeaders()
    },
    body: JSON.stringify(product)
  })

  if (!res.ok) throw new Error(await res.text())
  return await res.json()
}

async function apiDeleteProduct(productId) {
  const res = await fetch(`/api/products/delete-product/${productId}`, {
    method: 'DELETE',
    headers: { ...getAuthHeaders() }
  })

  if (!res.ok) {
    throw new Error(await res.text())
  }

  return await res.json()
}

async function apiUploadProductImage(productId, file, altText = '') {
  const formData = new FormData()
  formData.append('file', file)
  formData.append('alt_text', altText)

  const res = await fetch(`/api/products/add-product-picture?product_id=${productId}`, {
    method: 'POST',
    headers: {
      ...getAuthHeaders()
    },
    body: formData
  })

  if (!res.ok) {
    throw new Error(await res.text())
  }

  return await res.json()
}

export {
  apiFetchProjects,
  apiCreateProject,
  apiDeleteProject,

  apiFetchAllProducts,
  apiFetchProduct,
  apiFetchAllPublishedProducts,
  apiUpdateProduct,
  apiCreateProduct,
  apiDeleteProduct,
  apiUploadProductImage
}
