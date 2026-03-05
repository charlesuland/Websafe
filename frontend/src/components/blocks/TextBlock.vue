<script setup>
  const props = defineProps({
    text: {
      type: String,
      default: 'Default Text'
    }
  })
</script>

<template>
  <div>
    {{ text }}
  </div>
</template>

<style scoped>
  div {
    border-radius: 5px;
    background-color: white;
    padding: 1rem;
    margin: 1rem;
    min-width: 200px;
  }
</style>