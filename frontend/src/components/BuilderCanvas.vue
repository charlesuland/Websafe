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

const componentDefaults = {
  text: {
    colSpan: 4,
    rowSpan: 1,
    props: { text: "New Text Block" }
  },

  image: {
    colSpan: 6,
    rowSpan: 3,
    props: { src: placeholder }
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

  store.addComponent({
    id: crypto.randomUUID(),
    type: component.type,
    col,
    row,
    colSpan: config.colSpan,
    rowSpan: config.rowSpan,
    props: config.props,
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
  <div class="canvas"
       ref="canvas"
       @drop="onDrop"
       @dragover.prevent>

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
        draggable="true"

        @dragstart="startDrag($event, component)"
        @drag="dragMove($event, component)"
        @dragend="dragEnd($event, component)"

        :style="{
          gridColumn: component.col + ' / span ' + component.colSpan,
          gridRow: component.row + ' / span ' + component.rowSpan
        }"
      >
        <ComponentRenderer :componentData="component" />
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
  height: 100%;
  min-height: 800px;

  background-color: #918fb0;

  background-image:
    linear-gradient(#b0b0b0 1px, transparent 1px),
    linear-gradient(90deg, #ccc 1px, transparent 1px);

  background-size:
    100% 80px,
    calc(100% / 12) 100%; 

  background-repeat: repeat;
  background-blend-mode: lighten;

  box-shadow: inset 0 0 15px rgba(0,0,0,0.1);
}

.canvas-item {
  border-radius: 10px;
  background-color: rgba(113,113,113,0.85);

  border: 2px solid #444;

  padding: 12px;
  height: auto;
  position: relative;
}

.canvas-item:hover {
  border-width: 2px;
  border: solid;
  border-color: rgb(0, 255, 242);
  transition: border 0.2s ease;
}

.resize-handle {
  position: absolute;
  bottom: 6px;
  right: 6px;

  width: 16px;
  height: 16px;

  cursor: se-resize;

  background:
    linear-gradient(135deg, transparent 50%, #666 50%),
    linear-gradient(135deg, transparent 65%, #999 65%);
}
</style>