<script setup>
import { hexToRgb } from '@/utils/colorUtils.js'

const props = defineProps({
  text: {
    type: String,
    default: ""
  },
  style: {
    fontSize: 18,
    textAlign: "center",
    backgroundColor: "#ffffff",
    backgroundOpacity: 1,
    color: "#000000"
  }
})
</script>

<template>
  <div
    class="published-text-block"
    :style="{
      fontSize: style.fontSize + 'px',
      textAlign: style.textAlign,
      color: style.color,
      background: `rgba(${hexToRgb(style.backgroundColor)}, ${style.backgroundOpacity})`,
    }"
  >
    {{ text }}
  </div>
</template>

<style scoped>
.published-text-block {
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: stretch;
  padding: 5px;
  height: 100%;
  width: 100%;
  position: relative;
  border-radius: 10px;
  font-family: Arial, sans-serif;
}
</style>