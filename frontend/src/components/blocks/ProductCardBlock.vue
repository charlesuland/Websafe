<script setup>
import { ref } from 'vue'
import { useCartStore } from '@/stores/cartStore'
import { useRouter } from 'vue-router'

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
  shippingPrice: {
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
  },
  projectId: { 
    type: String, 
    default: null 
  }
})


const cart = useCartStore()
const router = useRouter()
const added = ref(false)

function addToCart() {
  if (!props.inStock) return
  if (props.projectId) cart.setProject(props.projectId)
  cart.addItem({
    productId: props.productId,
    name: props.name,
    price: props.price,
    shippingPrice: props.shippingPrice,
    imageUrl: props.imageUrl,
    altText: props.altText,
  })
  added.value = true
  setTimeout(() => {added.value = false}, 1600)
}

function goToCheckout() {
  const pid = props.projectId || cart.projectId
  if (pid) router.push(`/checkout/${pid}`)
}
</script>

<template>
  <div class="product-card" :class="{ 'out-of-stock-card': !inStock }">
    <div v-if="imageUrl" class="product-image-container">
      <img :src="imageUrl" :alt="altText" class="product-image" />
    </div>
    <div v-else class="product-image-placeholder">No Image</div>

    <div class="product-info">
      <h3>{{ name }}</h3>
      <p class="description">{{ description }}</p>

      <div class="product-footer">
        <div class="price-block">
          <strong class="price">${{ (price / 100).toFixed(2) }}</strong>
          <span v-if="shippingPrice > 0" class="shipping-note">+ ${{ (shippingPrice / 100).toFixed(2) }} shipping</span>
          <span v-else class="shipping-note free-ship">Free shipping</span>
        </div>
        <span v-if="inStock" class="in-stock">In Stock</span>
        <span v-else class="out-of-stock">Out of Stock</span>
      </div>

      <div class="card-actions">
        <button class="btn-cart" :class="{ added }" :disabled="!inStock" @click="addToCart">
          <span v-if="added">✓ Added!</span>
          <span v-else>Add to Cart</span>
        </button>
        <button v-if="cart.totalItems > 0" class="btn-checkout" @click="goToCheckout">
          Checkout ({{ cart.totalItems }})
        </button>
      </div>
    </div>
  </div>
</template>

<style scoped>
.product-card {
  background: #ffffff;
  border: 1px solid #e8e8e8;
  border-radius: 12px;
  overflow: visible;
  display: flex;
  flex-direction: column;
  height: auto;
  min-height: 100%;
  width: 100%;
  box-sizing: border-box;
  transition: transform 0.2s ease, box-shadow 0.2s ease;
}

.product-image-container {
  width: 100%;
  aspect-ratio: 1 / 1; /* keeps images perfectly square */
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
  gap: 8px;
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

  /*  multi-line truncation */
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




.card-actions { display: flex; gap: 8px; margin-top: 4px; }

.btn-cart {
  flex: 1; 
  padding: 9px 12px; 
  border: none; 
  border-radius: 8px;
  background: #1d4ed8; 
  color: #fff; 
  font-size: 0.82rem; 
  font-weight: 600;
  cursor: pointer; 
  transition: background 0.15s, transform 0.1s;
}

.btn-cart:hover:not(:disabled) { 
  background: #1e40af; 

}
.btn-cart:active:not(:disabled) { 
  transform: scale(0.97); 
}

.btn-cart.added { 
  background: #16a34a; 
}

.btn-cart:disabled { 
  background: #9ca3af; 
  cursor: not-allowed; 
}

.btn-checkout {
  padding: 9px 12px; 
  border: 2px solid #1d4ed8; 
  border-radius: 8px;
  background: transparent; 
  color: #1d4ed8; 
  font-size: 0.82rem; 
  font-weight: 600;
  cursor: pointer; 
  transition: all 0.15s; 
  white-space: nowrap;
}
.btn-checkout:hover { 
  background: #1d4ed8; 
  color: #fff; 
}
</style>
