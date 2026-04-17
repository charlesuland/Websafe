<template>
  <div class="security-page">

    <div class="page-header">
      <button class="back-btn" @click="router.back()">← Back</button>
      <div>
        <h1>Security</h1>
        <p class="sub">Monitor your account login activity</p>
      </div>
    </div>

    <div class="metrics">
      <div class="metric">
        <span class="metric-label">Total logins</span>
        <span class="metric-val">{{ stats.logins }}</span>
      </div>
      <div class="metric">
        <span class="metric-label">Failed attempts</span>
        <span class="metric-val" :class="{ warn: stats.failures > 0 }">{{ stats.failures }}</span>
      </div>
      <div class="metric">
        <span class="metric-label">Account status</span>
        <span class="metric-val" :class="stats.failures > 0 ? 'warn' : 'ok'">
          {{ stats.failures > 0 ? 'Review' : 'Secure' }}
        </span>
      </div>
    </div>

    <div class="card">
      <div class="card-header">
        <span class="card-title">Recent activity</span>
        <div class="filters">
          <button
            v-for="f in filters"
            :key="f.value"
            class="filter-pill"
            :class="{ active: activeFilter === f.value }"
            @click="setFilter(f.value)"
          >
            {{ f.label }}
          </button>
        </div>
      </div>

      <div v-if="loading" class="state-msg">Loading...</div>
      <div v-else-if="error" class="state-msg error">{{ error }}</div>
      <div v-else-if="filtered.length === 0" class="state-msg">No activity found.</div>

      <table v-else class="log-table">
        <thead>
          <tr>
            <th>Event</th>
            <th>Browser</th>
            <th>IP address</th>
            <th>Time</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="log in filtered" :key="log.id">
            <td>
              <span class="dot" :class="dotClass(log.action)"></span>
              <span class ="dot-text">{{ formatAction(log.action) }}</span>
            </td>
            <td class="muted">{{ parseBrowser(log.details) }}</td>
            <td class="mono">{{ log.ip_address ?? '—' }}</td>
            <td class="muted">{{ formatDate(log.created_at) }}</td>
          </tr>
        </tbody>
      </table>
    </div>

  </div>
</template>

<script setup>
  import { ref, computed, onMounted } from 'vue'
  import { useRouter } from 'vue-router'
  import { apiFetchSecurityActivity } from '@/DatabaseFunctions.js'

  const router = useRouter()

  const logs = ref([])
  const loading = ref(true)
  const error = ref(null)
  const activeFilter = ref('all')

  const filters = [
    { label: 'All', value: 'all' },
    { label: 'Auth', value: 'login' },
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
    return logs.value.filter(l => l.action === activeFilter.value)
  })

  const stats = computed(() => ({
    logins: logs.value.filter(l => l.action === 'login').length,
    failures: logs.value.filter(l => l.action === 'failed_login').length,
  }))

  function setFilter(val) {
    activeFilter.value = val
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
    }
    return map[action] ?? action
  }


  //NOT WORKING ONLY DOES CHROME
  function parseBrowser(ua) {
    if (!ua) return '—'
    if (ua.includes('Chrome')) return 'Chrome'
    if (ua.includes('Firefox')) return 'Firefox'
    if (ua.includes('Safari')) return 'Safari'
    if (ua.includes('Edg')) return 'Edge'
    return 'Unknown'
  }

  function formatDate(iso) {
    return new Date(iso).toLocaleString(undefined, {
      month: 'short', day: 'numeric',
      hour: '2-digit', minute: '2-digit'
    })
  }
</script>
<style scoped>


.security-page {
  padding: 2rem 2.5rem;
  max-width: 900px;
  margin: 0 auto;
}

.page-header {
  display: flex;
  align-items: center;
  gap: 1rem;
  margin-bottom: 2rem;
}

.page-header h1 {
  font-size: 1.4rem;
  font-weight: 600;
  margin: 0;
  color: #111;
}

.sub {
  font-size: 0.85rem;
  color: #888;
  margin: 0;
}

.back-btn {
  padding: 6px 14px;
  border: 1px solid #ddd;
  border-radius: 8px;
  background: none;
  cursor: pointer;
  font-size: 0.85rem;
}

.back-btn:hover {
  background: #f5f5f5;
}

.metrics {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 12px;
  margin-bottom: 2rem;
}

.metric {
  background: #f9f9f9;
  border-radius: 10px;
  padding: 1rem;
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.metric-label {
  font-size: 0.75rem;
  color: #888;
}

.metric-val {
  font-size: 1.4rem;
  font-weight: 600;
  color: #0F6E56;
}

.metric-val.ok {
  color: #0F6E56;
}

.metric-val.warn {
  color: #BA7517;
}

.card {
  border: 1px solid #eee;
  border-radius: 12px;
  overflow: hidden;
}

.card-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 1rem 1.25rem;
  border-bottom: 1px solid #eee;
}

.card-title {
  font-weight: 600;
  font-size: 0.95rem;
  color: #111;
}

.filters {
  display: flex;
  gap: 6px;
}

.filter-pill {
  padding: 4px 12px;
  border-radius: 20px;
  border: 1px solid #ddd;
  background: none;
  cursor: pointer;
  font-size: 0.8rem;
  color: #666;
}

.filter-pill.active {
  background: #f0f0f0;
  color: #111;
  border-color: #bbb;
  font-weight: 500;
}

.state-msg {
  padding: 2rem;
  text-align: center;
  color: #888;
  font-size: 0.9rem;
}

.state-msg.error {
  color: #c0392b;
}

.log-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 0.875rem;
}

.log-table th {
  text-align: left;
  padding: 10px 1.25rem;
  font-size: 0.75rem;
  color: #888;
  border-bottom: 1px solid #eee;
  background: #fafafa;
}

.log-table td {
  padding: 12px 1.25rem;
  border-bottom: 1px solid #f0f0f0;
}

.log-table tr:last-child td {
  border-bottom: none;
}

.log-table tr:hover td {
  background: #fafafa;
}

.dot {
  display: inline-block;
  width: 8px;
  height: 8px;
  border-radius: 50%;
  margin-right: 8px;
}

.dot-success {
  background: #1D9E75;
}

.dot-danger {
  background: #E24B4A;
}

.dot-info {
  background: #378ADD;
}

.dot-text {
  color: #222222;
}

.muted {
  color: #888;
}

.mono {
  font-family: monospace;
  font-size: 0.8rem;
  color: #888;
}

</style>
