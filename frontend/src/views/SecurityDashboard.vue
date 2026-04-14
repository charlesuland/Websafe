<template>
  <div class="security-dashboard">
    <h1>Security Dashboard</h1>
    <section>
      <h2>User Logs</h2>
      <table v-if="logs.length">
        <thead>
          <tr>
            <th>Date</th>
            <th>User ID</th>
            <th>Action</th>
            <th>Details</th>
            <th>IP Address</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="log in logs" :key="log.id">
            <td>{{ log.created_at }}</td>
            <td>{{ log.user_id }}</td>
            <td>{{ log.action }}</td>
            <td>{{ log.details }}</td>
            <td>{{ log.ip_address }}</td>
          </tr>
        </tbody>
      </table>
      <div v-else>No logs found.</div>
    </section>
    <section>
      <h2>Security Reports</h2>
      <table v-if="reports.length">
        <thead>
          <tr>
            <th>Report ID</th>
            <th>Date</th>
            <th>Status</th>
            <th>XSS</th>
            <th>SQLi</th>
            <th>CSRF</th>
            <th>Urgent</th>
            <th>Notes</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="report in reports" :key="report.id">
            <td>{{ report.report_id }}</td>
            <td>{{ report.generated_at }}</td>
            <td>{{ report.status }}</td>
            <td>{{ report.xss_test_passed ? '✔️' : '❌' }}</td>
            <td>{{ report.sqli_test_passed ? '✔️' : '❌' }}</td>
            <td>{{ report.csrf_test_passed ? '✔️' : '❌' }}</td>
            <td>{{ report.urgent ? 'Yes' : 'No' }}</td>
            <td>{{ report.notes }}</td>
          </tr>
        </tbody>
      </table>
      <div v-else>No reports found.</div>
    </section>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'

const logs = ref([])
const reports = ref([])

async function fetchLogs() {
  const res = await fetch('/api/security/logs')
  logs.value = await res.json()
}

async function fetchReports() {
  const res = await fetch('/api/security/reports')
  reports.value = await res.json()
}

onMounted(() => {
  fetchLogs()
  fetchReports()
})
</script>

<style scoped>
.security-dashboard {
  padding: 2rem;
}
table {
  width: 100%;
  border-collapse: collapse;
  margin-bottom: 2rem;
}
th, td {
  border: 1px solid #ccc;
  padding: 0.5rem;
  text-align: left;
}
</style>
