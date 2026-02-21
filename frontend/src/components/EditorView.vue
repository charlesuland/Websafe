<script setup>
    import ComponentPallete from './ComponentPallete.vue';
    import BuilderCanvas from './BuilderCanvas.vue';
    import { useBuilderStore } from '@/stores/builderStore';

    const store = useBuilderStore()
</script>

<template>
    <div>
        <BuilderCanvas class="canvas"/>
        <ComponentPallete class="pallete"/>
    </div>
</template>

<style scoped>
    .editor-layout {
        display: flex;
        height: 100vh;
    }

    .palette {
        justify-content: center;;
        background: #f0f0f0;
        padding: 1rem;
    }

    .canvas {
        justify-content: center;
        width: 80%;
        padding: 1rem;
        overflow: auto;
    }
</style>