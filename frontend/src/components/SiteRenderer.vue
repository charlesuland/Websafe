<script setup>
import { computed } from 'vue'
import PublishedTextBlock from '@/components/blocks/PublishedTextBlock.vue'
import PublishedImageBlock from '@/components/blocks/PublishedImageBlock.vue'
import PublishedNavbar from '@/components/blocks/PublishedNavbar.vue'
import ProductCardBlock from '@/components/blocks/ProductCardBlock.vue'

const props = defineProps({
  componentData: {
    type: Object,
    required: true
  },
  projectId: {
    type: String,
    required: true
  },
  hasProducts: {
    type: Boolean,
    default: false
  }
})

const componentMap = {
  text: PublishedTextBlock,
  image: PublishedImageBlock,
  navbar: PublishedNavbar,
  product: ProductCardBlock,
}

const resolvedComponent = computed(() => {
  return componentMap[props.componentData.type] || null
})
</script>

<template>
  <div class="site-component-wrapper">
    <component
      v-if="resolvedComponent"
      :is="resolvedComponent"
      v-bind="componentData.props"
      :projectId="projectId"
      :hasProducts="hasProducts"
    />
  </div>
</template>

<style scoped>
.site-component-wrapper {
  width: 100%;
  height: 100%;
  display: flex;
  flex-direction: column;
}

.site-component-wrapper:last-child {
  margin-bottom: 0;
}

.unknown-component {
  padding: 20px;
  background: #f5f5f5;
  border: 1px solid #ddd;
  border-radius: 4px;
  color: #666;
  font-size: 14px;
  text-align: center;
}
</style>