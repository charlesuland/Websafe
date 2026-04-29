<script setup>
import { computed } from 'vue'
import TextBlock from '@/components/blocks/TextBlock.vue'
import ImageBlock from '@/components/blocks/ImageBlock.vue'
import EditorNavbar from '@/components/blocks/EditorNavbar.vue'
import ProductCardBlock from '@/components/blocks/ProductCardBlock.vue'

const props = defineProps({
  componentData: Object,
  projectId: String
})

const componentMap = {
  text: TextBlock,
  image: ImageBlock,
  navbar: EditorNavbar,
  product: ProductCardBlock,
}

const resolvedComponent = computed(() => {
  return componentMap[props.componentData.type] || null
})

function updateProp(key, value) {
  props.componentData.props[key] = value
}
</script>

<template>
  <component
    v-if="resolvedComponent"
    :is="resolvedComponent"
    v-bind="componentData.props"
    :projectId="projectId"
    @update:src="value => updateProp('src', value)"
    @update:text="value => updateProp('text', value)"
    @update:links="value => updateProp('links', value)"
  />

  <div v-else class="unknown-component">
    Unknown component type: {{ componentData?.type || 'undefined' }}
  </div>
</template>