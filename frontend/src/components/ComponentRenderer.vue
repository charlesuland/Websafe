<script setup>
import { computed } from 'vue'
import TextBlock from '@/components/blocks/TextBlock.vue'
import ImageBlock from '@/components/blocks/ImageBlock.vue'
import EditorNavbar from '@/components/blocks/EditorNavbar.vue'

const props = defineProps({
  componentData: Object
})

const componentMap = {
  text: TextBlock,
  image: ImageBlock,
  navbar: EditorNavbar
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
    @update:src="value => updateProp('src', value)"
    @update:text="value => updateProp('text', value)"
  />

  <div v-else class="unknown-component">
    Unknown component: {{ componentData.type }}
  </div>
</template>