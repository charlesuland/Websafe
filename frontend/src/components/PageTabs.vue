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
  
  if (!newName)
    return

  if (store.pages.some(p => p.name === newName)) {
    alert("Page already exists")
    return
  }

  page.name = newName
}
</script>

<template>
  <div class="tabs-container">
    <h2 class="tabs-header">Pages</h2>
    <div class="tabs">
      <div
        v-for="page in store.pages"
        @dblclick="renamePage(page)"
        :key="page.name"
        :class="['tab', page.name === store.currentPage ? 'active' : '']"
        @click="selectPage(page.name)"
      >
        {{ page.name }}
      </div>

      <div class="tab add" @click="addPage">
        +
      </div>
    </div>
  </div>
</template>

<style scoped>
.tabs-container {
  display: flex;
  flex-direction: row;
  align-items: center;
  gap: 20px;
  width: 100%;
  background: #ffffff;
  padding: 0 10px;
}

.tabs-header {
  color: black;
}

.tabs {
  display: flex;
  gap: 6px;
  align-items: center;
  height: 50px;
}

.tab {
  padding: 8px 14px;
  border-radius: 8px;
  cursor: pointer;
  font-size: 14px;
  background: transparent;
  color: #555;
  transition: all 0.2s ease;
}

.tab:hover {
  background: #f3f3f3;
  color: #000;
}

.tab.active {
  background: #2f7df6;
  color: white;
  font-weight: 500;
}

.tab.add {
  font-weight: bold;
  font-size: 16px;
  color: #2f7df6;
}

.tab.add:hover {
  background: #e8f0ff;
}
</style>