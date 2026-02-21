<script setup>
  const props = defineProps({
    src: {
      type: String,
      default: ""
    },
    alt: {
      type: String,
      default: ""
    }
  })
</script>

<template>
  <div class="image-block">
    <img :src="src" :alt="alt"/>
  </div>
</template>

<style scoped>
</style>