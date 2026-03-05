<script setup>
import ComponentPallete from './ComponentPallete.vue'
import BuilderCanvas from './BuilderCanvas.vue'
</script>

<template>
  <div class="editor-layout">
    <ComponentPallete class="palette"/>
    <BuilderCanvas class="canvas"/>
  </div>
</template>

<style scoped>
    .editor-layout {
        display: flex;
        height: 100vh;
        width: 100vw;
    }

    .palette {
        width: 250px;
        background: #767676;
        border-right: 1px solid #ccc
    }

    .canvas {
        flex: 1;
        padding: 1rem;
        overflow: auto;
    }
</style>