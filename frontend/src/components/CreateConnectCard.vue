<template>
  <div class="checkout-container">
    <button 
      :disabled="isLoading" 
      @click="handleCheckout"
      class="buy-button"
    >
      <span v-if="isLoading">Processing...</span>
      <span v-else>Connect Account</span>
    </button>
    
    <p v-if="errorMessage" class="error">{{ errorMessage }}</p>
  </div>
</template>

<script setup>
import { ref } from 'vue';
import { apiFetch } from '../auth'
// Props for vendor onboarding
const props = defineProps({
  country: {
    type: String,
    default: 'US'
  }
});

const isLoading = ref(false);
const errorMessage = ref('');

const handleCheckout = async () => {
  isLoading.value = true;
  errorMessage.value = '';

  try {
    const response = await apiFetch('/api/stripe/create-connect-account', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    
  })


    if (!response.ok) throw new Error('Network response was not ok');

    const data = await response.json();
    // The backend returns { account_id, onboarding_url }
    if (data.onboarding_url) {
      window.location.href = data.onboarding_url;
    } else {
      throw new Error('Failed to retrieve onboarding URL');
    }
  } catch (error) {
    console.error("Connect Account Error:", error);
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

.checkout-container {
  margin-bottom: 24px;
}
</style>