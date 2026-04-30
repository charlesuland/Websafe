<template>
  <div class="card">
    <h2>{{ name }}</h2>
    <p class="description">{{ description }}</p>

    <h3 class="price">{{ price }}</h3>

    <ul>
      <li v-for="(feature, i) in features" :key="i">
        {{ feature }}
      </li>
    </ul>

    <button
      :disabled="isLoading"
      @click="handleCheckout"
      class="buy-button"
    >
      <span v-if="isLoading">Processing...</span>
      <span v-else>Buy Now</span>
    </button>

    <p v-if="errorMessage" class="error">{{ errorMessage }}</p>
  </div>
</template>

<script setup>
import { apiFetch } from '@/auth'
import { ref } from 'vue'

const props = defineProps({
  planId: { type: String, required: true },
  name: String,
  description: String,
  price: String,
  successUrl: {
    type: String,
    default: () => window.location.origin + '/dashboard'
  },
  cancelUrl: {
    type: String,
    default: () => window.location.origin + '/dashboard'
  }
})

const isLoading = ref(false)
const errorMessage = ref('')

const handleCheckout = async () => {
  isLoading.value = true
  errorMessage.value = ''

  try {
    const response = await apiFetch('/api/stripe/create-checkout-session', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        plan_id: props.planId,
        success_url: props.successUrl,
        cancel_url: props.cancelUrl
      })
    })

    if (!response.ok) throw new Error(await response.text())

    const { url } = await response.json()

    window.location.href = url
  } catch (err) {
    errorMessage.value = 'Checkout failed. Try again.'
    console.error(err)
  } finally {
    isLoading.value = false
  }
}
</script>

<style scoped>
.card {
  background: linear-gradient(180deg, #132031 0%, #0f1825 100%);
  border: 1px solid #2a3d58;
  border-radius: 16px;
  padding: 1.5rem;
  width: 100%;
  max-width: 320px;
  box-shadow: 0 18px 36px rgba(0, 0, 0, 0.25);
  text-align: left;
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
  transition: transform 0.15s ease, box-shadow 0.15s ease;
}

.card:hover {
  transform: translateY(-4px);
  box-shadow: 0 24px 48px rgba(0, 0, 0, 0.35);
}

.card h2 {
  margin: 0;
  font-size: 1.2rem;
  font-weight: 700;
  color: #f8fbff;
}

.description {
  margin: 0;
  font-size: 0.9rem;
  color: #b8cade;
}

.price {
  font-size: 1.5rem;
  font-weight: 700;
  margin: 0.5rem 0;
  color: #74a0ff;
}

ul {
  padding-left: 18px;
  margin: 0.5rem 0 1rem;
  color: #d8e4f2;
  font-size: 0.9rem;
}

li {
  margin-bottom: 4px;
}

.buy-button {
  margin-top: auto;
  background: #1964d5;
  border: 1px solid #4283d8;
  color: #ffffff;
  padding: 0.75rem;
  border-radius: 10px;
  font-weight: 700;
  cursor: pointer;
  transition: background 0.15s ease, opacity 0.15s ease;
}

.buy-button:hover:not(:disabled) {
  background: #2464d9;
}

.buy-button:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.error {
  margin-top: 8px;
  font-size: 0.8rem;
  color: #f87171;
}
</style>