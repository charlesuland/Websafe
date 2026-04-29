<script setup>
import { ref, watch, onMounted, computed, nextTick } from 'vue'
import { useBuilderStore } from '@/stores/builderStore'
import { hexToRgb } from '@/utils/colorUtils.js'

const props = defineProps({
  links: Array,
  projectId: String,
  style: {
    fontSize: 18,
    backgroundColor: "#ffffff",
    backgroundOpacity: 1,
    color: "#000000"
  }
})

const emit = defineEmits(['update:links'])
const links = ref(
  props.links.map(l => ({
    id: l.id || crypto.randomUUID(),
    name: l.name ?? l
  }))
)
const availablePages = ref([])
const store = useBuilderStore()
const updatingFromProps = ref(false)

function getAvailableOptionsForIndex(currentIndex) {
  const options = [...availablePages.value]
  
  const currentLink = links.value[currentIndex]?.name
  if (currentLink && !options.includes(currentLink)) {
    options.push(currentLink)
  }
  
  return options
}

watch(() => props.links, async (newLinks) => {
  updatingFromProps.value = true
  links.value = newLinks.map(l => ({
    id: l.id || crypto.randomUUID(),
    name: l.name ?? l
  }))
  await nextTick()
  updatingFromProps.value = false
}, { deep: true })

watch(links, (newLinks) => {
  if (!updatingFromProps.value) {
    emit('update:links', newLinks.map(l => ({ ...l })))
  }
}, { deep: true, immediate: false })

watch(() => props.projectId, (newProjectId) => {
  console.log('projectId changed to:', newProjectId)
  if (newProjectId) {
    fetchAvailablePages()
  }
})

onMounted(async () => {
  console.log('EditorNavbar mounted with projectId:', props.projectId)
  if (props.projectId) {
    await fetchAvailablePages()
  } else {
    console.warn('EditorNavbar: projectId not provided, pages will not be fetched')
  }
})

async function fetchAvailablePages() {
  try {
    const pages = store.pages
    console.log('Pages from store:', pages)
    if (pages.length > 0) {
      availablePages.value = pages.map(page => page.name)
      console.log('Available pages from store:', availablePages.value)
      return
    }
  } catch (error) {
    console.error('Failed to fetch available pages:', error)
  }
}

async function addLink() {
  links.value.push({
    id: crypto.randomUUID(),
    name: ''
  })
  await nextTick
}

function removeLink(index) {
  links.value.splice(index, 1)
}

function updateLink(index, newValue) {
  links.value[index].name = newValue
}

const navbarContainerStyle = computed(() => {
  const s = props.style || {}

  const rgb = hexToRgb(s.backgroundColor || '#fff')
  const opacity = s.backgroundOpacity ?? 1

  return {
    backgroundColor: `rgba(${rgb}, ${opacity})`
  }
})

const selectStyle = computed(() => {
  const s = props.style || {}
  return {
    fontSize: (s.fontSize || 18) + 'px',
    color: s.color || '#000'
  }
})

</script>

<template>
  <div class="navbar" :style="navbarContainerStyle">
    <div class="nav-link-container" v-for="(link, index) in links" :key="link.id">
      <select
        :value="link.name"
        @change="updateLink(index, $event.target.value)"
        class="nav-link-select"
        :style="selectStyle"
      >
        <option value="">Select Page</option>
        <option
          v-for="page in getAvailableOptionsForIndex(index)"
          :key="page"
          :value="page"
        >
          {{ page }}
        </option>
      </select>
      <button @click="removeLink(index)" class="remove-link-btn">×</button>
    </div>
    <button @click="addLink" class="add-link-btn">+</button>
  </div>
</template>

<style scoped>
.navbar {
  width: 100%;
  border-radius: 5px;
  display: flex;
  justify-content: center;
  gap: 10px;
  padding: 10px;
  align-items: center;
}

.nav-link-container {
  display: flex;
  align-items: center;
  gap: 5px;
  position: relative;
}

.nav-link-select {
  padding: 8px 12px;
  border: 2px solid #ccc;
  border-radius: 4px;
  background: #ffffff;
  color: #333;
  min-width: 120px;
  font-size: inherit;
  cursor: pointer;
  appearance: auto;
  z-index: 1000;
  position: relative;
}

.nav-link-select:focus {
  outline: none;
  border-color: #0066cc;
  box-shadow: 0 0 4px rgba(0, 102, 204, 0.3);
}

.nav-link-select option {
  background: #ffffff;
  color: #333;
  padding: 8px;
  margin: 4px 0;
}

.remove-link-btn {
  background: #ff4444;
  color: white;
  border: none;
  border-radius: 50%;
  width: 20px;
  height: 20px;
  cursor: pointer;
  font-size: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.add-link-btn {
  background: #4CAF50;
  color: white;
  border: none;
  border-radius: 50%;
  width: 24px;
  height: 24px;
  cursor: pointer;
  font-size: 16px;
  display: flex;
  align-items: center;
  justify-content: center;
}
</style>
