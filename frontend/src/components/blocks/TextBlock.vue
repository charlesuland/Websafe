<script setup>
import { ref, watch } from 'vue'

const props = defineProps({
  text: {
    type: String
  },
  style: {
    fontSize: 18,
    textAlign: "center",
    backgroundColor: "#ffffff",
    backgroundOpacity: 1,
    color: "#000000"
  }
})

const emit = defineEmits(['update:text'])
const text = ref(props.text)

watch(text, (val) => emit('update:text', val))

function autoResize(e) {
  const el = e.target
  el.style.height = 'auto'
  el.style.height = el.scrollHeight + 'px'
}
</script>

<template>
  <div class="text-block"
    :style="{ 
      backgroundColor: props.style.backgroundColor,
      opacity: props.style.opacity 
    }">
    <textarea
      id="textField"
      placeholder="TEXT"
      v-model="text"
      @input="autoResize"
      :style="{
        fontSize: style.fontSize + 'px',
        textAlign: style.textAlign,
        color: style.color
      }"
    ></textarea>
  </div>
</template>

<style scoped>
  .text-block {
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: stretch;
    padding: 5px;
    height: 100%;
    width: 100%;
    background-color: blue;
    position: relative;
    border-radius: 10px;
    border-color: black;
    border-width: 30px;
    border: solid;
  }

  #textField {
    width: 100%;
    height: 100%;
    box-sizing: border-box;
    min-height: 30px;
    font-size: 12px;
    text-align: center;
    overflow-wrap: break-word;
    padding: 0.5em;
    border: none;
    resize: none;
    line-height: auto;
    background-color: transparent;
  }

  #textField:hover {
    border: solid;
    border-color: black;
  }
</style>