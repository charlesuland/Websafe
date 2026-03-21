<script setup>
import { useRouter } from 'vue-router'

const props = defineProps({
  links: Array,
  style: {
    fontSize: 18,
    textAlign: "center",
    backgroundColor: "#ffffff",
    backgroundOpacity: 1,
    color: "#000000"
  }
})

const router = useRouter()

function goTo(page) {
  // router.push(`/site/demo/${page.toLowerCase()}`)
}
</script>

<template>
  <div class="navbar" :style="{ backgroundColor: style.backgroundColor, color: style.color }">
    <span
      v-for="link in links"
      :key="link"
      @click="goTo(link)"
      class="nav-link"
    >
      {{ link }}
    </span>
  </div>
</template>

<style scoped>
.navbar {
  border-radius: 5px;
  display: flex;
  justify-content: space-between;
  gap: 20px;
  padding: 10px;
}

.nav-link {
  cursor: pointer;
}
</style>