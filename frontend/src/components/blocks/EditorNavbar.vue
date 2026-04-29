<script setup>
import { ref, watch, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import { getAuthHeaders } from '@/auth'
import { useBuilderStore } from '@/stores/builderStore'

const props = defineProps({
  links: Array,
  projectId: String,
  style: {
    type: Object,
    default: () => ({
      fontSize: 18,
      textAlign: "center",
      backgroundColor: "#ffffff",
      backgroundOpacity: 1,
      color: "#000000"
    })
  }
})

const emit = defineEmits(['update:links'])
const links = ref([...props.links])
const availablePages = ref([])
const store = useBuilderStore()
const router = useRouter()
const updatingFromProps = ref(false)

function getAvailableOptionsForIndex(currentIndex) {
  const options = [...availablePages.value]
  
  // Always include the current selection for this dropdown
  const currentLink = links.value[currentIndex]
  if (currentLink && !options.includes(currentLink)) {
    options.push(currentLink)
  }
  
  return options
}

watch(() => props.links, (newLinks) => {
  updatingFromProps.value = true
  links.value = [...newLinks]
  updatingFromProps.value = false
}, { deep: true })

watch(links, (newLinks) => {
  if (!updatingFromProps.value) {
    emit('update:links', newLinks)
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

function goTo(page) {
  if (props.projectId) {
    router.push(`/site/${props.projectId}/${encodeURIComponent(page)}`)
  }
}

function addLink() {
  links.value.push('')
}

function removeLink(index) {
  links.value.splice(index, 1)
}

function updateLink(index, newValue) {
  links.value[index] = newValue
}
</script>

<template>
  <div class="navbar" :style="{ backgroundColor: style.backgroundColor, color: style.color }">
    <div class="nav-link-container" v-for="(link, index) in links" :key="index">
      <select
        :value="link"
        @change="updateLink(index, $event.target.value)"
        class="nav-link-select"
        :style="{ fontSize: style.fontSize + 'px' }"
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