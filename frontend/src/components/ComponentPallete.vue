<script setup>
  const paletteItems = [
    { type: 'text', label: 'Text Block' },
    { type: 'image', label: 'Image Block' },
    { type: 'navbar', label: 'Navbar' }
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
    background-color: rgb(226, 226, 226);
    box-shadow: inset 0 0px 5px rgba(0, 0, 0, 0.5);
    height: 100%;
    padding: 20px;
    border-radius: 10px;
    border: solid;
    border-color: rgb(255, 255, 255);
    border-width: 5px;
  }

  .palette-item {
    background: #2f7df6;
    color: white;
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
    background: #99c2ff;
    border-color: #5a8cff;
  }

  .palette-item:active {
    cursor: grabbing;
    transform: scale(0.98);
  }
</style>