<script setup>
import placeholder from '@/assets/placeholder_image.jpg'

const props = defineProps({
  src: { type: String, default: "" },
  alt: { type: String, default: "Image" },
  style: {
    backgroundColor: "gray",
    backgroundOpacity: 1
  }
})

const emit = defineEmits(["update:src"])

function handleUpload(event) {
  const file = event.target.files[0]
  if (!file) return

  const reader = new FileReader()
  reader.onload = (e) => emit("update:src", e.target.result)
  reader.readAsDataURL(file)
}
</script>

<template>
  <div class="image-block">
    <div class="image-container">
      <img :src="src || placeholder" :alt="alt" />
      <div class="overlay">
        <label class="upload-button">
          Upload Image
          <input type="file" accept="image/*" @change="handleUpload" hidden />
        </label>
      </div>
    </div>
  </div>
</template>

<style scoped>
.image-block {
  width: 100%;
  height: 100%;
  display: flex;
  justify-content: center;
  align-items: center;
}

.image-container {
  position: relative;
  width: 100%;
  height: 100%;
  overflow: hidden;
  border-radius: 10px;
  border: 2px dashed #ccc;
  background-color: white;
  aspect-ratio: 16 / 9;
}

img {
  width: 100%;
  height: 100%;
  object-fit: contain;
  display: block;
}

.overlay {
  position: absolute;
  inset: 0;
  display: flex;
  justify-content: center;
  align-items: center;
  background: rgba(0, 0, 0, 0.4);
  color: gray;
  opacity: 0;
  transition: opacity 0.2s ease;
}

.image-container:hover .overlay {
  opacity: 1;
}

.upload-button {
  background: white;
  padding: 8px 14px;
  border-radius: 6px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
}
</style>
