<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'

const projects = ref([])
const router = useRouter()
const loading = ref(false)

onMounted(async () => {
  const token = localStorage.getItem('token')

  const res = await fetch('/api/projects/', {
    headers: {
      Authorization: `Bearer ${token}`
    },
    method: 'GET'
  })

  if (res.status === 401) {
    localStorage.removeItem('token')
    router.push('/login')
    return
  }

  projects.value = await res.json()
})

async function createProject() {
  const projectName = prompt("New project name?")
  if (!projectName)
    return

  const token = localStorage.getItem('token')

  // Create new project
  const res = await fetch('/api/projects/', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      Authorization: `Bearer ${token}`
    },
    body: JSON.stringify({
      name: projectName
    })
  })
  
  const project = await res.json()
  console.log(project)

  router.push(`/editor/${project.id}`)
}

async function deleteProject(project_id, project_name) {
  const token = localStorage.getItem('token')

  const confirmDelete = confirm(`Delete ${project_name}?`)

  if (!confirmDelete)
    return
  
  const res = await fetch(`/api/projects/${project_id}`, {
    method: 'DELETE',
    headers: {
      Authorization: `Bearer ${token}`
    }
  })

  if (!res.ok) {
    alert("Couldn't delete project")
    return
  }

  projects.value = projects.value.filter(p => p.id !== project_id)
}

async function openProject(project_id) {
  console.log("Opening project: " + project_id)
  router.push(`/editor/${project_id}`)
}
</script>

<template>
  <div class="dashboard">

    <header class="topbar">
      <h1>WebSafe</h1>
      <div class="user">Account</div>
    </header>

    <div class="body">

      <aside class="sidebar">
        <button>Projects</button>
        <button>Analytics</button>
        <button>Settings</button>
      </aside>

      <main class="content">

        <div class="content-header">
          <h2>Your Projects</h2>
          
          <button class="primary" @click="createProject">
            + New Project
          </button>
        </div>

        <div v-if="loading">Loading projects...</div>

        <div v-else-if="projects.length === 0">
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
                class="thumbnail"
              />
              <p class="project-text">Last Updated:</p>
              <strong>{{ project.last_updated }}</strong>
            </div>

            <div class="card-body">
              <p class="project-text">Last Updated:</p>
              <strong>{{ project.last_published }}</strong>
            </div>

            <div class="card-actions">
              <button @click="openProject(project.id)">Edit</button>
              <button @click="deleteProject(project.id, project.name)">Delete</button>
            </div>
          </div>
        </div>

      </main>
    </div>
  </div>
</template>

<style scoped>
.dashboard {
  display: flex;
  flex-direction: column;
  height: 100vh;
}

.topbar {
  height: 60px;
  background: #111;
  color: white;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 20px;
}

.body {
  display: flex;
  flex: 1;
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

.sidebar {
  width: 220px;
  background: #1e1e1e;
  padding: 20px;
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.sidebar button {
  background: transparent;
  color: white;
  border: none;
  text-align: left;
  padding: 10px;
  cursor: pointer;
}

.content {
  flex: 1;
  padding: 30px;
  background: #f5f5f5;
  overflow-y: auto;
}

.content-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 25px;
  color: rgb(90, 140, 255);
}

.primary {
  background: rgb(90, 140, 255);
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
  border-radius: 6px;
  font-size: 12px;
}

.status.live {
  background: #d4f8d4;
  color: green;
}

.status.draft {
  background: #eee;
  color: #696969;
}

.card-actions {
  display: flex;
  gap: 10px;
  margin-top: auto;
}

.card-actions button {
  flex: 1;
  padding: 8px;
  border: none;
  border-radius: 6px;
  cursor: pointer;
}
</style>