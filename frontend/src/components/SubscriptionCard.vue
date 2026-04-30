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
  background: white;
  padding: 20px;
  border-radius: 12px;
  width: 280px;
  box-shadow: 0 8px 20px rgba(0,0,0,0.1);
  text-align: left;
}

.price {
  font-size: 22px;
  margin: 10px 0;
}

.buy-button {
  background: #635bff;
  color: white;
  padding: 10px;
  border: none;
  width: 100%;
  border-radius: 6px;
  cursor: pointer;
}
</style>