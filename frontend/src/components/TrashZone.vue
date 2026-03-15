<script setup>
import { useBuilderStore } from '@/stores/builderStore'

const store = useBuilderStore()

function onDrop(event) {
  const id = event.dataTransfer.getData('component-id')
  if (!id) return

  store.removeComponent(id)
}
</script>

<template>
  <div
    class="trash-zone"
    @dragover.prevent
    @drop="onDrop"
  >
    Drag Here To Delete
  </div>
</template>

<style scoped>
    .trash-zone {
        position: fixed;
        bottom: 25px;
        right: 25px;
        width: 110px;
        height: 110px;
        background: #ff4d4d;
        border-radius: 12px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-weight: bold;
        cursor: pointer;
        box-shadow: 0 6px 18px rgba(0,0,0,.3);
    }
</style>