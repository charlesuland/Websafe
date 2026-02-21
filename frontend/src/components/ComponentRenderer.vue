<script setup>
    import TextBlock from '@/components/blocks/TextBlock.vue'
    import ImageBlock from '@/components/blocks/ImageBlock.vue'
    //import ContainerBlock from '@/components/blocks/ContainerBlock.vue'

    const props = defineProps({
        componentData: Object
    })

    const componentMap = {
        text: TextBlock,
        image: ImageBlock
    }

    console.log('ComponentRenderer mounting with:', props.componentData)
</script>

<template>
  <component
    :is="componentMap[componentData.type]"
    v-bind="componentData.props"
  />
</template>
