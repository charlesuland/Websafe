<script setup>
    import { VueDraggable } from 'vue-draggable-plus'
    import { useBuilderStore } from '@/stores/builderStore.js'
    import ComponentRenderer from '@/components/ComponentRenderer.vue'

    const store = useBuilderStore()

    function onDrop(event) {
        const data = event.dataTransfer.getData('component')
        if (!data) return

        console.log('Dropped data:', data)

        const component = JSON.parse(data)

        store.addComponent({
            id: crypto.randomUUID(),
            type: component.type,
            props: component.type === 'text' ? { text: 'New Text Block' }
                : component.type === 'image' ? { src: 'https://via.placeholder.com/150' }
                : {},
            children: []
        })
    }
</script>

<template>
  <div
    class="canvas"
    @drop="onDrop"
    @dragover.prevent
    @dragenter.prevent
  >
    <VueDraggable
      v-model="store.components">
      item-key="id"
      animation="200"
      ghost-class="ghost"
    >
      <template #item="{ element }">
        <ComponentRenderer :componentData="element" />
      </template>
    </VueDraggable>
  </div>
</template>

<style scoped>
    div.canvas {
        display: flex;
        background-color: gray;
        flex-direction: column;
        align-items: center;
        justify-content: start;
        min-height: 100%;
        flex: 1;
        overflow-y: auto;
        padding: 1rem;
    }

    .ghost {
        opacity: 0.5;
    }
</style>
