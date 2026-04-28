import { defineStore } from 'pinia'
import { ref, computed } from 'vue'

export const useCartStore = defineStore('cart', () => {
  const items = ref([])   // [{ productId, name, price, shippingPrice, imageUrl, quantity }]
  const projectId = ref(null)

  function setProject(id) {
    projectId.value = id
  }

  function addItem(product) {
    const existing = items.value.find(i => i.productId === product.productId)
    if (existing) {
      existing.quantity++
    } else {
      items.value.push({ ...product, quantity: 1 })
    }
  }

  function removeItem(productId) {
    items.value = items.value.filter(i => i.productId !== productId)
  }

  function updateQuantity(productId, qty) {
    const item = items.value.find(i => i.productId === productId)
    if (item) {
      if (qty < 1) removeItem(productId)
      else item.quantity = qty
    }
  }

  function clearCart() {
    items.value = []
    projectId.value = null
  }

  const totalItems = computed(() => items.value.reduce((s, i) => s + i.quantity, 0))

  const subtotalCents = computed(() =>
    items.value.reduce((s, i) => s + i.price * i.quantity, 0)
  )

  const shippingCents = computed(() =>
    items.value.reduce((s, i) => s + i.shippingPrice * i.quantity, 0)
  )

  const totalCents = computed(() => subtotalCents.value + shippingCents.value)

  return {
    items, projectId,
    setProject, addItem, removeItem, updateQuantity, clearCart,
    totalItems, subtotalCents, shippingCents, totalCents,
  }
})