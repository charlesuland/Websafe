<script setup>
import ComponentPallete from './ComponentPallete.vue'
import BuilderCanvas from './BuilderCanvas.vue'
import TrashZone from './TrashZone.vue'
</script>

<template>
  <div class="editor-layout">

    <aside>
      <ComponentPallete />
    </aside>

    <main>
      <BuilderCanvas />
    </main>

    <TrashZone />

  </div>
</template>

<style scoped>

main {
  flex: 1;
  display: flex;
  width: 100%;
  height: 100%;
  position: relative;
}

.editor-layout {
  display: flex;
  height: 100vh;
  width: 100vw;

  background: #1e1e1e;
  color: white;
  overflow: hidden;
}

</style>