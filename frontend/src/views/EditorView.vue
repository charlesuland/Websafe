<script setup>
import ComponentPallete from '@/components/ComponentPallete.vue'
import BuilderCanvas from '@/components/BuilderCanvas.vue'
import TrashZone from '@/components/TrashZone.vue'
import Toolbar from '@/components/Toolbar.vue'
import PageTabs from '@/components/PageTabs.vue'
import { useBuilderStore } from '@/stores/builderStore'
import { onMounted, onUnmounted, ref } from 'vue'
import { useRoute } from 'vue-router'
import { useRouter } from 'vue-router'
import html2canvas from 'html2canvas'
import { apiFetch } from '@/auth'
import { apiHasActiveSubscription } from '@/DatabaseFunctions.js'

const route = useRoute()
const projectId = route.params.projectId
const canvasRef = ref(null)

const savingState = ref(null)

const router = useRouter()
const store = useBuilderStore()

onMounted(async () => {
  const res = await apiFetch(`/api/projects/${projectId}/get-draft-pages`, {
    method: 'GET',
    headers: {
      'Content-Type': 'application/json'
    },
  })
  const pages = await res.json()

  console.log(pages)
  store.setPages(pages)
})

async function saveDraft({ showStatus = true } = {}) {
  const start = Date.now()
  if (showStatus) {
    savingState.value = 'saving'
  }

  store.updateCurrentPageLayout()

  const previewImage = await captureCanvas()

  const res = await apiFetch(`/api/projects/${projectId}/save-draft`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      pages: store.pages,
      preview: previewImage
    })
  })

  if (!res.ok) {
    console.error('Save failed', await res.text())
    if (showStatus) {
      savingState.value = null
    }
    return false
  }

  if (showStatus) {
    const elapsed = Date.now() - start
    const minDuration = 600

    setTimeout(() => {
      savingState.value = 'saved'

      setTimeout(() => {
        savingState.value = null
      }, 1200)

    }, Math.max(0, minDuration - elapsed))
  }

  return true
}

async function publishLayout() {
  savingState.value = 'saving'

  store.updateCurrentPageLayout()

  const draftSaved = await saveDraft({ showStatus: false })
  if (!draftSaved) {
    savingState.value = null
    alert('Unable to save draft before publishing.')
    return
  }

  const hasSubscription = await apiHasActiveSubscription()

  if (!hasSubscription) {
    alert('You need an active subscription to publish your site. Redirecting to subscriptions page.')
    savingState.value = null
    router.push('/subscriptions')
    return
  }

  const res = await apiFetch(`/api/projects/${projectId}/publish`, {
    method: 'POST'
  })

  if (!res.ok) {
    console.error('Publish failed', await res.text())
    savingState.value = null
    alert(`Publish failed, ${await res.text()}`)
    return
  }

  savingState.value = 'published'
  setTimeout(() => {
    savingState.value = null
  }, 1500)
}

async function captureCanvas() {
  if (!canvasRef.value)
    return null

  const canvasImage = await html2canvas(canvasRef.value, {
    useCORS: true,
    x: 0,
    y: 0,
    windowWidth: canvasRef.value.Width,
    windowHeight: 400
  })

  return canvasImage.toDataURL('image/png')
}

async function exitEditor() {
  await saveDraft()
  router.push('/dashboard')
}

function handleKeyDown(e) {
  const target = e.target

  const isTyping =
    target.tagName === 'INPUT' ||
    target.tagName === 'TEXTAREA' ||
    target.isContentEditable

  if (isTyping) return

  const isDeleteCombo =
    (e.key === 'Delete' || e.key === 'Backspace') &&
    (e.metaKey || e.ctrlKey)

  if (isDeleteCombo) {
    e.preventDefault()

    if (store.selectedComponent) {
      store.removeComponent(store.selectedComponent.id)
      store.selectedComponent = null
    }
  }

  if (e.key === 'Escape') {
    store.selectedComponent = null
  }
}

onMounted(() => {
    window.addEventListener('keydown', handleKeyDown)
})

onUnmounted(() => {
    window.removeEventListener('keydown', handleKeyDown)
})

</script>

<template>
  <div class="editor-layout">

    <header class="topbar">
      <div class="left">
        <button class="back-button secondary" @click="exitEditor">Back to Projects</button>
      </div>

      <div class="center">
        <PageTabs />
      </div>

      <div class="right">
        <button class="secondary" @click="saveDraft">Save Draft</button>
        <button class="primary" @click="publishLayout" :disabled="savingState === 'saving'">Publish Site</button>
      </div>
    </header>

    <div class="toolbar">
      <Toolbar />
    </div>
 
    <aside class="sidebar">
      <ComponentPallete />
    </aside>

    <main class="canvas-area">
      <div class="canvas-wrapper" ref="canvasRef">
        <BuilderCanvas :key="store.renderKey" :projectId="projectId" />
      </div>
    </main>

    <div class="trash">
      <TrashZone />
    </div>

    <div v-if="savingState === 'saving'" class="save-icon">
      Saving...
    </div>
    <div v-if="savingState === 'saved'" class="save-icon saved">
      Saved!
    </div>
    <div v-if="savingState === 'published'" class="save-icon published">
      Published!
    </div>
  </div>
</template>

<style scoped>
.editor-layout {
  display: grid;
  grid-template-columns: 260px 1fr;
  grid-template-rows: 60px 70px 1fr;

  grid-template-areas:
    "topbar topbar"
    "toolbar toolbar"
    "sidebar canvas";

  height: 100vh;
  width: 100vw;
}

.topbar {
  grid-area: topbar;
  display: flex;
  align-items: center;
  justify-content: space-between;

  padding: 0 16px;
  background: #111827;
  color: #f9fafb;
}

.toolbar {
  grid-area: toolbar;
  display: flex;
  justify-content: space-evenly;
  align-items: center;

  background-color: #1f2937;
}

.sidebar {
  grid-area: sidebar;
  background: #111827;
  padding: 10px;
  overflow-y: auto;
}

.canvas-area {
  grid-area: canvas;
  background: #0f172a;
  display: flex;
  justify-content: center;
  padding: 20px;
}

.canvas-wrapper {
  width: 100%;
  max-width: 1100px;
  background: #ffffff;
  border-radius: 12px;
  box-shadow: 0 10px 25px rgba(0,0,0,0.25);
}

button {
  border: none;
  border-radius: 8px;
  padding: 8px 14px;
  margin: 5px;
  cursor: pointer;
  font-weight: 500;
}

.primary {
  background: #2563eb;
  color: #ffffff;
}

.primary:hover {
  background: #1d4ed8;
}

.secondary {
  background: #374151;
  color: #f9fafb;
}

.secondary:hover {
  background: #4b5563;
}

button:focus-visible {
  outline: 3px solid #60a5fa;
  outline-offset: 2px;
}

.save-icon {
  position: fixed;
  right: 30px;
  bottom: 30px;

  background-color: #2563eb;
  color: white;
  
  padding: 10px 16px;
  border-radius: 999px;
}

.saved {
  background: #16a34a;
}

.published {
  background: #059669;
}
</style>