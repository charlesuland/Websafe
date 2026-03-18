<script setup>
    import { useBuilderStore } from '@/stores/builderStore'

    const store = useBuilderStore()

    function updateStyle(key, value) {
        const component = store.selectedComponent

        if (!component.props.style)
            component.props.style = {}

        component.props.style[key] = value
    }
</script>

<template>
    <div class="toolbar">
        <button class="publish-button" @click="$emit('publish')">Publish</button>
        <div class="toolbar-item" v-if="store.selectedComponent?.props.style?.fontSize !== undefined">
            <h4>Font Size:</h4>
            <input
                type="number"
                min="10"
                max="72"
                :value="store.selectedComponent.props.style.fontSize"
                @input="updateStyle('fontSize', $event.target.value)"
            />
        </div>

        <div class="toolbar-item" v-if="store.selectedComponent?.props.style?.textAlign !== undefined">
            <h4>Text Alignment:</h4>
            <button
                @click="updateStyle('textAlign', 'left')"
            >
            Left
            </button>
            <button 
                @click="updateStyle('textAlign', 'center')"
            >
            Center
            </button>
            <button 
                @click="updateStyle('textAlign', 'right')"
            >
            Right
            </button>
        </div>

        <div class="toolbar-item" v-if="store.selectedComponent?.props.style?.color !== undefined">
            <h4>Font Color:</h4>
            <input
                type="color"
                :value="store.selectedComponent.props.style.color"
                @input="updateStyle('color', $event.target.value)"
            />
        </div>

        <div class="toolbar-item" v-if="store.selectedComponent?.props.style?.backgroundColor !== undefined">
            <h4>Background Color:</h4>
            <input
                type="color"
                :value="store.selectedComponent.props.style.backgroundColor"
                @input="updateStyle('backgroundColor', $event.target.value)"
            />
        </div>

        <div class="toolbar-item" v-if="store.selectedComponent?.props.style?.backgroundOpacity !== undefined">
            <h4>Background Opacity:</h4>
            <input
                type="range"
                id="opacityValue"
                min="0"
                max="1"
                step="0.01"
                :value="store.selectedComponent.props.style.backgroundOpacity"
                @change="updateStyle('opacity', $event.target.value)"
            />
        </div>
    </div>
</template>

<style scoped>
    .toolbar {
        display: flex;
        gap: 20px;
        justify-content: right;
        align-content: center;
        background-color: white;
        border-radius: 5px;
        padding: 10px;
        position: fixed;
        right: 0px;
        height: 50px;
        width: 100%;
    }

    .toolbar-item {
        display: flex;
        flex-direction: row;
        gap: 5px;
        color: black;
    }

    h4 {
        font-weight: bold;
    }

    .publish-button {
        position: absolute;
        left: 5px;
        top: 5px;
        bottom: 5px;
        background-color: rgb(0, 123, 255);
        height: 100%;
        width: 100px;
        border: none;
        border-radius: 10px;
        font-size: large;
        font-weight: bold;
        color: white;
    }
</style>