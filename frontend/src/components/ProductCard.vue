<script setup>
const props = defineProps({
  product: {
    type: Object,
    required: true
  },
  imageUrl: {
    type: String,
    default: null
  },
  project: {
    type: Object,
    required: true
  }
})

const emit = defineEmits(['edit', 'delete', 'toggle-active'])

function onEdit() {
  emit('edit', props.product, props.project)
}

function onDelete() {
  emit('delete', props.product.id, props.project)
}

function onToggleActive() {
  emit('toggle-active', props.product, props.project)
}
</script>

<template>
  <div class="card">
    <div v-if="imageUrl" class="product-image-container">
      <img :src="imageUrl" :alt="product.name" class="product-image" />
    </div>
    <div v-else class="product-image-placeholder">No Image</div>

    <h3>{{ product.name }}</h3>
    <p>{{ product.description }}</p>
    <strong>${{ (product.sale_price / 100).toFixed(2) }}</strong>

    <div class="actions">
      <button @click="onEdit">Edit</button>
      <button @click="onDelete">Delete</button>
      <button @click="onToggleActive">
        {{ product.is_active ? 'Deactivate' : 'Activate' }}
      </button>
    </div>
  </div>
</template>

<style scoped>
.card {
  background: #ffffff;
  border-radius: 16px;
  display: flex;
  flex-direction: column;
  border: 1px solid rgba(226, 232, 240, 0.9);
  transition: transform 0.24s ease, box-shadow 0.24s ease;
  overflow: hidden;
  min-height: 380px;
  max-height: 380px;
  height: 380px;
  width: 300px;
  box-sizing: border-box;
  justify-content: flex-start;
}

.card:hover {
  transform: translateY(-4px);
  box-shadow: 0 16px 40px rgba(15, 23, 42, 0.08);
}

.card h3 {
  font-size: 1.1rem;
  color: #111827;
  padding: 16px 16px 4px;
  margin: 0;
}

.card p {
  font-size: 0.95rem;
  color: #4b5563;
  padding: 0 16px;
  margin: 0;
  min-height: 44px;
}

.card strong {
  font-size: 1.1rem;
  color: #2563eb;
  padding: 12px 16px 0 16px;
  display: block;
}

.product-image-container {
  width: 100%;
  aspect-ratio: 4 / 3;
  height: 180px;
  background-color: #f8f9fb;
  border-radius: 12px 12px 0 0;
  overflow: hidden;
  display: flex;
  align-items: center;
  justify-content: center;
}

.product-image {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.product-image-placeholder {
  width: 100%;
  aspect-ratio: 4 / 3;
  height: 180px;
  background-color: #eaeef2;
  border-radius: 12px 12px 0 0;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #7d8a99;
  font-size: 0.95rem;
}

.actions {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  padding: 16px;
  margin-top: auto;
  background: #f8f9fb;
  border-top: 1px solid #e5e7eb;
  position: relative;
  bottom: 0;
  left: 0;
  width: 100%;
  z-index: 2;
}

.actions button {
  flex: 1 1 120px;
  min-width: 100px;
  padding: 10px 12px;
  border-radius: 10px;
  font-size: 0.9rem;
  border: none;
  cursor: pointer;
}

.actions button:hover {
  opacity: 0.95;
}

.actions button:nth-child(1) {
  background: #6b7280;
  color: #fff;
}

.actions button:nth-child(2) {
  background: #ef4444;
  color: #fff;
}

.actions button:nth-child(3) {
  background: #2563eb;
  color: #fff;
}
</style>
