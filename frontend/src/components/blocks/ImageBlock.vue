<script setup>
import { useRoute } from 'vue-router'
import placeholder from '@/assets/placeholder_image.jpg'
import { apiFetch } from '@/auth.js'
import { hexToRgb } from '@/utils/colorUtils.js'

const props = defineProps({
  src: { type: String, default: "" },
  alt: { type: String, default: "Image" },
  style: {
      backgroundColor: "#ffffff",
      backgroundOpacity: 1,
    }
})

const emit = defineEmits(["update:src"])
const route = useRoute()

async function handleUpload(event) {
  const file = event.target.files[0]
  if (!file) return

  const projectId = route.params.projectId
  if (!projectId) {
    console.error('No project ID found for editor image upload')
    return
  }

  const formData = new FormData()
  formData.append('file', file)
  formData.append('alt_text', props.alt)

  const res = await apiFetch(`/api/projects/${projectId}/upload-image`, {
    method: 'POST',
    body: formData
  })

  if (!res.ok) {
    console.error('Image upload failed', await res.text())
    return
  }

  const data = await res.json()
  emit('update:src', data.url)
}
</script>

<template>
  <div class="image-block">
    <div class="image-container"
      :style="{
        backgroundColor: `rgba(${hexToRgb(style.backgroundColor)}, ${style.backgroundOpacity})`
      }">
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
