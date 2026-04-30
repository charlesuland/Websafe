<script setup>
import { ref, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useCartStore } from '@/stores/cartStore'

const route = useRoute()
const router = useRouter()
const cart = useCartStore()

// ── form fields ──────────────────────────────────────────────
const firstName  = ref('')
const lastName   = ref('')
const email      = ref('')
const phone      = ref('')
const address    = ref('')
const city       = ref('')
const state      = ref('')
const zip        = ref('')

// ── ui state ─────────────────────────────────────────────────
const submitting = ref(false)
const error      = ref(null)
const success    = ref(false)
const orderId    = ref(null)

const projectId = computed(() => route.params.projectId)

const fmt = cents => `$${(cents / 100).toFixed(2)}`

// ── submit ────────────────────────────────────────────────────
async function placeOrder() {
  error.value = null

  // basic client-side guard
  if (!firstName.value || !lastName.value || !email.value || !address.value || !city.value || !state.value || !zip.value) {
    error.value = 'Please fill in all required fields.'
    return
  }

  submitting.value = true

  // Build the payload for POST /api/checkout/create
  // The shippingAddress fields are stored in `meta` via the backend;
  // when Charlie wires Stripe the payment_method field will be replaced
  // with a real Stripe PaymentMethod ID.
  const payload = {
    //project_id: parseInt(projectId.value),
    items: cart.items.map(i => ({
      product_id: i.productId,
      quantity: i.quantity,
    })),
    customer: {
      first_name: firstName.value.trim(),
      last_name: lastName.value.trim(),
      email: email.value.trim(),
      phone: phone.value.trim(),

      house_number: address.value.trim().split(' ')[0], 
      street_name: address.value.trim().split(' ').slice(1).join(' '),
      city: city.value.trim(),
      state: state.value.trim(),
      postal_code: zip.value.trim(),
    },


  }

  try {
    console.log("Checkout Payload:", payload)
    const res = await fetch('/api/stripe/create-cart-checkout', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    })

    if (!res.ok) {
      const data = await res.json().catch(() => ({}))
      throw new Error(data.detail || `Error ${res.status}`)
    }

    const data = await res.json()
    console.log("Checkout Response:", data)
    if (data.url) {
      window.location.href = data.url
    } else {
      throw new Error('No checkout URL received')
    }

    cart.clearCart()
  } catch (e) {
    error.value = e.message
  } finally {
    submitting.value = false
  }
}

function continueShopping() {
  router.push(`/site/${projectId.value}/Shop`)
}
</script>

<template>
  <div class="checkout-page">

    <!-- ── top bar ──────────────────────────────────────── -->
    <header class="topbar">
      <button class="back-link" @click="router.back()">← Back to Shop</button>
      <span class="topbar-title">Checkout</span>
      <span class="secure-badge"> Secure</span>
    </header>

    <!-- ── SUCCESS STATE ───────────────────────────────── -->
    <div v-if="success" class="success-screen">
      <div class="success-card">
        <div class="success-icon">✓</div>
        <h2>Order Placed!</h2>
        <p>Thank you for your order. Your order ID is <strong>#{{ orderId }}</strong>.</p>
        <p class="sub-note">You'll receive a confirmation email at <strong>{{ email }}</strong> once your order is processed.</p>
        <button class="btn-primary" @click="continueShopping">Continue Shopping</button>
      </div>
    </div>

    <!-- ── EMPTY CART STATE ────────────────────────────── -->
    <div v-else-if="cart.items.length === 0" class="empty-screen">
      <div class="empty-card">
        <div class="empty-icon">🛒</div>
        <h2>Your cart is empty</h2>
        <p>Add some products before checking out.</p>
        <button class="btn-primary" @click="router.back()">Browse Products</button>
      </div>
    </div>

    <!-- ── MAIN CHECKOUT ───────────────────────────────── -->
    <div v-else class="checkout-layout">

      <!-- LEFT — form ──────────────────────────────────── -->
      <section class="form-section">

        <!-- Contact -->
        <div class="form-block">
          <h3 class="block-title">Contact Information</h3>
          <div class="row-2">
            <div class="field">
              <label>First Name <span class="req">*</span></label>
              <input v-model="firstName" type="text" placeholder="Jane" autocomplete="given-name" />
            </div>
            <div class="field">
              <label>Last Name <span class="req">*</span></label>
              <input v-model="lastName" type="text" placeholder="Smith" autocomplete="family-name" />
            </div>
          </div>
          <div class="field">
            <label>Email <span class="req">*</span></label>
            <input v-model="email" type="email" placeholder="jane@example.com" autocomplete="email" />
          </div>
          <div class="field">
            <label>Phone <span class="optional">(optional)</span></label>
            <input v-model="phone" type="tel" placeholder="+1 (555) 000-0000" autocomplete="tel" />
          </div>
        </div>

        <!-- Shipping -->
        <div class="form-block">
          <h3 class="block-title">Shipping Address</h3>
          <div class="field">
            <label>Street Address <span class="req">*</span></label>
            <input v-model="address" type="text" placeholder="123 Main St" autocomplete="street-address" />
          </div>
          <div class="row-3">
            <div class="field city-field">
              <label>City <span class="req">*</span></label>
              <input v-model="city" type="text" placeholder="Springfield" autocomplete="address-level2" />
            </div>
            <div class="field state-field">
              <label>State <span class="req">*</span></label>
              <input v-model="state" type="text" placeholder="KY" maxlength="2" autocomplete="address-level1" />
            </div>
            <div class="field zip-field">
              <label>ZIP <span class="req">*</span></label>
              <input v-model="zip" type="text" placeholder="42101" maxlength="10" autocomplete="postal-code" />
            </div>
          </div>
        </div>


        <!-- Error -->
        <div v-if="error" class="error-banner" role="alert">{{ error }}</div>

        <button class="btn-place-order" :disabled="submitting" @click="placeOrder">
          <span v-if="submitting">Placing Order…</span>
          <span v-else>Place Order · {{ fmt(cart.totalCents) }}</span>
        </button>

        <p class="legal-note">
          By placing your order you agree to our Terms of Service and Privacy Policy.
          Your payment information is encrypted and secure.
        </p>

      </section>

      <!-- RIGHT — order summary ───────────────────────── -->
      <aside class="summary-section">
        <div class="summary-card">
          <h3 class="summary-title">Order Summary</h3>

          <ul class="item-list">
            <li v-for="item in cart.items" :key="item.productId" class="item-row">
              <div class="item-img-wrap">
                <img v-if="item.imageUrl" :src="item.imageUrl" :alt="item.altText" class="item-thumb" />
                <div v-else class="item-thumb-placeholder">—</div>
                <span class="item-qty-badge">{{ item.quantity }}</span>
              </div>
              <div class="item-details">
                <p class="item-name">{{ item.name }}</p>
                <p class="item-unit">{{ fmt(item.price) }} each</p>
              </div>
              <p class="item-total">{{ fmt(item.price * item.quantity) }}</p>
            </li>
          </ul>

          <div class="divider"></div>

          <div class="totals">
            <div class="total-row">
              <span>Subtotal</span>
              <span>{{ fmt(cart.subtotalCents) }}</span>
            </div>
            <div class="total-row">
              <span>Shipping</span>
              <span>{{ cart.shippingCents > 0 ? fmt(cart.shippingCents) : 'Free' }}</span>
            </div>
            <div class="divider"></div>
            <div class="total-row grand">
              <span>Total</span>
              <span>{{ fmt(cart.totalCents) }}</span>
            </div>
          </div>

          <!-- quantity controls -->
          <div class="qty-section">
            <p class="qty-label">Adjust quantities</p>
            <div v-for="item in cart.items" :key="'qty-' + item.productId" class="qty-row">
              <span class="qty-name">{{ item.name }}</span>
              <div class="qty-controls">
                <button class="qty-btn" @click="cart.updateQuantity(item.productId, item.quantity - 1)">−</button>
                <span class="qty-val">{{ item.quantity }}</span>
                <button class="qty-btn" @click="cart.updateQuantity(item.productId, item.quantity + 1)">+</button>
                <button class="qty-remove" @click="cart.removeItem(item.productId)">✕</button>
              </div>
            </div>
          </div>

        </div>
      </aside>

    </div>
  </div>
</template>

<style scoped>
/* ── page shell ───────────────────────────────────── */
.checkout-page {
  min-height: 100vh;
  background: #f8fafc;
  font-family: 'Segoe UI', system-ui, sans-serif;
}

/* ── top bar ──────────────────────────────────────── */
.topbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 24px;
  height: 56px;
  background: #fff;
  border-bottom: 1px solid #e5e7eb;
  position: sticky;
  top: 0;
  z-index: 10;
}

.back-link {
  background: none;
  border: none;
  color: #2563eb;
  font-size: 0.87rem;
  font-weight: 500;
  cursor: pointer;
  padding: 0;
}

.back-link:hover { text-decoration: underline; }

.topbar-title {
  font-size: 1rem;
  font-weight: 600;
  color: #0f172a;
}

.secure-badge {
  font-size: 0.78rem;
  color: #64748b;
}

/* ── layout ───────────────────────────────────────── */
.checkout-layout {
  display: grid;
  grid-template-columns: 1fr 380px;
  gap: 32px;
  max-width: 1100px;
  margin: 0 auto;
  padding: 40px 24px;
  align-items: start;
}

/* ── form section ─────────────────────────────────── */
.form-section {
  display: flex;
  flex-direction: column;
  gap: 28px;
}

.form-block {
  background: #fff;
  border: 1px solid #e5e7eb;
  border-radius: 14px;
  padding: 24px;
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.block-title {
  font-size: 0.95rem;
  font-weight: 700;
  color: #0f172a;
  margin: 0 0 4px;
}

.row-2 {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 14px;
}

.row-3 {
  display: grid;
  grid-template-columns: 1fr 80px 100px;
  gap: 14px;
}

.field {
  display: flex;
  flex-direction: column;
  gap: 5px;
}

.field label {
  font-size: 0.8rem;
  font-weight: 600;
  color: #374151;
}

.req { color: #ef4444; }
.optional { font-weight: 400; color: #9ca3af; }

.field input {
  padding: 10px 12px;
  border: 1px solid #d1d5db;
  border-radius: 8px;
  font-size: 0.9rem;
  color: #0f172a;
  transition: border-color 0.15s, box-shadow 0.15s;
  outline: none;
  background: #fff;
}

.field input:focus {
  border-color: #2563eb;
  box-shadow: 0 0 0 3px rgba(37,99,235,0.12);
}



/* ── error ────────────────────────────────────────── */
.error-banner {
  background: #fef2f2;
  border: 1px solid #fecaca;
  border-radius: 8px;
  padding: 12px 16px;
  color: #b91c1c;
  font-size: 0.875rem;
}

/* ── submit button ────────────────────────────────── */
.btn-place-order {
  width: 100%;
  padding: 15px;
  background: #1d4ed8;
  color: #fff;
  border: none;
  border-radius: 10px;
  font-size: 1rem;
  font-weight: 700;
  cursor: pointer;
  transition: background 0.15s, transform 0.1s;
}

.btn-place-order:hover:not(:disabled) { background: #1e40af; }
.btn-place-order:active:not(:disabled) { transform: scale(0.99); }
.btn-place-order:disabled { background: #93c5fd; cursor: not-allowed; }

.legal-note {
  font-size: 0.72rem;
  color: #9ca3af;
  text-align: center;
  line-height: 1.5;
  margin: 0;
}

/* ── summary card ─────────────────────────────────── */
.summary-section { position: sticky; top: 72px; }

.summary-card {
  background: #fff;
  border: 1px solid #e5e7eb;
  border-radius: 16px;
  padding: 24px;
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.summary-title {
  font-size: 0.95rem;
  font-weight: 700;
  color: #0f172a;
  margin: 0;
}

/* item list */
.item-list { list-style: none; margin: 0; padding: 0; display: flex; flex-direction: column; gap: 14px; }

.item-row {
  display: flex;
  align-items: center;
  gap: 12px;
}

.item-img-wrap { position: relative; flex-shrink: 0; }

.item-thumb {
  width: 52px;
  height: 52px;
  border-radius: 8px;
  object-fit: cover;
  border: 1px solid #e5e7eb;
}

.item-thumb-placeholder {
  width: 52px; height: 52px;
  background: #f1f5f9;
  border-radius: 8px;
  display: flex; align-items: center; justify-content: center;
  color: #94a3b8; font-size: 1.2rem;
  border: 1px solid #e5e7eb;
}

.item-qty-badge {
  position: absolute;
  top: -6px;
  right: -6px;
  background: #1d4ed8;
  color: #fff;
  font-size: 0.65rem;
  font-weight: 700;
  width: 18px;
  height: 18px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
}

.item-details { flex: 1; min-width: 0; }
.item-name { font-size: 0.85rem; font-weight: 600; color: #111827; margin: 0; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.item-unit { font-size: 0.75rem; color: #6b7280; margin: 2px 0 0; }
.item-total { font-size: 0.88rem; font-weight: 600; color: #111827; white-space: nowrap; }

/* totals */
.divider { height: 1px; background: #f1f5f9; }

.totals { display: flex; flex-direction: column; gap: 8px; }
.total-row { display: flex; justify-content: space-between; font-size: 0.875rem; color: #374151; }
.total-row.grand { font-size: 1rem; font-weight: 700; color: #0f172a; }

/* qty controls */
.qty-section { display: flex; flex-direction: column; gap: 10px; }
.qty-label { font-size: 0.75rem; font-weight: 600; color: #6b7280; text-transform: uppercase; letter-spacing: 0.05em; margin: 0; }

.qty-row { display: flex; align-items: center; justify-content: space-between; gap: 8px; }
.qty-name { font-size: 0.8rem; color: #374151; flex: 1; min-width: 0; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }

.qty-controls { display: flex; align-items: center; gap: 4px; flex-shrink: 0; }

.qty-btn {
  width: 26px; height: 26px;
  border: 1px solid #d1d5db;
  border-radius: 6px;
  background: #f9fafb;
  color: #374151;
  font-size: 1rem;
  cursor: pointer;
  display: flex; align-items: center; justify-content: center;
  transition: background 0.1s;
}
.qty-btn:hover { background: #e5e7eb; }

.qty-val { font-size: 0.85rem; font-weight: 600; color: #0f172a; width: 22px; text-align: center; }

.qty-remove {
  width: 26px; height: 26px;
  border: none; border-radius: 6px;
  background: none; color: #ef4444;
  font-size: 0.75rem; cursor: pointer;
  display: flex; align-items: center; justify-content: center;
  transition: background 0.1s;
}
.qty-remove:hover { background: #fef2f2; }

/* ── success / empty screens ──────────────────────── */
.success-screen, .empty-screen {
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: calc(100vh - 56px);
  padding: 40px 24px;
}

.success-card, .empty-card {
  background: #fff;
  border: 1px solid #e5e7eb;
  border-radius: 20px;
  padding: 52px 48px;
  text-align: center;
  max-width: 480px;
  width: 100%;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 14px;
}

.success-icon {
  width: 64px; height: 64px;
  background: #dcfce7;
  border-radius: 50%;
  display: flex; align-items: center; justify-content: center;
  font-size: 1.8rem;
  color: #16a34a;
}

.empty-icon { font-size: 3rem; }

.success-card h2, .empty-card h2 { font-size: 1.5rem; font-weight: 700; color: #0f172a; margin: 0; }
.success-card p, .empty-card p { font-size: 0.9rem; color: #6b7280; margin: 0; line-height: 1.6; }
.sub-note { font-size: 0.82rem !important; }

.btn-primary {
  margin-top: 8px;
  padding: 12px 28px;
  background: #1d4ed8;
  color: #fff;
  border: none;
  border-radius: 10px;
  font-size: 0.9rem;
  font-weight: 600;
  cursor: pointer;
  transition: background 0.15s;
}
.btn-primary:hover { background: #1e40af; }

/* ── responsive ───────────────────────────────────── */
@media (max-width: 768px) {
  .checkout-layout {
    grid-template-columns: 1fr;
    padding: 20px 16px;
  }

  .summary-section { position: static; }

  .row-3 { grid-template-columns: 1fr 1fr; }
  .city-field { grid-column: 1 / -1; }
}
</style>