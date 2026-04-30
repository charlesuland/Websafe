<template>
  <div class="orders-container">
    <h1>Project Orders</h1>

    <div v-if="loading">Loading orders...</div>

    <div v-else class="order-card" v-for="order in orders" :key="order.id">
      <div class="order-header">
        <div>
          <h3>Order #{{ order.id }}</h3>
          <p class="order-date">Placed {{ formatDate(order.created_at) }}</p>
        </div>
        <span class="total-badge">${{ (order.vendor_amount_cents / 100).toFixed(2) }}</span>
      </div>

      <div class="details-grid">
        <div class="section">
          <h4>Customer Details</h4>
          <p><strong>{{ order.customer.first_name }} {{ order.customer.last_name }}</strong></p>
          <p>{{ order.customer.email }} | {{ order.customer.phone }}</p>
          <p>{{ order.customer.line }}</p>
          <p>{{ order.customer.city }}, {{ order.customer.state }} {{ order.customer.postal_code }}</p>
        </div>

        <div class="section">
          <h4>Financials</h4>
          <ul>
            <li>Total: ${{ (order.amount_total / 100).toFixed(2) }}</li>
            <li>Vendor Amount: ${{ (order.vendor_amount_cents / 100).toFixed(2) }}</li>
            <li>Shipping: ${{ (order.shipping_price_cents / 100).toFixed(2) }}</li>
          </ul>
        </div>
      </div>

      <table class="items-table">
        <thead>
          <tr>
            <th>Item Name</th>
            <th>Quantity</th>
            <th>Price</th>
            <th>Shipping Status</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="(item, index) in order.items" :key="index">
            <td>{{ item.name }}</td>
            <td>{{ item.quantity }}</td>
            <td>${{ (item.price_at_purchase / 100).toFixed(2) }}</td>
            <td>
              <select 
                v-model="item.shipping_status" 
                @change="updateShippingStatus(item.id)"
                :class="item.shipping_status.toLowerCase()"
              >
                <option value="pending">Pending</option>
                <option value="shipped">Shipped</option>
                <option value="delivered">Delivered</option>
              </select>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import {apiFetch} from '../auth.js';


const orders = ref([]);
const loading = ref(true);

const formatDate = (value) => {
  if (!value) return ''
  const date = new Date(value)
  return date.toLocaleString(undefined, {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  })
}

// Fetch data from your FastAPI endpoint
const fetchOrders = async () => {
  try {
    // Note: You'll need to pass the project_id as required by your FastAPI route
    const response = await apiFetch('/api/orders/');
    if (!response.ok) throw new Error('Failed to fetch orders');
    const data = await response.json();
    orders.value = data.orders; // Assuming your API returns { orders: [...] }
  } catch (error) {
    console.error("Error fetching orders:", error);
  } finally {
    loading.value = false;
  }
};

// Handle editing the shipping status
const updateShippingStatus = async (itemId) => {
  // Find the item in the orders data
  let targetItem = null;
  for (const order of orders.value) {
    targetItem = order.items.find(item => item.id === itemId);
    if (targetItem) break;
  }
  if (!targetItem) {
    console.error("Item not found");
    return;
  }

  try {


    const response = await apiFetch(`/api/orders/update-shipping-status/${itemId}`, {
      method: 'PATCH',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ 
        status: targetItem.shipping_status.toUpperCase(),
      })
    });

    if (!response.ok) {
      throw new Error('Failed to update shipping status');
    }


  } catch (error) {
    console.error("Failed to update status:", error);
  }
};

onMounted(fetchOrders);
</script>

<style scoped>
.orders-container { padding: 20px; font-family: sans-serif; }
.order-card { 
  border: 1px solid #ddd; 
  border-radius: 8px; 
  margin-bottom: 2rem; 
  padding: 1.5rem;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}
.order-header { display: flex; justify-content: space-between; align-items: center; border-bottom: 2px solid #eee; margin-bottom: 1rem; }  .order-date { color: #6b7280; font-size: 0.9rem; margin: 6px 0 0; }.total-badge { background: #4caf50; color: white; padding: 4px 12px; border-radius: 20px; font-weight: bold; }
.details-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 20px; margin-bottom: 1rem; }
.items-table { width: 100%; border-collapse: collapse; margin-top: 1rem; }
.items-table th, .items-table td { text-align: left; padding: 12px; border-bottom: 1px solid #eee; }
select { padding: 6px; border-radius: 4px; border: 1px solid #ccc; cursor: pointer; }
.shipped { border-color: #2196f3; color: #2196f3; }
.delivered { border-color: #4caf50; color: #4caf50; }
</style>