<script setup>
import { useBuilderStore } from '@/stores/builderStore'
import '@/assets/trash_icon.png'

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
    <img
      src="@/assets/trash_icon.png"
      alt="Trash icon"
      class="trash-icon"
    />
  </div>
</template>

<style scoped>
.trash-zone {
  position: fixed;
  bottom: 20px;
  left: 20px;
  z-index: 50;

  width: 150px;
  height: 80px;
  background: #dc2626;
  color: #ffffff;

  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  text-align: center;

  font-weight: bold;
  box-shadow: 0 6px 18px rgba(0,0,0,.4);
}

.trash-icon {
  width: 40px;
  height: 40px;
  margin: 8px;
}
</style>