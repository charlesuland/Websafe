<script setup>
import { VueDraggable } from 'vue-draggable-plus'
import { useBuilderStore } from '@/stores/builderStore'
import ComponentRenderer from '@/components/ComponentRenderer.vue'
import { computed } from 'vue'

const store = useBuilderStore()

const components = computed({
  get: () => store.components,
  set: (val) => store.components = val
})

function onDrop(event) {
  const data = event.dataTransfer.getData('component')
  if (!data) return

  const component = JSON.parse(data)

  store.addComponent({
    id: crypto.randomUUID(),
    type: component.type,
    props:
      component.type === 'text'
        ? { text: 'New Text Block' }
        : component.type === 'image'
        ? { src: 'https://via.placeholder.com/150' }
        : {},
    children: []
  })
}
</script>

<template>
  <div class="canvas"
       @drop="onDrop"
       @dragover.prevent>

    <VueDraggable
      v-model="components"
      item-key="id"
      tag="div"
      animation="200"
    >
      <div class="canvas-item" v-for="component in components">
        <ComponentRenderer :componentData="component" />
      </div>
    </VueDraggable>

  </div>
</template>

<style scoped>
.canvas {
  flex: 1;
  min-height: 100vh;
  width: 100%;
  padding: 1rem;
  background-color: #b9b9b9;
}

.canvas-item {
  color: black;
  border-radius: 10px;
  background: white;
  padding: 12px;
  margin-bottom: 10px;
  min-height: 40px;
}
</style>