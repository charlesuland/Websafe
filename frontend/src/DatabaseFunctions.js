import { getAuthHeaders } from '@/auth.js'

async function apiFetchProjects() {
    const res = await fetch('/api/projects/', {
        headers: {
            ...getAuthHeaders()
        },
    })
    if (!res.ok)
        throw new Error(await res.text())

    return await res.json()
}

async function apiCreateProject(projectName) {
    const res = await fetch('/api/projects/create', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            ...getAuthHeaders()
        },
        body: JSON.stringify({
            name: projectName
        })
    })
    if (!res.ok) 
        throw new Error(await res.text())

    return await res.json()
}

async function apiDeleteProject(project_id) {
    const res = await fetch(`/api/projects/${project_id}/delete`, {
        method: 'DELETE',
        headers: {
            ...getAuthHeaders()
        }
    })
    if (!res.ok) 
        throw new Error(await res.text())

    return await res.json()
}



async function apiFetchProduct(product_id) {
    const res = await fetch(`/api/products/get-product?product_id=${product_id}`, {
        method: 'GET',
        headers: { 
            ...getAuthHeaders()
        }
    })
    if (!res.ok) 
        throw new Error(await res.text())

    return await res.json()
}

async function apiFetchAllProducts(projectId) {
    const res = await fetch(`/api/products/get-all-products?project_id=${projectId}`, {
        method: 'GET',
        headers: { 
            ...getAuthHeaders()
        }
    })
    if (!res.ok) 
        throw new Error(await res.text())

    return await res.json()
}

async function apiFetchAllPublishedProducts(projectId) {
    const res = await fetch(`/api/products/get-all-published-products?project_id=${projectId}`, {
        method: 'GET',
        headers: { 
            ...getAuthHeaders()
        }
    })
    if (!res.ok) 
        throw new Error(await res.text())

    return await res.json()
}

async function apiUpdateProduct(productId, product) {
    const res = await fetch(`/api/products/update-product`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            ...getAuthHeaders()
        },
        body: JSON.stringify({
            product_id: { val: productId },
            product_in: product
        })
    })

    if (!res.ok)
        throw new Error(await res.text())

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
  if (!res.ok) 
    throw new Error(await res.text())

  return await res.json()
}


async function apiDeleteProduct(productId) {
    const res = await fetch(`/api/products/delete-product?product_id=${productId}`, {
        method: 'DELETE',
        headers: { 
            'Content-Type': 'application/json',
            ...getAuthHeaders()
        }
    })

    if (!res.ok) {
        throw new Error(await res.text())
    }

    return await res.json()
}

async function apiUploadImage() {
    const res = await fetch('/api/products/upload-image', {
        method: 'POST',
        headers: {
            ...getAuthHeaders()
        }
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
    
    const res = await fetch(`/api/security/activity?${params}`, {
        headers: getAuthHeaders()
    })
    if (!res.ok) throw new Error(await res.text())
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
    apiUploadImage,

    // Security Activity APIs
    apiFetchSecurityActivity
}