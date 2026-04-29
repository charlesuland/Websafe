<template>
  <div class="checkout-container">
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
import { ref } from 'vue';

// Props allow you to reuse this button for different subscription tiers
const props = defineProps({
  planId: {
    type: String,
    required: true
  },
  successUrl: {
    type: String,
    default: () => window.location.origin + '/success'
  },
  cancelUrl: {
    type: String,
    default: () => window.location.origin + '/cancel'
  }
});

const isLoading = ref(false);
const errorMessage = ref('');

const handleCheckout = async () => {
  isLoading.value = true;
  errorMessage.value = '';
  const token = localStorage.getItem('token');
  
  try {
    const response = await fetch('/api/stripe/create-checkout-session', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`
      },
      body: JSON.stringify({
        plan_id: props.planId,
        success_url: props.successUrl,
        cancel_url: props.cancelUrl
      }),
    });
    console.log("Checkout Response:", response);
    if (!response.ok) throw new Error('Network response was not ok');

    const { url } = await response.json();

    // Redirect the user to Stripe's hosted page
    if (url) {
      window.location.href = url;
    } else {
      throw new Error('Failed to retrieve checkout URL');
    }

  } catch (error) {
    console.error("Checkout Error:", error);
    errorMessage.value = "Something went wrong. Please try again.";
  } finally {
    isLoading.value = false;
  }
};
</script>

<style scoped>
.buy-button {
  background-color: #635bff; /* Stripe Purple */
  color: white;
  padding: 12px 24px;
  border: none;
  border-radius: 4px;
  font-weight: 600;
  cursor: pointer;
  transition: opacity 0.2s;
}

.buy-button:disabled {
  opacity: 0.7;
  cursor: not-allowed;
}

.error {
  color: #df1b41;
  font-size: 0.9rem;
  margin-top: 8px;
}
</style>