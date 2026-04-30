<template>
  <div class="buy-subscription-page">
    <h1>Choose Your Subscription</h1>

    <div class="subscription-options">
      <SubscriptionCard
        v-for="option in subscriptionOptions"
        :key="option.id"
        :planId="option.id"
        :name="option.name"
        :description="option.description"
        :price="option.price"
      />
    </div>
  </div>
</template>

<script setup>
import SubscriptionCard from '@/components/SubscriptionCard.vue'

const subscriptionOptions = [
  {
    id: 'price_1TNd3WEzUozMKyEeWNvGM1g1',
    name: 'Basic Plan',
    description: 'Good for starting your first project',
    price: '$20/month',
  },
  {
    id: 'price_1TNytoEzUozMKyEezpvWKOQl',
    name: 'Pro Plan',
    description: 'Best for serious creators',
    price: '$200/year (save 20%)',
  }
]
</script>

<style scoped>
.buy-subscription-page {
  padding: 40px;
  text-align: center;
}

.subscription-options {
  display: flex;
  gap: 20px;
  justify-content: center;
  margin-top: 30px;
}
</style>