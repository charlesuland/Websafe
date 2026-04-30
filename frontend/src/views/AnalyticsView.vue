<template>
  <div class="dashboard-container">
    <header class="db-header">
      <h1>Store Analytics</h1>
      <button @click="fetchData" class="refresh-btn">Refresh Data</button>
    </header>

    <div class="metrics-grid">
      <div class="metric-card">
        <label>Total Revenue</label>
        <div class="value">${{ (stats.totalRevenue / 100).toFixed(2) }}</div>
      </div>
      <div class="metric-card">
        <label>Total Orders</label>
        <div class="value">{{ orders.length }}</div>
      </div>
      <div class="metric-card">
        <label>Avg. Order Value</label>
        <div class="value">${{ (stats.aov / 100).toFixed(2) }}</div>
      </div>
      <div class="metric-card">
        <label>Items Sold</label>
        <div class="value">{{ stats.totalItems }}</div>
      </div>
    </div>

    <div class="charts-grid">
      <div class="chart-container">
        <h3>Product Sales Volume</h3>
        <canvas ref="productChartCanvas"></canvas>
      </div>
      <div class="chart-container">
        <h3>Shipping Status Distribution</h3>
        <canvas ref="statusChartCanvas"></canvas>
      </div>
      <div class="chart-container">
        <h3>Daily Revenue</h3>
        <canvas ref="revenueChartCanvas"></canvas>
      </div>

    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue';
import Chart from 'chart.js/auto';
import { apiFetch } from '../auth.js';


const orders = ref([]);
const productChartCanvas = ref(null);
const statusChartCanvas = ref(null);
const revenueChartCanvas = ref(null);
let revenueChart = null;
let productChart = null;
let statusChart = null;

// 1. Fetch Data
const fetchData = async () => {
  try {

    const response = await apiFetch('/api/orders/');
    if (!response.ok) throw new Error('Failed to fetch orders');
    const data = await response.json();
    orders.value = data.orders;

    renderCharts();
  } catch (e) {
    console.error("Dashboard fetch failed", e);
  }
};

// 2. Compute Statistics (The "Analysis")
const stats = computed(() => {
  let totalRev = 0;
  let totalItems = 0;
  
  orders.value.forEach(o => {
    totalRev += o.amount_total;
    o.items.forEach(i => totalItems += i.quantity);
  });

  return {
    totalRevenue: totalRev,
    totalItems: totalItems,
    aov: orders.value.length ? totalRev / orders.value.length : 0
  };
});

// 3. Prepare Chart Data
const renderCharts = () => {
  // Destroy old instances if they exist (prevents flickering)
  if (productChart) productChart.destroy();
  if (statusChart) statusChart.destroy();

  // Process Product Data: { 'Item Name': TotalQuantity }
  const productMap = {};
  const statusMap = {};

  orders.value.forEach(order => {
    order.items.forEach(item => {
      productMap[item.name] = (productMap[item.name] || 0) + item.quantity;
      statusMap[item.shipping_status] = (statusMap[item.shipping_status] || 0) + 1;
    });
  });

  // Render Bar Chart
  productChart = new Chart(productChartCanvas.value, {
    type: 'bar',
    data: {
      labels: Object.keys(productMap),
      datasets: [{
        label: 'Units Sold',
        data: Object.values(productMap),
        backgroundColor: '#4f46e5'
      }]
    },
    options: { responsive: true, maintainAspectRatio: false }
  });

  // Render Doughnut Chart
  statusChart = new Chart(statusChartCanvas.value, {
    type: 'doughnut',
    data: {
      labels: Object.keys(statusMap),
      datasets: [{
        data: Object.values(statusMap),
        backgroundColor: ['#f59e0b', '#10b981', '#3b82f6', '#ef4444']
      }]
    },
    options: { responsive: true, maintainAspectRatio: false }
  });


  if (revenueChart) revenueChart.destroy();

  // 1. Group revenue by date
  const revenueByDate = {};
  
  orders.value.forEach(order => {
    // Format date to YYYY-MM-DD
    const date = new Date(order.created_at).toISOString().split('T')[0];
    const amount = order.amount_total / 100; // Convert cents to dollars
    
    revenueByDate[date] = (revenueByDate[date] || 0) + amount;
  });

  // 2. Sort dates chronologically
  const sortedDates = Object.keys(revenueByDate).sort();
  const revenueData = sortedDates.map(date => revenueByDate[date]);

  // 3. Create the Line Chart
  revenueChart = new Chart(revenueChartCanvas.value, {
    type: 'line',
    data: {
      labels: sortedDates,
      datasets: [{
        label: 'Revenue ($)',
        data: revenueData,
        borderColor: '#4f46e5',
        backgroundColor: 'rgba(79, 70, 229, 0.1)',
        fill: true,
        tension: 0.4, // Makes the line curvy
        pointRadius: 4
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: { display: false }
      },
      scales: {
        y: {
          beginAtZero: true,
          ticks: { callback: (value) => '$' + value }
        }
      }
    }
  });

};

onMounted(fetchData);
</script>

<style scoped>
.dashboard-container {
  padding: 2rem 2.5rem 3rem;
  min-height: 100vh;
  color: #d8e4f2;
}

.db-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 2rem;
}

.db-header h1 {
  margin: 0;
  font-size: 1.75rem;
  font-weight: 700;
  color: #f8fbff;
}

.refresh-btn {
  padding: 0.7rem 1rem;
  border-radius: 10px;
  border: 1px solid #4283d8;
  background: #1964d5;
  color: white;
  font-weight: 700;
  cursor: pointer;
}

.refresh-btn:hover {
  background: #2464d9;
}

.metrics-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 20px;
  margin-bottom: 2rem;
}

.metric-card {
  background: linear-gradient(180deg, #132031 0%, #0f1825 100%);
  border: 1px solid #2a3d58;
  border-radius: 16px;
  padding: 1.25rem;
  box-shadow: 0 18px 36px rgba(0, 0, 0, 0.22);
}

.metric-card label {
  font-size: 0.8rem;
  font-weight: 700;
  color: #b9cadd;
  text-transform: uppercase;
}

.metric-card .value {
  font-size: 1.6rem;
  font-weight: 700;
  margin-top: 6px;
  color: #f8fbff;
}


.charts-grid {
  display: grid;
  grid-template-columns: 2fr 1fr;
  gap: 20px;
}

.chart-container {
  background: linear-gradient(180deg, #132031 0%, #0f1825 100%);
  border: 1px solid #2a3d58;
  border-radius: 16px;
  padding: 1.25rem;
  padding-bottom: 3rem;
  height: 380px;
  box-shadow: 0 18px 36px rgba(0, 0, 0, 0.22);
}

.chart-container h3 {
  margin: 0 0 10px;
  font-size: 0.95rem;
  font-weight: 700;
  color: #b9cadd;
}

.loading-state,
.empty-state {
  text-align: center;
  padding: 40px;
  color: #c6d4e5;
}
</style>