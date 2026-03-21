<script setup>
import { useRoute } from 'vue-router'
import { ref, onMounted, watch } from 'vue'
import ComponentRenderer from '@/components/ComponentRenderer.vue'

const route = useRoute()
const layout = ref([])

async function loadPage() {
  const res = await fetch(
    `/api/projects/${route.params.project}/${route.params.page}`
  )
  layout.value = await res.json()
}

onMounted(loadPage)
watch(() => route.params.page, loadPage)
</script>

<template>
  <div class="published">
    <ComponentRenderer
      v-for="comp in layout"
      :key="comp.id"
      :componentData="comp"
    />
  </div>
</template>