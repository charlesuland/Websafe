<script setup>
  const paletteItems = [
    { type: 'text', label: 'Text Block' },
    { type: 'image', label: 'Image Block' }
    // Not implemented yet so just holding off until text and images are solid
    //{ type: 'container', label: 'Container' }
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
    display: flex;
    flex-direction: column;
    gap: 5px;
    width: 100%;
    height: 100%;
    background-color: gray;
    height: 100%;
    padding: 20px;
    border-radius: 10px;
  }

  .palette-item {
    background: #3a3a3a;
    border-radius: 8px;
    padding: 12px;
    cursor: grab;
    text-align: center;
    font-weight: bold;
    border: 1px solid darkgray;
    box-shadow: 10px, 10px, 5px, black;
    transition: all .2s ease;
  }

  .palette-item:hover {
    background: #4a4a4a;
    border-color: #5a8cff;
  }

  .palette-item:active {
    cursor: grabbing;
    transform: scale(0.98);
  }
</style>