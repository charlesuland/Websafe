<script setup>
const props = defineProps({
  src: {
    type: String,
    default: ""
  },
  alt: {
    type: String,
    default: "Image"
  },
  style: {
    type: Object,
    default: () => ({
      backgroundColor: "gray",
      backgroundOpacity: 1
    })
  }
})
</script>

<template>
  <div class="published-image-block">
    <img
      v-if="src"
      :src="src"
      :alt="alt"
      class="published-image"
    />
    <div v-else class="published-image-placeholder">
      Image not available
    </div>
  </div>
</template>

<style scoped>
.published-image-block {
  width: 100%;
  height: 100%;
  display: flex;
  justify-content: center;
  align-items: center;
}

.published-image {
  max-width: 100%;
  height: auto;
  border-radius: 8px;
}

.published-image-placeholder {
  width: 100%;
  height: 200px;
  background-color: #f5f5f5;
  border: 2px dashed #ddd;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #999;
  font-size: 14px;
}
</style>