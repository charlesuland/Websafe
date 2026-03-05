<script setup>
  const paletteItems = [
    { type: 'text', label: 'Text Block' },
    { type: 'image', label: 'Image' },
    { type: 'container', label: 'Container' }
  ]

  function startDrag(type, event) {
    event.dataTransfer.setData(
      'component',
      JSON.stringify({ type })
    )
  }
</script>

<template>
  <div class="palette">
    <div
      v-for="item in paletteItems"
      :key="item.type"
      class="palette-item"
      draggable="true"
      @dragstart="startDrag(item.type, $event)"
    >
      {{ item.label }}
    </div>
  </div>
</template>

<style scoped>
  .palette-item {
    background-color: rgb(155, 155, 155);
    color: black;
    display: flex;
    justify-content: center;
    border-radius: 5px;
    margin-bottom: 1rem;
    cursor: grab;
  }
</style>