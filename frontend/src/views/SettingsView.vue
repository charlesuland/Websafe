<template>
  <div class="settings-view">
    <h1 class="settings-title">Settings</h1>
    <SlugSetting :projectId="Number(route.params.projectId)" />
  </div>
</template>

<script setup>
import { useRoute } from 'vue-router'
import SlugSetting from '@/components/SlugSetting.vue'

const route = useRoute()
</script>

<style scoped>
.settings-view {
  padding: 32px;
  max-width: 600px;
}

.settings-title {
  font-size: 1.5rem;
  font-weight: 600;
  color: #111;
  margin-bottom: 32px;
}
</style>