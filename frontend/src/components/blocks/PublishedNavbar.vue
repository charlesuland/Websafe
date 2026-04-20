<script setup>
import { useRouter } from 'vue-router'
import { computed } from 'vue'

const props = defineProps({
  links: {
    type: Array,
    default: () => []
  },
  projectId: {
    type: String,
    required: true
  },
  hasProducts: {
    type: Boolean,
    default: false
  },
  style: {
    type: Object,
    default: () => ({
      fontSize: 18,
      textAlign: "center",
      backgroundColor: "#ffffff",
      backgroundOpacity: 1,
      color: "#000000"
    })
  }
})

const router = useRouter()

const effectiveLinks = computed(() => {
  const baseLinks = [...props.links]
  if (props.hasProducts && !baseLinks.includes('Shop')) {
    baseLinks.push('Shop')
  }
  return baseLinks
})

function goTo(page) {
  router.push(`/site/${props.projectId}/${page}`)
}
</script>

<template>
  <nav
    class="published-navbar"
    :style="{
      backgroundColor: style.backgroundColor,
      color: style.color,
      opacity: style.backgroundOpacity
    }"
  >
    <div class="nav-container">
      <button
        v-for="link in effectiveLinks"
        :key="link"
        @click="goTo(link)"
        class="nav-link"
        type="button"
        :style="{ fontSize: style.fontSize + 'px' }"
      >
        {{ link }}
      </button>
    </div>
  </nav>
</template>

<style scoped>
.published-navbar {
  width: 100%;
  height: 100%;
  padding: 15px 0;
  border-bottom: 1px solid #e0e0e0;
  display: flex;
  align-items: center;
}

.nav-container {
  max-width: 1200px;
  margin: 0 auto;
  display: flex;
  justify-content: center;
  gap: 30px;
  padding: 0 20px;
}

.nav-link {
  cursor: pointer;
  padding: 8px 16px;
  border-radius: 4px;
  transition: background-color 0.2s ease;
  display: inline-block;
  background: transparent;
  border: none;
  color: inherit;
}

.nav-link:hover {
  background-color: rgba(0, 0, 0, 0.1);
}

@media (max-width: 768px) {
  .nav-container {
    flex-direction: column;
    gap: 15px;
    align-items: center;
  }

  .nav-link {
    padding: 6px 12px;
  }
}
</style>
