<script setup>
import { computed } from 'vue'
import TextBlock from '@/components/blocks/TextBlock.vue'
import ImageBlock from '@/components/blocks/ImageBlock.vue'

const props = defineProps({
  componentData: Object
})

const componentMap = {
  text: TextBlock,
  image: ImageBlock
}

const resolvedComponent = computed(() => {
  return componentMap[props.componentData.type] || null
})
</script>

<template>
  <component
    v-if="resolvedComponent"
    :is="resolvedComponent"
    v-bind="componentData.props"
  />

  <div v-else class="unknown-component">
    Unknown component: {{ componentData.type }}
  </div>
</template>