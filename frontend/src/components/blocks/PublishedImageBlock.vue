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
    <div class="published-image-container">
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

.published-image-container {
  width: 100%;
  height: 100%;
  overflow: hidden;
  border-radius: 10px;
  background-color: white;
  aspect-ratio: 16 / 9;
}

.published-image {
  width: 100%;
  height: 100%;
  object-fit: contain;
  display: block;
}

.published-image-placeholder {
  width: 100%;
  height: 100%;
  background-color: #f5f5f5;
  border: 2px dashed #ddd;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #999;
  font-size: 14px;
}
</style>
