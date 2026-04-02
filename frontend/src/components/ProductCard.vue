<script setup>

import { assignToProject } from '@/views/ProductsView.vue'

const selectedProject = ref(null)

</script>


<template>
<select v-model="selectedProject" @change="assignToProject(product.id, selectedProject)">
    <option disabled selected>Assign to project</option>
    <option v-for="p in projects" :value="p.id">{{  p.name  }}</option>
</select>
</template>


<style scoped>

</style>