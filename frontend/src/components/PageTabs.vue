<script setup>
import { useBuilderStore } from '@/stores/builderStore'

const store = useBuilderStore()

function selectPage(name) {
  store.updateCurrentPageLayout()
  store.currentPage = name

  const page = store.pages.find(p => p.name === name)
  store.setPageComponents(page?.layout || [])
}

function addPage() {
  const name = prompt("Page name?")
  if (!name) return

  if (store.pages.some(p => p.name === name)) {
    alert("Page already exists")
    return
  }

  store.pages.push({
    name,
    layout: []
  })

  selectPage(name)
}

function renamePage(page) {
  const newName = prompt("Rename page", page.name)
  if (!newName) return

  if (store.pages.some(p => p.name === newName)) {
    alert("Page already exists")
    return
  }

  page.name = newName
}

/* 🔑 KEYBOARD NAVIGATION (arrow keys like real tabs) */
function handleKeydown(e, index) {
  const tabs = store.pages
  if (!tabs.length) return

  if (e.key === 'ArrowRight') {
    const next = (index + 1) % tabs.length
    selectPage(tabs[next].name)
  }

  if (e.key === 'ArrowLeft') {
    const prev = (index - 1 + tabs.length) % tabs.length
    selectPage(tabs[prev].name)
  }
}
</script>

<template>
  <div class="tabs-container">
    <h2 class="tabs-header">Pages</h2>

    <div 
      class="tabs" 
      role="tablist" 
      aria-label="Project pages"
    >
      <button
        v-for="(page, index) in store.pages"
        :key="page.name"
        class="tab""
        :class="{ active: page.name === store.currentPage }"
        @click="selectPage(page.name)"
        @dblclick="renamePage(page)"
        @keydown="handleKeydown($event, index)"

        role="tab"
        type="button"
        tabindex="0"
        :aria-selected="page.name === store.currentPage"
        :aria-label="`Page ${page.name}`"
      >
        {{ page.name }}
      </button>

      <button 
        class="tab add" 
        type="button"
        @click="addPage"
        role="tab"
        aria-label="Add new page"
      >
        +
      </button>
    </div>
  </div>
</template>

<style scoped>
.tabs-container {
  display: flex;
  align-items: center;
  gap: 20px;
  width: 100%;
  background: #111827;
  padding: 0 10px;
}

.tabs-header {
  color: #f9fafb;
}

.tabs {
  display: flex;
  gap: 6px;
  align-items: center;
  height: 50px;
}

.tab {
  padding: 8px 14px;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  font-size: 14px;

  background: transparent;
  color: #d1d5db; /* lighter gray for readability */
  transition: all 0.2s ease;
}

.tab:hover {
  background: #374151;
  color: #ffffff;
}

.tab.active {
  background: #2563eb;
  color: white;
  font-weight: 500;
}

.tab.add {
  font-weight: bold;
  font-size: 16px;
  color: #60a5fa;
}

.tab.add:hover {
  background: #1e3a8a;
  color: #ffffff;
}

.tab:focus-visible {
  outline: 3px solid #f59e0b;
  outline-offset: 2px;
}
</style>