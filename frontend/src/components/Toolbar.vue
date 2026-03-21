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
    <div class="toolbar" v-if="store.selectedComponent">
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
        align-items: center;
        gap: 20px;
        flex-wrap: wrap;
        padding: 10px 16px;
        border-radius: 8px;
    }

    .toolbar-item {
        display: flex;
        align-items: center;
        height: 50px;
        gap: 8px;
        background: #e4e4e4;
        box-shadow: 0 2px 6px rgba(0,0,0,0.05);
        padding: 6px 10px;
        border-radius: 6px;
    }

    .toolbar-item h4 {
        font-size: 12px;
        margin: 0;
        color: #555;
    }

    .toolbar-item input[type="number"] {
        width: 60px;
    }

    .toolbar-item input[type="color"] {
        border: none;
        width: 32px;
        height: 32px;
        padding: 0;
        background: none;
        cursor: pointer;
    }

    .toolbar-item button {
        padding: 4px 8px;
        border-radius: 6px;
        border: none;
        background: #ddd;
        cursor: pointer;
        font-size: 12px;
    }

    .toolbar-item button:hover {
        background: #ccc;
    }
</style>