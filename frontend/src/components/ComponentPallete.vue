<script setup>
const paletteItems = [
  { type: 'text', label: 'Text Block' },
  { type: 'image', label: 'Image Block' },
  { type: 'navbar', label: 'Navbar' },
]

function startDrag(type, event) {
  event.dataTransfer.setData(
    'component',
    JSON.stringify({ type })
  )
}
</script>

<template>
  <div 
    class="palette" 
    role="region" 
    aria-label="Component palette"
  >
    <button
      v-for="item in paletteItems"
      :key="item.type"
      class="palette-item"
      type="button"
      draggable="true"
      :aria-label="`Drag ${item.label}`"
      @dragstart="startDrag(item.type, $event)"
    >
      {{ item.label }}
    </button>
  </div>
</template>

<style scoped>
.palette {
  display: flex;
  flex-direction: column;
  gap: 8px;
  background-color: #1f2937;
  padding: 16px;
  border-radius: 10px;
}

.palette-item {
  background: #2563eb;
  color: #ffffff;
  border: none;
  border-radius: 8px;
  padding: 12px;
  cursor: grab;
  text-align: center;
  font-weight: 600;
  transition: all 0.2s ease;
}

.palette-item:hover {
  background: #1d4ed8;
}

.palette-item:active {
  cursor: grabbing;
  transform: scale(0.97);
}

/* KEYBOARD FOCUS */
.palette-item:focus-visible {
  outline: 3px solid #60a5fa;
  outline-offset: 2px;
}
</style>