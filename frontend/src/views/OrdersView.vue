<template>
  <main class="orders-container" aria-labelledby="orders-title">
    <h1 id="orders-title">Project Orders</h1>

    <div v-if="loading" role="status" aria-live="polite">
      Loading orders...
    </div>

    <section
      v-else
      aria-label="Order list"
    >
      <article
        v-for="order in orders"
        :key="order.id"
        class="order-card"
        :aria-labelledby="`order-${order.id}-title`"
      >
        <!-- Header -->
        <div class="order-header">
          <div>
            <h2 :id="`order-${order.id}-title`">
              Order #{{ order.id }}
            </h2>
            <p class="order-date">
              Placed
              <time :datetime="order.created_at">
                {{ formatDate(order.created_at) }}
              </time>
            </p>
          </div>

          <span
            class="total-badge"
            :aria-label="`Vendor payout ${(
              order.vendor_amount_cents / 100
            ).toFixed(2)} dollars`"
          >
            ${{ (order.vendor_amount_cents / 100).toFixed(2) }}
          </span>
        </div>

        <!-- Details -->
        <div class="details-grid">
          <section class="section" aria-labelledby="customer-details">
            <h3 id="customer-details">Customer Details</h3>
            <p>
              <strong>
                {{ order.customer.first_name }} {{ order.customer.last_name }}
              </strong>
            </p>
            <p>
              <a class="email" :href="`mailto:${order.customer.email}`">
                {{ order.customer.email }}
              </a>
              |
              <span>{{ order.customer.phone }}</span>
            </p>
            <p>{{ order.customer.line }}</p>
            <p>
              {{ order.customer.city }},
              {{ order.customer.state }}
              {{ order.customer.postal_code }}
            </p>
          </section>

          <section class="section" aria-labelledby="financial-details">
            <h3 id="financial-details">Financial Details</h3>
            <ul>
              <li>
                Total:
                <strong>${{ (order.amount_total / 100).toFixed(2) }}</strong>
              </li>
              <li>
                Vendor Amount:
                <strong>${{ (order.vendor_amount_cents / 100).toFixed(2) }}</strong>
              </li>
              <li>
                Shipping:
                <strong>${{ (order.shipping_price_cents / 100).toFixed(2) }}</strong>
              </li>
            </ul>
          </section>
        </div>

        <!-- Items Table -->
        <table
          class="items-table"
          :aria-labelledby="`order-${order.id}-title`"
        >
          <caption class="sr-only">
            Items in order {{ order.id }}
          </caption>

          <thead>
            <tr>
              <th scope="col">Item Name</th>
              <th scope="col">Quantity</th>
              <th scope="col">Price</th>
              <th scope="col">Shipping Status</th>
            </tr>
          </thead>

          <tbody>
            <tr
              v-for="(item, index) in order.items"
              :key="index"
            >
              <td>{{ item.name }}</td>
              <td>{{ item.quantity }}</td>
              <td>
                ${{ (item.price_at_purchase / 100).toFixed(2) }}
              </td>
              <td>
                <label
                  class="sr-only"
                  :for="`status-${item.id}`"
                >
                  Shipping status for {{ item.name }}
                </label>

                <select
                  :id="`status-${item.id}`"
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
      </article>
    </section>
  </main>
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
    const response = await apiFetch('/api/orders');
    if (!response.ok) throw new Error('Failed to fetch orders');
    const data = await response.json();
    orders.value = data.orders;
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
.orders-container {
  padding: 2rem 2.5rem 3rem;
  color: #d8e4f2;
}

.orders-container h1 {
  color: #f8fbff;
  font-size: 1.75rem;
  font-weight: 700;
  margin-bottom: 1.5rem;
}

.order-card {
  background: linear-gradient(180deg, #132031 0%, #0f1825 100%);
  border: 1px solid #2a3d58;
  border-radius: 16px;
  padding: 1.5rem;
  margin-bottom: 1.5rem;
  box-shadow: 0 18px 36px rgba(0, 0, 0, 0.22);
}

.order-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  border-bottom: 1px solid #2a3d58;
  padding-bottom: 0.75rem;
  margin-bottom: 1rem;
}

.order-header h3 {
  margin: 0;
  color: #f8fbff;
}

.order-date {
  color: #9fb3c8;
  font-size: 0.85rem;
  margin-top: 4px;
}

.total-badge {
  background: #1a7755;
  color: #ffffff;
  padding: 6px 14px;
  border-radius: 999px;
  font-weight: 700;
  font-size: 0.9rem;
}

.details-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 20px;
  margin-bottom: 1.2rem;
}

.section h4 {
  margin-bottom: 6px;
  color: #f8fbff;
}

.section p,
.section li {
  color: #b9cadd;
  font-size: 0.9rem;
}

.items-table {
  width: 100%;
  border-collapse: collapse;
  margin-top: 1rem;
}

.items-table th {
  text-align: left;
  padding: 10px;
  color: #9fb3c8;
  font-size: 0.85rem;
  border-bottom: 1px solid #2a3d58;
}

.items-table td {
  padding: 12px;
  border-bottom: 1px solid #1f2e44;
  color: #d8e4f2;
  font-size: 0.9rem;
}

select {
  padding: 6px 10px;
  border-radius: 8px;
  border: 1px solid #2a3d58;
  background: #0f1825;
  color: #f8fbff;
  cursor: pointer;
}

.pending {
  border-color: #f59e0b;
  color: #fbbf24;
}

.shipped {
  border-color: #3b82f6;
  color: #60a5fa;
}

.delivered {
  border-color: #10b981;
  color: #34d399;
}

.orders-container > div[v-if] {
  color: #b8cade;
}

.email {
  color: rgb(0, 221, 255);
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
</style>