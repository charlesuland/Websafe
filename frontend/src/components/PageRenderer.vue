<script setup>
import { ref } from 'vue'
import ComponentRenderer from './ComponentRenderer.vue';

const components = ref([])

function loadFile(e) {
    const file = e.target.files[0]
    const reader = new FileReader()

    reader.onload = () => {
        const data = JSON.parse(reader.result)
        components.value = data.components
    }

    reader.readAsText(file)
}
</script>

<template>
    <input type="file" @change="loadFile" />

    <div class="render-canvas">
        <div
            v-for="component in components"
            :key = component.id
            class="render-item"
            :style="{
                gridColumn: component.col + ' / span ' + component.colSpan,
                gridRow: component.row + ' / span ' + component.rowSpan
            }"
        >
            <ComponentRenderer :componentData="component" />
        </div>
    </div>
</template>

<style scoped>
.render-canvas {
  display: grid;
  grid-template-columns: repeat(12, 1fr);
  grid-auto-rows: 80px;

  width: 100%;
  min-height: 100vh;

  background: white;
}

.render-item {
  display: flex;
  align-items: center;
  justify-content: center;
}
</style>