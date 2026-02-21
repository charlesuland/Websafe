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
  .palette {
    position: fixed;
    top: 0;
    left: 0;
    width: 200px;
    height: 100vh;
    background-color: #f0f0f0;
    border-right: 1px solid #ccc;
    padding: 1rem;
  }
  .palette-item {
    background-color: gray;
    color: black;
    display: flex;
    justify-content: center;
    border-radius: 5px;
    margin-bottom: 1rem;
    cursor: grab;
  }
</style>