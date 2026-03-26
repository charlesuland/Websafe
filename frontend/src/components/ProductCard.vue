<script setup>

const selectedProject = ref(null)

async function assignToProject(productId, projectId) {
    const token = localStorage.getItem('token')

    const res = await fetch(`/api/projects/${projectId}/products`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            Authorization: `Bearer ${token}`
        },
        body: JSON.stringify({
            product_ids: [productId]
        })
    })

    if (!res.ok) {
        console.error("Failed to assign project", await res.text())
        return
    }

    console.log(`Product ${productId} assigned to project ${projectId}`)
}

</script>


<template>
<select v-model="selectedProject" @change="assignToProject(product.id, selectedProject)">
    <option disabled selected>Assign to project</option>
    <option v-for="p in projects" :value="p.id">{{  p.name  }}</option>
</select>
</template>


<style scoped>

</style>