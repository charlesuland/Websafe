<script setup>
import ComponentPallete from './ComponentPallete.vue'
import BuilderCanvas from './BuilderCanvas.vue'
import TrashZone from './TrashZone.vue'
import Toolbar from './Toolbar.vue'
import { useBuilderStore } from '@/stores/builderStore'
import { onMounted, onUnmounted } from 'vue'

const store = useBuilderStore()

function publishLayout() {
  const layout = {
    components: store.components
  }

  const json = JSON.stringify(layout, null, 2)
  downloadJSON(json)
}

function downloadJSON(json) {
  const blob = new Blob([json], { type: 'application/json' })
  const url = URL.createObjectURL(blob)

  const a = document.createElement('a')
  a.href = url
  a.download = 'layout.json'
  a.click()

  URL.revokeObjectURL(url)
}

function handleKeyDown(e) {
  const target = e.target

  const isTyping =
    target.tagName === 'INPUT' ||
    target.tagName === 'TEXTAREA' ||
    target.isContentEditable

  if (isTyping) return

  const isDeleteCombo =
    (e.key === 'Delete' || e.key === 'Backspace') &&
    (e.metaKey || e.ctrlKey)

  if (isDeleteCombo) {
    e.preventDefault()

    if (store.selectedComponent) {
      store.removeComponent(store.selectedComponent.id)
      store.selectedComponent = null
    }
  }

  if (e.key === 'Escape') {
    store.selectedComponent = null
  }
}

onMounted(() => {
    window.addEventListener('keydown', handleKeyDown)
})

onUnmounted(() => {
    window.removeEventListener('keydown', handleKeyDown)
})

</script>

<template>
  <div class="editor-layout">
    <header class="toolbar">
      <Toolbar @publish="publishLayout"/>
    </header>

    <aside class="sidebar">
      <ComponentPallete />
    </aside>

    <main class="canvas-area">
      <BuilderCanvas :key="store.renderKey" />
    </main>

    <div class="trash">
      <TrashZone />
    </div>
  </div>
</template>

<style scoped>
.trash {
  position: fixed;
  bottom: 20px;
  right: 20px;
  z-index: 20;
}

.editor-layout {
  display: grid;
  position: fixed;
  left: 0;
  top: 0;
  grid-template-columns: 250px 1fr;
  grid-template-rows: 60px 1fr;

  grid-template-areas:
    "toolbar toolbar"
    "sidebar canvas";

  height: 100vh;
  width: 100vw;

  overflow: hidden;
}

.toolbar {
  grid-area: toolbar;
  background: #ffffff;
  z-index: 10;
}

.sidebar {
  grid-area: sidebar;
  background: gray;
  overflow-y: auto;
}

.canvas-area {
  grid-area: canvas;
  overflow-y: auto;
  overflow-x: hidden;
  position: relative;
}
</style>