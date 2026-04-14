<script setup>
const props = defineProps({
  text: {
    type: String,
    default: ""
  },
  style: {
    type: Object,
    default: () => ({
      fontSize: 18,
      textAlign: "center",
      backgroundColor: "#ffffff",
      backgroundOpacity: 1,
      color: "#000000"
    })
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
      backgroundColor: style.backgroundColor,
      opacity: style.backgroundOpacity
    }"
  >
    {{ text }}
  </div>
</template>

<style scoped>
.published-text-block {
  padding: 10px;
  white-space: pre-wrap;
  word-wrap: break-word;
  line-height: 1.4;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
}
</style>