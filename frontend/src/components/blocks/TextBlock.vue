<script setup>
import { ref, watch } from 'vue'

const props = defineProps({
  text: { type: String, default: 'TEXT BOX' }
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
  <div class="text-block">
    <textarea
      id="textField"
      placeholder="TEXT"
      v-model="text"
      @input="autoResize"
    ></textarea>
  </div>
</template>

<style scoped>
  .text-block {
    width: 100%;
    height: 100%;
    display: flex;
    align-items: center;
    justify-content: center;
    padding: 5px;
  }

  #textField {
    width: 90%;
    min-height: 40px;
    max-height: 100%;
    font-size: clamp(14px, 2vw, 24px);
    text-align: center;
    line-height: 1.4;
    resize: none;
    overflow: hidden;
    border: none;
    background: transparent;
  }

  #inputField::placeholder {
    color: black;
  }

  #inputField:hover {
    border: solid;
    border-color: black;
    border-radius: 5px;
  }
</style>