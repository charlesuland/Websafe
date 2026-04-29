<script setup>
import { VueDraggable } from 'vue-draggable-plus'
import { useBuilderStore } from '@/stores/builderStore'
import ComponentRenderer from '@/components/ComponentRenderer.vue'
import { computed } from 'vue'
import { ref } from 'vue'
import placeholder from '@/assets/placeholder_image.jpg'

const store = useBuilderStore()
const canvas = ref(null)
const resizing = ref(null)
const dragging = ref(null)

const props = defineProps({
  projectId: String
})

const componentDefaults = {
  text: {
    colSpan: 4,
    rowSpan: 1,
    props: {
      text: "New Text Block",
      style: {
        fontSize: 18,
        textAlign: "center",
        backgroundColor: "#ffffff",
        backgroundOpacity: 1,
        color: "#000000"
      }
    },
  },

  image: {
    colSpan: 6,
    rowSpan: 3,
    props: { 
      src: placeholder,
      style: {
        backgroundColor: "#ffffff",
        backgroundOpacity: 1
      }
    }
  },

  navbar: {
    colSpan: 12,
    rowSpan: 1,
    props: {
      links: ["Home"],
      style: {
        backgroundColor: "#ffffff",
        backgroundOpacity: 1,
        fontSize: 18,
        color: "#000000"
      }
    }
  },

  product: {
    colSpan: 4,
    rowSpan: 3,
    props: {
      productId: 0,
      name: "Sample Product",
      description: "Product description goes here",
      price: 2999,
      imageUrl: null,
      altText: "Product image",
      inStock: true
    }
  }
}

const components = computed({
  get: () => store.components,
  set: (val) => store.components = val
})

function startResize(event, component) {
  event.stopPropagation()
  event.preventDefault(); 

  resizing.value = {
    component,
    startX: event.clientX,
    startY: event.clientY,
    startColSpan: component.colSpan,
    startRowSpan: component.rowSpan,
  }

  window.addEventListener("mousemove", resizeMove)
  window.addEventListener("mouseup", stopResize)
}

function resizeMove(event) {
  const canvasRect = canvas.value.getBoundingClientRect()

  const colWidth = canvasRect.width / 12
  const rowHeight = 80

  const dx = event.clientX - resizing.value.startX
  const dy = event.clientY - resizing.value.startY

  const dCols = Math.round(dx / colWidth)
  const dRows = Math.round(dy / rowHeight)

  resizing.value.component.colSpan = Math.max(1, resizing.value.startColSpan + dCols)
  resizing.value.component.rowSpan = Math.max(1, resizing.value.startRowSpan + dRows)
}

function stopResize() {
  window.removeEventListener("mousemove", resizeMove)
  window.removeEventListener("mouseup", stopResize)
  resizing.value = null
}

function onDrop(event) {
  const data = event.dataTransfer.getData('component')
  if (!data) return

  const component = JSON.parse(data)

  const { col, row } = getGridPosition(event, canvas.value, dragging.value)

  const config = componentDefaults[component.type]
  
  if (!config) {
    console.error(`Component type "${component.type}" not found in defaults`)
    return
  }

  store.addComponent({
    id: crypto.randomUUID(),
    type: component.type,
    col,
    row,
    colSpan: config.colSpan,
    rowSpan: config.rowSpan,
    props: structuredClone(config.props),
    children: []
  })
}

function startDrag(event, component) {
  if (resizing.value) return

  event.dataTransfer.setData("component-id", component.id);

  dragging.value = component
  event.dataTransfer.effectAllowed = 'move'

  const crt = document.createElement('div')
  crt.style.width = '0px'
  crt.style.height = '0px'
  event.dataTransfer.setDragImage(crt, 0, 0)
}

function dragMove(event, component) {
  if (!dragging.value) return

  const { col, row } = getGridPosition(event, canvas.value, dragging.value)

  dragging.value.col = col
  dragging.value.row = row
}

function dragEnd(event, component) {
  dragging.value = null
}

function getGridPosition(event, canvas, component = null) {
  const rect = canvas.getBoundingClientRect()
  const x = event.clientX - rect.left
  const y = event.clientY - rect.top

  const colWidth = rect.width / 12
  const rowHeight = 80

  let col = Math.round(x / colWidth)
  let row = Math.round(y / rowHeight)

  if (component) {
    col = Math.round((x - (component.colSpan * colWidth) / 2) / colWidth)
    row = Math.round((y - (component.rowSpan * rowHeight) / 2) / rowHeight)
  }

  col = Math.max(1, Math.min(12 - (component?.colSpan ?? 1) + 1, col))
  row = Math.max(1, row)

  return { col, row }
}

</script>

<template>
  <div 
    class="canvas"
    ref="canvas"
    @drop="onDrop"
    @dragover.prevent
    @click.self="store.deselectComponent"
  >
    <VueDraggable
      v-model="components"
      item-key="id"
      tag="div"
      class="vue-draggable-wrapper"
      animation="200"
    >
      <div 
        class="canvas-item"
        v-for="component in components"
        :key="component.id"
        :class="{ selected: store.selectedComponent?.id === component.id }"
        draggable="true"

        @dragstart="startDrag($event, component)"
        @drag="dragMove($event, component)"
        @dragend="dragEnd($event, component)"
        @click="store.selectComponent(component)"
        
        :style="{
          gridColumn: (component.col) + ' / span ' + component.colSpan,
          gridRow: (component.row) + ' / span ' + component.rowSpan
        }"
      >
        <ComponentRenderer :componentData="component" :projectId="projectId" />
        <div class="resize-handle" @mousedown="startResize($event, component)" draggable="false"></div>
      </div>
    </VueDraggable>
  </div>
</template>

<style scoped>
.vue-draggable-wrapper {
  display: contents;
}

.canvas {
  display: grid;
  grid-template-columns: repeat(12, 1fr);
  grid-auto-rows: 80px;
  width: 100%;
  min-height: 800px;

  background-color: #ffffff;

  background-image:
    linear-gradient(#e5e7eb 1px, transparent 1px),
    linear-gradient(90deg, #e5e7eb 1px, transparent 1px);

  background-size:
    100% 80px,
    calc(100% / 12) 100%;

  box-shadow: inset 0 0 10px rgba(0,0,0,0.08);
}

.canvas-item {
  display: flex;
  position: relative;
  overflow: hidden;
}

.canvas-item.selected {
  outline: 3px solid #2563eb;
}

.canvas-item:hover:not(.selected) {
  outline: 2px solid #93c5fd;
}

.canvas-item:focus-visible {
  outline: 3px solid #f59e0b;
  outline-offset: 2px;
}

.canvas-item:active {
  cursor: grabbing;
  transform: scale(0.98);
  box-shadow: 0 4px 12px rgba(0,0,0,0.7);
  transition: transform 0.1s ease, box-shadow 0.1s ease;
}

.resize-handle {
  position: absolute;
  bottom: 6px;
  right: 6px;
  width: 16px;
  height: 16px;
  cursor: se-resize;

  background:
    linear-gradient(135deg, transparent 50%, #444 50%),
    linear-gradient(135deg, transparent 65%, #888 65%);
}
</style>