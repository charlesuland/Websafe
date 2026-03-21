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

const route = useRoute()
const projectId = route.params.projectId
const canvasRef = ref(null)

const savingState = ref(null)

const router = useRouter()
const store = useBuilderStore()

onMounted(async () => {
  const token = localStorage.getItem('token')

  const res = await fetch(`/api/projects/${projectId}/draft-pages`, {
    method: 'GET',
    headers: {
      'Content-Type': 'application/json',
      Authorization: `Bearer ${token}`
    },
  })
  const pages = await res.json()

  console.log(pages)
  store.setPages(pages)
})

async function saveDraft() {
  const start = Date.now()
  savingState.value = 'saving'

  const token = localStorage.getItem('token')

  store.updateCurrentPageLayout()

  const previewImage = await captureCanvas()

  const res = await fetch(`/api/projects/${projectId}/draft`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      Authorization: `Bearer ${token}`
    },
    body: JSON.stringify({
      pages: store.pages,
      preview: previewImage
    })
  })

  if (!res.ok) {
    console.error("Save failed", await res.text())
  }

  const elapsed = Date.now() - start
  const minDuration = 600

  setTimeout(() => {
    savingState.value = 'saved'

    setTimeout(() => {
      savingState.value = null
    }, 1200)

  }, Math.max(0, minDuration - elapsed))
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

async function publishLayout() {
  await fetch(`/api/projects/${projectId}/publish`, {
    method: 'POST'
  })
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
        <button class="secondary" @click="saveDraft">Save</button>
        <button class="primary" @click="publishLayout">Publish</button>
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
        <BuilderCanvas :key="store.renderKey" />
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
    background: #ffffff;
    border-bottom: 1px solid #e5e5e5;
    z-index: 10;
  }

  .topbar .left,
  .topbar .center,
  .topbar .right {
    display: flex;
    align-items: center;
    gap: 10px;
  }

  .toolbar {
    grid-area: toolbar;
    display: flex;
    align-items: center;
    justify-content: space-evenly;
    height: 80px;

    padding: 16px 16px;
    background-color: #cecece;
    z-index: 10;
  }

  .sidebar {
    grid-area: sidebar;
    background: #c2c2c2;
    color: white;
    padding: 10px;
    overflow-y: auto;
  }

  .canvas-area {
    grid-area: canvas;
    background: #f5f5f5;
    overflow: auto;
    display: flex;
    justify-content: center;
    align-items: flex-start;
    padding: 20px;
  }

  .canvas-wrapper {
    width: 100%;
    max-width: 1100px;
    background: white;
    border-radius: 12px;
    box-shadow: 0 10px 30px rgba(0,0,0,0.1);
    overflow: hidden;
  }

  .trash {
    position: fixed;
    bottom: 20px;
    left: 20px;
    z-index: 20;
  }

  button {
    border: none;
    border-radius: 8px;
    padding: 8px 14px;
    cursor: pointer;
  }

  .primary {
    background: #2f7df6;
    color: white;
  }

  .secondary {
    background: #eee;
  }

  .back-button {
    font-weight: 500;
  }

  .save-icon {
    position: fixed;
    right: 30px;
    bottom: 30px;

    background-color: #2f7df6;
    color: white;

    z-index: 20;
    padding: 10px 16px;
    border-radius: 999px;

    font-size: 14px;
    font-weight: 500;
    box-shadow: 0 4px 12px rgba(0,0,0,0.1);

    animation: fadeIn 0.2s ease
  }

  .saved {
    background: rgba(40, 167, 69, 0.9);
  }

  @keyframes fadeIn {
    from {
      opacity: 0;
      transform: translateY(10px);
    }
    to {
      opacity: 1;
      transform: translateY(0);
    }
  }
</style>