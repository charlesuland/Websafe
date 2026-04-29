<script setup>
const props = defineProps({
  productId: {
    type: Number,
    required: true
  },
  name: {
    type: String,
    required: true
  },
  description: {
    type: String,
    default: ''
  },
  price: {
    type: Number,
    default: 0
  },
  imageUrl: {
    type: String,
    default: null
  },
  altText: {
    type: String,
    default: 'Product image'
  },
  inStock: {
    type: Boolean,
    default: true
  }
})
</script>

<template>
  <div class="product-card">
    <div v-if="imageUrl" class="product-image-container">
      <img :src="imageUrl" :alt="altText" class="product-image" />
    </div>
    <div v-else class="product-image-placeholder">No Image</div>
    
    <div class="product-info">
      <h3>{{ name }}</h3>
      <p class="description">{{ description }}</p>
      <div class="product-footer">
        <strong class="price">${{ (price / 100).toFixed(2) }}</strong>
        <div class="stock-status">
          <span v-if="inStock" class="in-stock">In Stock</span>
          <span v-else class="out-of-stock">Out of Stock</span>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.product-card {
  background: #ffffff;
  border: 1px solid #e8e8e8;
  border-radius: 12px;
  overflow: hidden;
  display: flex;
  flex-direction: column;
  height: 100%;
  width: 100%;
  box-sizing: border-box;
  transition: transform 0.2s ease, box-shadow 0.2s ease;
}

.product-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 10px 18px rgba(0, 0, 0, 0.08);
}

.product-image-container {
  width: 100%;
  aspect-ratio: 1 / 1;
  background-color: #f5f5f5;
  overflow: hidden;
}

.product-image {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.product-image-placeholder {
  width: 100%;
  aspect-ratio: 1 / 1;
  background-color: #e5e5e5;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #999;
  font-size: 0.85rem;
}

.product-info {
  padding: 14px;
  display: flex;
  flex-direction: column;
  gap: 6px;
  flex: 1;
}

.product-info h3 {
  font-size: 0.95rem;
  font-weight: 600;
  color: #222;
  margin: 0;

  display: -webkit-box;
  -webkit-line-clamp: 1;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.description {
  font-size: 0.85rem;
  color: #666;

  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.product-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: auto;
}

.price {
  font-size: 1rem;
  font-weight: 600;
  color: #2563eb;
}

.stock-status {
  font-size: 0.7rem;
  font-weight: 600;
  text-transform: uppercase;
}

.in-stock {
  color: #22c55e;
}

.out-of-stock {
  color: #ef4444;
}
</style>
