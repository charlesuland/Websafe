const CSRF_COOKIE_NAME = 'csrf_token'
const CSRF_HEADER_NAME = 'X-CSRF-Token'
const SAFE_METHODS = new Set(['GET', 'HEAD', 'OPTIONS', 'TRACE'])

function getCookie(name) {
  const escapedName = name.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')
  const match = document.cookie.match(new RegExp(`(?:^|; )${escapedName}=([^;]*)`))
  return match ? decodeURIComponent(match[1]) : null
}

function getCsrfToken() {
  return getCookie(CSRF_COOKIE_NAME)
}

function buildAuthHeaders(method = 'GET', headers = {}) {
  const normalizedMethod = method.toUpperCase()
  const nextHeaders = { ...headers }

  if (!SAFE_METHODS.has(normalizedMethod)) {
    const csrfToken = getCsrfToken()
    if (csrfToken) {
      nextHeaders[CSRF_HEADER_NAME] = csrfToken
    }
  }

  return nextHeaders
}

async function apiFetch(url, options = {}) {
  const method = (options.method || 'GET').toUpperCase()
  const headers = buildAuthHeaders(method, options.headers || {})

  const response = await fetch(url, {
    ...options,
    method,
    credentials: 'include',
    headers,
  })

  if (
    response.status === 401 &&
    !options._skipRefresh &&
    url !== '/api/token' &&
    url !== '/api/auth/refresh'
  ) {
    const refreshRes = await apiFetch('/api/auth/refresh', {
      method: 'POST',
      _skipRefresh: true,
    })

    if (refreshRes.ok) {
      return fetch(url, {
        ...options,
        method,
        credentials: 'include',
        headers: buildAuthHeaders(method, options.headers || {}),
      })
    }
  }

  return response
}

async function ensureAuthenticated() {
  let res = await apiFetch('/api/auth/session')
  if (res.ok) {
    const data = await res.json()
    if (data.authenticated) {
      return true
    }
  }

  const refreshRes = await apiFetch('/api/auth/refresh', { method: 'POST' })
  if (!refreshRes.ok) {
    return false
  }

  res = await apiFetch('/api/auth/session')
  if (!res.ok) {
    return false
  }

  const data = await res.json()
  return Boolean(data.authenticated)
}

async function logoutSession() {
  await apiFetch('/api/auth/logout', { method: 'POST' })
}

export {
  apiFetch,
  ensureAuthenticated,
  getCsrfToken,
  logoutSession,
}
