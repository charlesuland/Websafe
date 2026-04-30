<script setup>
const props = defineProps({
  product: Object,
  project: Object
})

const emit = defineEmits(['edit', 'delete', 'toggle-published'])

function onEdit() {
  emit('edit', props.product, props.project)
}

function onDelete() {
  emit('delete', props.product, props.project)
}

function onTogglePublished() {
  emit('toggle-published', props.product, props.project)
}
</script>

<template>
  <article class="card" :aria-label="product?.name || 'Product card'">
    <div v-if="product?.image_url" class="product-image-container">
      <img
        :src="product.image_url"
        :alt="product.alt_text"
        class="product-image"
      />
    </div>

    <div v-else class="product-image-placeholder">
      No Image
    </div>

    <div class="card-body">
      <h3 class="title">{{ product?.name }}</h3>

      <p class="description">
        {{ product?.description }}
      </p>

      <strong class="price">
        ${{ (product?.sale_price / 100).toFixed(2) }}
      </strong>
    </div>

    <div class="actions">
      <button type="button" class="secondary" @click="onEdit">
        Edit
      </button>

      <button type="button" class="danger" @click="onDelete">
        Delete
      </button>

      <button
        type="button"
        :class="product?.is_published ? 'active-btn' : 'inactive-btn'"
        @click="onTogglePublished"
      >
        {{ product?.is_published ? 'Active' : 'Inactive' }}
      </button>
    </div>
  </article> 
</template>

<style scoped>
.active-btn {
  background: #0c6c2f;
  color: #ffffff;
}

.active-btn:hover {
  background: #084a20;
}

.inactive-btn {
  background: #475569;
  color: #ffffff;
}

.inactive-btn:hover {
  background: #334155;
}

.card {
  background: linear-gradient(180deg, #132031 0%, #0f1825 100%);
  border: 1px solid #2a3d58;
  border-radius: 16px;

  display: flex;
  flex-direction: column;

  overflow: hidden;

  width: 100%;
  max-width: 100%;
  min-height: 380px;
  max-height: 480px;

  box-shadow: 0 18px 36px rgba(0, 0, 0, 0.25);
  transition: transform 0.2s ease, box-shadow 0.2s ease;
}

.card:hover {
  transform: translateY(-4px);
  box-shadow: 0 24px 48px rgba(0, 0, 0, 0.35);
}

.product-image-container,
.product-image-placeholder {
  width: 100%;
  height: 180px;
  aspect-ratio: 4 / 3;

  display: flex;
  align-items: center;
  justify-content: center;

  background: #0b1220;
  border-bottom: 1px solid #2a3d58;
}

.product-image {
  width: 100%;
  height: 100%;
  object-fit: contain;
}

.product-image-placeholder {
  color: #94a3b8;
  font-size: 0.95rem;
}

.card-body {
  padding: 14px 16px;
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.title {
  margin: 0;
  font-size: 1.1rem;
  font-weight: 700;
  color: #f8fbff;
}

.description {
  margin: 0;
  font-size: 0.95rem;
  color: #b8cade;
  min-height: 40px;
}

.price {
  font-size: 1.1rem;
  font-weight: 700;
  color: #60a5fa;
  margin-top: 6px;
}

.actions {
  margin-top: auto;
  display: flex;
  gap: 8px;
  flex-wrap: wrap;

  padding: 14px;
  background: rgba(255, 255, 255, 0.02);
  border-top: 1px solid #2a3d58;
}

.actions button {
  flex: 1;
  min-width: 90px;

  padding: 10px 12px;
  border-radius: 10px;

  font-size: 0.95rem;
  font-weight: 600;

  cursor: pointer;
  border: 1px solid transparent;

  transition: transform 0.15s ease, background 0.2s ease;
}

.actions button:active {
  transform: scale(0.98);
}

.actions button:focus-visible {
  outline: 2px solid #60a5fa;
  outline-offset: 2px;
}

.primary {
  background: #1a7755;
  color: #ffffff;
}

.primary:hover {
  background: rgb(11, 73, 34);
}

.secondary {
  background: #1e293b;
  color: #f8fbff;
  border: 1px solid #334155;
}

.secondary:hover {
  background: #334155;
}

.danger {
  background: #b91c1c;
  color: #ffffff;
}

.danger:hover {
  background: #991b1b;
}
</style>