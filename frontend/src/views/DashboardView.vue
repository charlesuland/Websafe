<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { 
  apiFetchProjects,
  apiCreateProject,
  apiDeleteProject
} from '@/DatabaseFunctions.js'
import CreateConnectCard from '@/components/CreateConnectCard.vue'



const projects = ref([])
const router = useRouter()
const loading = ref(false)

onMounted(async () => {
  try {
    const res = await apiFetchProjects()
    projects.value = res
  } catch (error) {
    router.push('/login')
  }
})

async function createProject() {
  const projectName = prompt("Enter new project name")
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

  // Update local state to remove deleted project
  projects.value = projects.value.filter(p => p.id !== project_id)
}

async function openProject(project_id) {
  console.log("Opening project: " + project_id)
  router.push(`/editor/${project_id}`)
}

function viewPublishedSite(project) {
  window.open(`/site/${project.slug}/Home`, '_blank')
}

function formatDateTime(value) {
  if (!value) 
    return 'Not yet'

  const date = parseServerDate(value)
  if (Number.isNaN(date.getTime())) 
    return 'Unknown'

  return date.toLocaleString(undefined, {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
    hour: 'numeric',
    minute: '2-digit',
  })
}

function parseServerDate(value) {
  if (value instanceof Date) return value
  if (typeof value !== 'string') return new Date(value)

  const normalized = value.includes('T') ? value : value.replace(' ', 'T')
  const hasTimezone = /[zZ]$|[+-]\d{2}:\d{2}$/.test(normalized)

  return new Date(hasTimezone ? normalized : `${normalized}Z`)
}
</script>

<template>
  <CreateConnectCard />
  <main class="dashboard-content" aria-labelledby="projects-title">
    <header class="content-header">
      <div>
        <h2 id="projects-title">Your Projects</h2>
        <p class="intro-text">Manage project drafts, published sites, and recent activity.</p>
      </div>

      <button class="primary" type="button" @click="createProject">
        Create Project
      </button>
    </header>

    <div v-if="loading" class="loading-state" role="status" aria-live="polite">
      Loading projects…
    </div>

    <div v-else-if="projects.length === 0" class="empty-state" role="status">
      <p>No projects yet. Create your first one.</p>
    </div>

    <section v-else class="grid" aria-label="Project list">
      <article
        v-for="project in projects"
        :key="project.id"
        class="card"
        :aria-labelledby="`project-${project.id}-title`"
      >
        <div class="card-header">
          <h3 :id="`project-${project.id}-title`" class="project-title">{{ project.name }}</h3>
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
          <div class="meta-block">
            <span class="meta-label">Last Updated</span>
            <strong class="date-text">{{ formatDateTime(project.last_updated) }}</strong>
          </div>
        </div>

        <div class="card-body">
          <div class="meta-block">
            <span class="meta-label">Last Published</span>
            <strong class="date-text">{{ formatDateTime(project.last_published) }}</strong>
          </div>
        </div>

        <div class="card-actions">
          <button type="button" class="secondary-action" @click="openProject(project.id)">
            Edit
          </button>
          <button
            v-if="project.is_live && project.slug"
            type="button"
            @click="viewPublishedSite(project)"
            class="view-site"
          >
            View Site
          </button>
          <button type="button" class="delete" @click="deleteProject(project.id, project.name)">
            Delete
          </button>
        </div>
      </article>
    </section>
  </main>
</template>

<style scoped>
.dashboard-content {
  padding: 2rem 2.5rem 3rem;
  color: #d8e4f2;
}

.content-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 1rem;
  margin-bottom: 1.5rem;
}

.content-header h2 {
  margin: 0;
  color: #f8fbff;
  font-size: 1.75rem;
  font-weight: 700;
}

.primary {
  min-width: 150px;
  padding: 0.8rem 1rem;
  border: 1px solid #4283d8;
  border-radius: 10px;
  background: #1964d5;
  color: #ffffff;
  cursor: pointer;
  font-weight: 700;
}

.primary:hover {
  background: #2464d9;
}

.primary:focus-visible,
.card-actions button:focus-visible {
  outline: 3px solid #f8c35d;
  outline-offset: 3px;
}

.intro-text {
  margin: 0.45rem 0 0;
  color: #b8cade;
  font-size: 0.98rem;
}

.card {
  background: linear-gradient(180deg, #132031 0%, #0f1825 100%);
  border: 1px solid #2a3d58;
  border-radius: 16px;
  padding: 1rem;
  box-shadow: 0 18px 36px rgba(0, 0, 0, 0.22);
  display: flex;
  flex-direction: column;
  gap: 0.85rem;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 0.75rem;
}

.grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 20px;
}

.status {
  padding: 0.35rem 0.7rem;
  border-radius: 999px;
  font-size: 0.8rem;
  font-weight: 700;
}

.status.live {
  background: #d8f7e8;
  color: #0d5e42;
}

.status.draft {
  background: #fff0c2;
  color: #735100;
}

.card-body {
  flex: 1;
}

.project-title {
  margin: 0;
  color: #f8fbff;
  font-size: 1.15rem;
}

.card-actions {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-top: auto;
}

.card-actions button {
  flex: 1;
  min-width: 120px;
  padding: 0.75rem 0.85rem;
  border: 1px solid transparent;
  border-radius: 10px;
  cursor: pointer;
  font-weight: 700;

  font-size: 16px;
  font-weight: 600;
  letter-spacing: 0.2px;
}

.delete {
  background: #ab303c;
  color: #ffffff;
}

.view-site {
  background: #1a7755;
  color: #ffffff;
}

.secondary-action {
  background: #20344e;
  color: #f8fbff;
}

.date-text {
  color: #f8fbff;
  font-size: 1rem;
}

.thumbnail {
  width: 100%;
  height: auto;
  object-fit: cover;
  border-radius: 12px;
  border: 1px solid #324866;
}

.meta-block {
  display: flex;
  flex-direction: column;
  gap: 0.3rem;
}

.meta-label {
  color: #b9cadd;
  font-size: 0.82rem;
  font-weight: 600;
  letter-spacing: 0.02em;
}

.loading-state,
.empty-state {
  text-align: center;
  padding: 40px;
  color: #c6d4e5;
}

.empty-state p {
  font-size: 1.1rem;
  margin: 0;
}

@media (max-width: 720px) {
  .dashboard-content {
    padding: 1.25rem 1rem 2rem;
  }

  .content-header {
    flex-direction: column;
  }

  .primary,
  .card-actions button {
    width: 100%;
  }
}
</style>
