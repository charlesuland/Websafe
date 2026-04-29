<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { 
  apiFetchProjects,
  apiCreateProject,
  apiDeleteProject
} from '@/DatabaseFunctions.js'

const projects = ref([])
const router = useRouter()
const loading = ref(false)

onMounted(async () => {
  const token = localStorage.getItem('token')

  const res = await apiFetchProjects()

  // If unauthorized, redirect to login view
  if (res.status === 401) {
    localStorage.removeItem('token')
    router.push('/login')
    return
  }

  projects.value = res
})

async function createProject() {
  const projectName = prompt("New project name?")
  if (!projectName)
    return

  const project = await apiCreateProject(projectName)

  router.push(`/editor/${project.id}`)
}

async function deleteProject(project_id, project_name) {
  const confirmDelete = confirm(`Delete ${project_name}?`)

  if (!confirmDelete)
    return

  await apiDeleteProject(project_id)

  projects.value = projects.value.filter(p => p.id !== project_id)
}

async function openProject(project_id) {
  console.log("Opening project: " + project_id)
  router.push(`/editor/${project_id}`)
}

function viewPublishedSite(project) {
  window.open(`/site/${project.slug}/Home`, '_blank')
}
</script>

<template>
  <div class="dashboard-content">
    <div class="content-header">
      <h2>Your Projects</h2>

      <button class="primary" @click="createProject">
        + New Project
      </button>
    </div>

    <div v-if="loading" class="loading-state">
      Loading projects...
    </div>

    <div v-else-if="projects.length === 0" class="empty-state">
      <p>No projects yet. Create your first one</p>
    </div>

    <div v-else class="grid">
      <div
        v-for="project in projects"
        :key="project.id"
        class="card"
      >
        <div class="card-header">
          <h3 class="project-text">{{ project.name }}</h3>
          <span :class="['status', project.is_live ? 'live' : 'draft']">
            {{ project.is_live ? 'Live' : 'Draft' }}
          </span>
        </div>

        <div class="card-body">
          <img
            v-if="project.preview_image"
            :src="project.preview_image"
            :alt="project.name + ' preview image'"
            class="thumbnail"
          />
          <p class="project-text">Last Updated:</p>
          <strong>{{ project.last_updated }}</strong>
        </div>

        <div class="card-body">
          <p class="project-text">Last Published:</p>
          <strong>{{ project.last_published }}</strong>
        </div>

        <div class="card-actions">
          <button @click="openProject(project.id)">Edit</button>
          <button v-if="project.is_live && project.slug" @click="viewPublishedSite(project)" class="view-site">View Site</button>
          <button class="delete" @click="deleteProject(project.id, project.name)">Delete</button>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
h2 {
  color: rgb(90, 140, 255);
}

.dashboard-content {
  padding: 30px;
}

.content-header h2 {
  margin: 0;
}

.primary {
  background: rgb(90, 140, 255);
  margin-top: 10px;
  margin-bottom: 10px;
  color: white;
  border: none;
  padding: 10px 16px;
  border-radius: 8px;
  cursor: pointer;
}

.grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
  gap: 20px;
}

.card {
  background: white;
  border-radius: 12px;
  padding: 16px;
  box-shadow: 0 4px 12px rgba(0,0,0,0.08);
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.status {
  padding: 4px 8px;
  border-radius: 12px;
  font-size: 12px;
  font-weight: bold;
}

.status.live {
  background: #d4edda;
  color: #155724;
}

.status.draft {
  background: #fff3cd;
  color: #856404;
}

.card-body {
  flex: 1;
}

.card-actions {
  display: flex;
  gap: 8px;
  margin-top: auto;
}

.card-actions button {
  flex: 1;
  padding: 8px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}

.delete {
  background: #dc3545;
  color: white;
}

.view-site {
  background: #28a745;
  color: white;
}

.project-text {
  color: rgb(90, 140, 255);
}

.thumbnail {
  width: 100%;
  height: auto;
  object-fit: cover;
  border-radius: 8px;
}

.loading-state,
.empty-state {
  text-align: center;
  padding: 40px;
  color: #666;
}

.empty-state p {
  font-size: 1.1rem;
  margin: 0;
}
</style>