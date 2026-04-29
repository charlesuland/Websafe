import { apiFetch } from '@/auth.js'

// =========================
// PROJECTS
// =========================

async function apiFetchProjects() {
  const res = await apiFetch('/api/projects/')

  if (!res.ok) throw new Error(await res.text())
  return await res.json()
}

async function apiCreateProject(projectName) {
  const res = await apiFetch('/api/projects/create', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({ name: projectName })
  })

  if (!res.ok) throw new Error(await res.text())
  return await res.json()
}

async function apiDeleteProject(project_id) {
  const res = await apiFetch(`/api/projects/${project_id}/delete`, {
    method: 'DELETE'
  })

  if (!res.ok) throw new Error(await res.text())
  return await res.json()
}

// =========================
// PRODUCTS
// =========================

async function apiFetchProduct(product_id) {
  const res = await apiFetch(`/api/products/get-product?product_id=${product_id}`)

  if (!res.ok) throw new Error(await res.text())
  return await res.json()
}

async function apiFetchAllProducts(projectId) {
  const res = await apiFetch(`/api/products/get-all-products?project_id=${projectId}`)

  if (!res.ok) throw new Error(await res.text())
  return await res.json()
}

async function apiFetchAllPublishedProducts(projectId) {
  const res = await apiFetch(`/api/products/get-all-published-products?project_id=${projectId}`)

  if (!res.ok) throw new Error(await res.text())
  return await res.json()
}

async function apiUpdateProduct(productId, product) {
  const res = await apiFetch(`/api/products/update-product/${productId}`, {
    method: 'PUT',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify(product)
  })

  if (!res.ok) {
    throw new Error(await res.text())
  }

  return await res.json()
}

async function apiCreateProduct(product) {
  const res = await apiFetch('/api/products/create-product', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify(product)
  })

  if (!res.ok) throw new Error(await res.text())
  return await res.json()
}

async function apiDeleteProduct(productId) {
  const res = await apiFetch(`/api/products/delete-product/${productId}`, {
    method: 'DELETE'
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

  const res = await apiFetch(`/api/products/add-product-picture?product_id=${productId}`, {
    method: 'POST',
    body: formData
  })

  if (!res.ok) {
    throw new Error(await res.text())
  }

  return await res.json()
}


// function to fetch data from security/activity
async function apiFetchSecurityActivity(action = null) {
    const params = new URLSearchParams()
    if (action) params.set('action', action)
    
    const res = await apiFetch(`/api/security/activity?${params}`)
    if (!res.ok) throw new Error(await res.text())
    return res.json()
}

/**
 * Check if the current user's vendor account has Stripe payments enabled (payouts_enabled)
 * @returns {Promise<boolean>} true if enabled, false otherwise
 */
export async function apiVendorStripeEnabled() {
  const res = await fetch('/api/vendors/me', {
    method: 'GET',
    headers: {
      ...getAuthHeaders(),
    },
  });
  if (!res.ok) throw new Error(await res.text());
  const vendor = await res.json();
  return !!vendor.payouts_enabled;
}



export async function getProjectSlug(projectId) {
  const res = await fetch(`/api/projects/${projectId}/slug`, {
    headers: { ...getAuthHeaders() }
  })
  if (!res.ok) throw new Error('Failed to fetch slug')
  return res.json()
}

export async function setProjectSlug(projectId, slug) {
  const res = await fetch(`/api/projects/${projectId}/slug`, {
    method: 'PUT',
    headers: {
      'Content-Type': 'application/json',
      ...getAuthHeaders()
    },
    body: JSON.stringify({ slug })
  })

  if (res.status === 409) throw new Error('That URL is already taken — try another name')
  if (res.status === 400) throw new Error('Invalid slug — use letters, numbers, and hyphens only')
  if (!res.ok) throw new Error('Failed to save slug')

  return res.json()
}

export {
    // Project APIs
    apiFetchProjects,
    apiCreateProject,
    apiDeleteProject,

    // Product APIs
    apiFetchAllProducts,
    apiFetchProduct,
    apiFetchAllPublishedProducts,
    apiUpdateProduct,
    apiCreateProduct,
    apiDeleteProduct,

    // Image APIs
    apiUploadProductImage,

    // Security Activity APIs
    apiFetchSecurityActivity
}
