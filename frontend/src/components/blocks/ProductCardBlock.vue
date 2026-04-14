<script setup>
defineProps({
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
  border: 1px solid #e0e0e0;
  border-radius: 10px;
  overflow: hidden;
  display: flex;
  flex-direction: column;
  transition: transform 0.2s, box-shadow 0.2s;
  height: 100%;
  width: 100%;
  box-sizing: border-box;
}

.product-card:hover {
  transform: translateY(-3px);
  box-shadow: 0 6px 12px rgba(0, 0, 0, 0.1);
}

.product-image-container {
  width: 100%;
  flex: 0 0 auto;
  height: 120px;
  background-color: #f0f0f0;
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
  height: 120px;
  background-color: #e0e0e0;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #999;
  font-size: 0.85rem;
}

.product-info {
  padding: 12px;
  display: flex;
  flex-direction: column;
  flex: 1;
  overflow: hidden;
}

.product-info h3 {
  font-size: 1rem;
  color: #222;
  margin: 0 0 4px 0;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.description {
  font-size: 0.8rem;
  color: #666;
  margin: 0 0 8px 0;
  flex: 1;
  overflow: hidden;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
}

.product-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: auto;
  flex-shrink: 0;
}

.price {
  font-size: 1rem;
  color: #2f7df6;
  font-weight: bold;
}

.stock-status {
  font-size: 0.75rem;
  font-weight: 600;
}

.in-stock {
  color: #27ae60;
}

.out-of-stock {
  color: #e74c3c;
}
</style>
