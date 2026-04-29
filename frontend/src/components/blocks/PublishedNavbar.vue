<script setup>
import { useRouter } from 'vue-router'
import { computed } from 'vue'
import { hexToRgb } from '@/utils/colorUtils.js'

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
    fontSize: 18,
    backgroundColor: "#ffffff",
    backgroundOpacity: 1,
    color: "#000000"
  }
})

const router = useRouter()

const effectiveLinks = computed(() => {
  const links = props.links || []

  return props.hasProducts
    ? [...links, ...(!links.includes('Shop') ? ['Shop'] : [])]
    : links
})

function goTo(page) {
  router.push(`/site/${props.projectId}/${page}`)
}

const navbarStyle = computed(() => {
  const s = props.style || {}

  const rgb = hexToRgb(s.backgroundColor || '#fff')
  const opacity = s.backgroundOpacity ?? 1

  return {
    backgroundColor: `rgba(${rgb}, ${opacity})`,
    color: s.color || '#000',
    fontSize: (s.fontSize || 18) + 'px'
  }
})
</script>

<template>
  <nav
    class="published-navbar"
    :style="navbarStyle"
  >
    <div class="nav-container">
      <button
        v-for="link in effectiveLinks"
        :key="link.id"
        @click="goTo(link.name)"
        class="nav-link"
        type="button"
        :style="navbarStyle"
      >
        {{ link.name }}
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
