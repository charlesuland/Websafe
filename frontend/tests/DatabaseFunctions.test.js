// tests/DatabaseFunctions.test.js
// Jest test script for frontend DatabaseFunctions.js
import {
  apiFetchProjects,
  apiCreateProject,
  apiDeleteProject,
  apiFetchAllProducts,
  apiFetchProduct,
  apiFetchAllPublishedProducts,
  apiUpdateProduct,
  apiCreateProduct,
  apiDeleteProduct
} from '../src/DatabaseFunctions.js'

// Mock fetch and getAuthHeaders
global.fetch = jest.fn()
jest.mock('../src/auth.js', () => ({ getAuthHeaders: () => ({ Authorization: 'Bearer testtoken' }) }))

describe('DatabaseFunctions', () => {
  beforeEach(() => {n
    fetch.mockClear()
  })

  it('fetches projects', async () => {
    fetch.mockResolvedValueOnce({ ok: true, json: async () => ([{ id: 1, name: 'Test Project' }]) })
    const projects = await apiFetchProjects()
    expect(fetch).toHaveBeenCalledWith('/api/projects/', expect.any(Object))
    expect(projects[0].name).toBe('Test Project')
  })

  it('creates a project', async () => {
    fetch.mockResolvedValueOnce({ ok: true, json: async () => ({ id: 2, name: 'New Project' }) })
    const project = await apiCreateProject('New Project')
    expect(fetch).toHaveBeenCalledWith('/api/projects/create', expect.any(Object))
    expect(project.name).toBe('New Project')
  })

  it('deletes a project', async () => {
    fetch.mockResolvedValueOnce({ ok: true, json: async () => ({ success: true }) })
    const res = await apiDeleteProject(1)
    expect(fetch).toHaveBeenCalledWith('/api/projects/1/delete', expect.any(Object))
    expect(res.success).toBe(true)
  })

  it('fetches all products for a project', async () => {
    fetch.mockResolvedValueOnce({ ok: true, json: async () => ([{ id: 1, name: 'Product' }]) })
    const products = await apiFetchAllProducts(1)
    expect(fetch).toHaveBeenCalledWith('/api/products/get-all-products?project_id=1', expect.any(Object))
    expect(products[0].name).toBe('Product')
  })

  it('fetches a single product', async () => {
    fetch.mockResolvedValueOnce({ ok: true, json: async () => ({ id: 1, name: 'Product' }) })
    const product = await apiFetchProduct(1)
    expect(fetch).toHaveBeenCalledWith('/api/products/get-product?product_id=1', expect.any(Object))
    expect(product.name).toBe('Product')
  })

  it('fetches all published products', async () => {
    fetch.mockResolvedValueOnce({ ok: true, json: async () => ([{ id: 1, name: 'Published' }]) })
    const products = await apiFetchAllPublishedProducts(1)
    expect(fetch).toHaveBeenCalledWith('/api/products/get-all-published-products?project_id=1', expect.any(Object))
    expect(products[0].name).toBe('Published')
  })

  it('creates a product', async () => {
    fetch.mockResolvedValueOnce({ ok: true, json: async () => ({ id: 3, name: 'New Product' }) })
    const product = await apiCreateProduct({ name: 'New Product' })
    expect(fetch).toHaveBeenCalledWith('/api/products/create-product', expect.any(Object))
    expect(product.name).toBe('New Product')
  })

  it('updates a product', async () => {
    fetch.mockResolvedValueOnce({ ok: true, json: async () => ({ id: 1, name: 'Updated Product' }) })
    const product = await apiUpdateProduct(1, { name: 'Updated Product' })
    expect(fetch).toHaveBeenCalledWith('/api/products/update-product', expect.any(Object))
    expect(product.name).toBe('Updated Product')
  })

  it('deletes a product', async () => {
    fetch.mockResolvedValueOnce({ ok: true, json: async () => ({ success: true }) })
    const res = await apiDeleteProduct(1)
    expect(fetch).toHaveBeenCalledWith('/api/products/delete-product?product_id=1', expect.any(Object))
    expect(res.success).toBe(true)
  })

  it('throws on failed fetch', async () => {
    fetch.mockResolvedValueOnce({ ok: false, text: async () => 'Error' })
    await expect(apiFetchProjects()).rejects.toThrow('Error')
  })
})
