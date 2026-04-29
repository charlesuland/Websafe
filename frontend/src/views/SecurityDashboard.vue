<template>
  <main class="security-page" aria-labelledby="security-title">
    <header class="page-header">
      <button class="back-btn" type="button" @click="router.back()">Back</button>
      <div>
        <h1 id="security-title">Security</h1>
        <p class="sub">Monitor account authentication, project, and product activity.</p>
      </div>
    </header>

    <section class="metrics" aria-label="Security summary">
      <article class="metric">
        <span class="metric-label">Total logins</span>
        <span class="metric-val">{{ stats.logins }}</span>
      </article>
      <article class="metric">
        <span class="metric-label">Failed login attempts</span>
        <span class="metric-val" :class="{ warn: stats.failures > 0 }">{{ stats.failures }}</span>
      </article>
      <article class="metric">
        <span class="metric-label">Site changes</span>
        <span class="metric-val" :class="stats.changes > 0 ? 'ok' : ''">
          {{ stats.changes }}
        </span>
      </article>
    </section>

    <section class="card" aria-labelledby="activity-title">
      <div class="card-header">
        <h2 id="activity-title" class="card-title">Recent activity</h2>
        <div class="filters" role="toolbar" aria-label="Filter activity">
          <button
            v-for="f in filters"
            :key="f.value"
            type="button"
            class="filter-pill"
            :class="{ active: activeFilter === f.value }"
            :aria-pressed="activeFilter === f.value"
            @click="setFilter(f.value)"
          >
            {{ f.label }}
          </button>
        </div>
      </div>

      <div v-if="loading" class="state-msg" role="status" aria-live="polite">Loading activity…</div>
      <div v-else-if="error" class="state-msg error" role="alert">{{ error }}</div>
      <div v-else-if="filtered.length === 0" class="state-msg" role="status">No activity found.</div>

      <div v-else class="table-wrap" tabindex="0" aria-label="Security activity table">
        <table class="log-table">
          <caption class="sr-only">
            Security activity log with event, details, IP address, and local date and time.
          </caption>
          <thead>
            <tr>
              <th scope="col">Event</th>
              <th scope="col">Details</th>
              <th scope="col">IP address</th>
              <th scope="col">Date / Time</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="log in filtered" :key="log.id">
              <td>
                <span class="dot" :class="dotClass(log.action)" aria-hidden="true"></span>
                <span class="dot-text">{{ formatAction(log.action) }}</span>
              </td>
              <td class="muted">{{ formatDetails(log) }}</td>
              <td class="mono">{{ log.ip_address ?? '—' }}</td>
              <td class="muted">{{ formatDate(log.created_at) }}</td>
            </tr>
          </tbody>
        </table>
      </div>
    </section>
  </main>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { apiFetchSecurityActivity } from '@/DatabaseFunctions.js'

const router = useRouter()

const logs = ref([])
const loading = ref(true)
const error = ref(null)
const activeFilter = ref('all')

const filters = [
  { label: 'All', value: 'all' },
  { label: 'Auth', value: 'auth' },
  { label: 'Projects', value: 'project' },
  { label: 'Products', value: 'product' },
  { label: 'Alerts', value: 'failed_login' },
]

onMounted(async () => {
  try {
    logs.value = await apiFetchSecurityActivity()
  } catch (e) {
    error.value = e.message
  } finally {
    loading.value = false
  }
})

const filtered = computed(() => {
  if (activeFilter.value === 'all') return logs.value
  if (activeFilter.value === 'auth') {
    return logs.value.filter(log => ['login', 'failed_login', 'logout', 'password_change'].includes(log.action))
  }
  if (activeFilter.value === 'project') {
    return logs.value.filter(log => log.action.startsWith('project_'))
  }
  if (activeFilter.value === 'product') {
    return logs.value.filter(log => log.action.startsWith('product_'))
  }
  return logs.value.filter(log => log.action === activeFilter.value)
})

const stats = computed(() => ({
  logins: logs.value.filter(log => log.action === 'login').length,
  failures: logs.value.filter(log => log.action === 'failed_login').length,
  changes: logs.value.filter(log => log.action.startsWith('project_') || log.action.startsWith('product_')).length,
}))

function setFilter(value) {
  activeFilter.value = value
}

function dotClass(action) {
  return {
    'dot-success': action === 'login',
    'dot-danger': action === 'failed_login',
    'dot-info': !['login', 'failed_login'].includes(action),
  }
}

function formatAction(action) {
  const map = {
    login: 'Login',
    failed_login: 'Failed login',
    logout: 'Logout',
    password_change: 'Password changed',
    project_created: 'Project created',
    project_saved: 'Project saved',
    project_deleted: 'Project deleted',
    project_published: 'Project published',
    product_created: 'Product created',
    product_updated: 'Product saved',
    product_deleted: 'Product deleted',
  }
  return map[action] ?? action
}

function formatDetails(log) {
  if (log.action === 'login' || log.action === 'failed_login') {
    return parseBrowser(log.details)
  }
  return log.details || '—'
}

function parseBrowser(ua) {
  if (!ua) return '—'
  if (ua.includes('Edg')) return 'Edge'
  if (ua.includes('Chrome')) return 'Chrome'
  if (ua.includes('Firefox')) return 'Firefox'
  if (ua.includes('Safari')) return 'Safari'
  return ua
}

function formatDate(value) {
  if (!value) return '—'

  const date = parseServerDate(value)
  if (Number.isNaN(date.getTime())) return '—'

  return date.toLocaleString(undefined, {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
    hour: 'numeric',
    minute: '2-digit',
  })
}

function parseServerDate(value) {
  if (value instanceof Date) return value
  if (typeof value !== 'string') return new Date(value)

  const normalized = value.includes('T') ? value : value.replace(' ', 'T')
  const hasTimezone = /[zZ]$|[+-]\d{2}:\d{2}$/.test(normalized)

  return new Date(hasTimezone ? normalized : `${normalized}Z`)
}
</script>

<style scoped>
.security-page {
  padding: 2rem 2.5rem 3rem;
  max-width: 980px;
  margin: 0 auto;
  color: #d8e4f2;
}

.page-header {
  display: flex;
  align-items: center;
  gap: 1rem;
  margin-bottom: 2rem;
}

.page-header h1 {
  margin: 0;
  color: #f8fbff;
  font-size: 1.65rem;
  font-weight: 700;
}

.sub {
  margin: 0;
  color: #b6c8dd;
  font-size: 0.95rem;
}

.back-btn {
  padding: 0.7rem 1rem;
  border: 1px solid #5b7492;
  border-radius: 10px;
  background: #122133;
  color: #f8fbff;
  cursor: pointer;
  font-size: 0.95rem;
  font-weight: 600;
}

.back-btn:hover {
  background: #1b2f47;
}

.metrics {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 14px;
  margin-bottom: 2rem;
}

.metric {
  min-height: 112px;
  padding: 1rem 1.1rem;
  border: 1px solid #2a3d58;
  border-radius: 14px;
  background: linear-gradient(180deg, #142235 0%, #0f1825 100%);
  display: flex;
  flex-direction: column;
  gap: 0.4rem;
}

.metric-label {
  color: #bbccdf;
  font-size: 0.8rem;
  letter-spacing: 0.02em;
}

.metric-val {
  color: #b9f5d8;
  font-size: 1.6rem;
  font-weight: 700;
}

.metric-val.ok {
  color: #b9f5d8;
}

.metric-val.warn {
  color: #ffd08a;
}

.card {
  overflow: hidden;
  border: 1px solid #2a3d58;
  border-radius: 16px;
  background: #101926;
  box-shadow: 0 18px 36px rgba(0, 0, 0, 0.22);
}

.card-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 1rem;
  padding: 1rem 1.25rem;
  border-bottom: 1px solid #27364d;
}

.card-title {
  margin: 0;
  color: #f8fbff;
  font-size: 1rem;
  font-weight: 700;
}

.filters {
  display: flex;
  flex-wrap: wrap;
  gap: 0.45rem;
}

.filter-pill {
  padding: 0.45rem 0.85rem;
  border: 1px solid #516885;
  border-radius: 999px;
  background: #172538;
  color: #edf4fb;
  cursor: pointer;
  font-size: 0.85rem;
  font-weight: 600;
}

.filter-pill:hover {
  background: #213550;
}

.filter-pill.active {
  border-color: #f0b14a;
  background: #f0b14a;
  color: #1a1406;
}

.state-msg {
  padding: 2rem;
  color: #c6d5e6;
  font-size: 0.95rem;
  text-align: center;
}

.state-msg.error {
  color: #ffb1a8;
  background: rgba(127, 29, 29, 0.24);
}

.table-wrap {
  overflow-x: auto;
}

.log-table {
  width: 100%;
  min-width: 720px;
  border-collapse: collapse;
}

.log-table th,
.log-table td {
  padding: 0.95rem 1.25rem;
  border-top: 1px solid #27364d;
  text-align: left;
  vertical-align: top;
  font-size: 0.95rem;
}

.log-table th {
  background: #162334;
  color: #c1d3e7;
  font-size: 0.8rem;
  text-transform: uppercase;
  letter-spacing: 0.04em;
}

.log-table tbody tr:nth-child(even) {
  background: rgba(255, 255, 255, 0.02);
}

.log-table tbody tr:hover {
  background: rgba(240, 177, 74, 0.08);
}

.dot {
  display: inline-block;
  width: 0.6rem;
  height: 0.6rem;
  margin-right: 0.6rem;
  border-radius: 999px;
}

.dot-success {
  background: #59d89a;
}

.dot-danger {
  background: #ff8f86;
}

.dot-info {
  background: #8db8ff;
}

.dot-text {
  color: #f8fbff;
  font-weight: 600;
}

.muted {
  color: #d4e0ee;
  line-height: 1.45;
}

.mono {
  color: #f3f7fc;
  font-family: ui-monospace, SFMono-Regular, Menlo, monospace;
}

.back-btn:focus-visible,
.filter-pill:focus-visible,
.table-wrap:focus-visible {
  outline: 3px solid #f8c35d;
  outline-offset: 3px;
}

.sr-only {
  position: absolute;
  width: 1px;
  height: 1px;
  padding: 0;
  margin: -1px;
  overflow: hidden;
  clip: rect(0, 0, 0, 0);
  white-space: nowrap;
  border: 0;
}

@media (max-width: 900px) {
  .security-page {
    padding: 1.25rem 1rem 2rem;
  }

  .page-header {
    flex-direction: column;
    align-items: flex-start;
  }

  .metrics {
    grid-template-columns: 1fr;
  }

  .card-header {
    flex-direction: column;
    align-items: flex-start;
  }
}
</style>
