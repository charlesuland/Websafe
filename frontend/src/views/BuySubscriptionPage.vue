<template>
  <main class="subscription-page">
    <header class="subscription-header">
      <h1>Choose Your Subscription</h1>
      <p class="subtitle">
        Unlock features and scale your store with the right plan.
      </p>
    </header>

    <section class="subscription-grid">
      <SubscriptionCard
        v-for="option in subscriptionOptions"
        :key="option.id"
        :planId="option.id"
        :name="option.name"
        :description="option.description"
        :price="option.price"
      />
    </section>
  </main>
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
.subscription-page {
  padding: 2rem 2.5rem 3rem;
  color: #d8e4f2;
  min-height: 100vh;
}

.subscription-header {
  text-align: center;
  margin-bottom: 2.5rem;
}

.subscription-header h1 {
  margin: 0;
  font-size: 2rem;
  font-weight: 700;
  color: #f8fbff;
}

.subtitle {
  margin-top: 0.6rem;
  color: #b8cade;
  font-size: 1rem;
}

.subscription-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(260px, 320px));
  justify-content: center;
  gap: 24px;
}

.subscription-grid :deep(.subscription-card) {
  background: linear-gradient(180deg, #132031 0%, #0f1825 100%);
  border: 1px solid #2a3d58;
  border-radius: 16px;
  padding: 1.5rem;
  box-shadow: 0 18px 36px rgba(0, 0, 0, 0.25);
  transition: transform 0.15s ease, box-shadow 0.15s ease;
}

.subscription-grid :deep(.subscription-card:hover) {
  transform: translateY(-4px);
  box-shadow: 0 22px 45px rgba(0, 0, 0, 0.35);
}

@media (max-width: 720px) {
  .subscription-page {
    padding: 1.25rem 1rem 2rem;
  }

  .subscription-header h1 {
    font-size: 1.6rem;
  }
}
</style>