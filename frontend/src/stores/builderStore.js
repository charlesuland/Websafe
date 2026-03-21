import { defineStore } from 'pinia'
import { ref } from 'vue'

export const useBuilderStore = defineStore('builder', () => {
  const components = ref([])
  const selectedComponent = ref(null)

  const pages = ref([])
  const currentPage = ref('Home')

  const renderKey = ref(0)

  function setPages(pageList) {
    pages.value = pageList

    if (pageList.length > 0) {
      currentPage.value = pageList[0].name
      components.value = pageList[0].layout || []
    }
  }

  function getPageComponents() {
    const page = pageList.value.find(p => p.name === currentPage.value)
    return page?.layout || []
  }

  function updateCurrentPageLayout() {
    let page = pages.value.find(p => p.name === currentPage.value)
    if (page) {
      page.layout = components.value
    }
  }

  function setPageComponents(newComponents) {
    let page = pages.value.find(p => p.name === currentPage.value)
    if (page) {
      page.layout = newComponents
    } else {
      page = {
        name: currentPage.value,
        layout: newComponents
      }
      pages.value.push(page)
    }
    components.value = newComponents
  }

  function addComponent(component) {
    components.value.push(component)
  }

  function removeComponent(component_id) {
    setTimeout(() => {
      components.value = components.value.filter(c => c.id !== component_id)
      console.log("Removed component: " + component_id)
      renderKey.value++
    })
  }

  function selectComponent(component) {
    console.log("Selected component: " + component.id + " " + component.props["text"])
    selectedComponent.value = component
  }

  function deselectComponent() {
    selectedComponent.value = null
  }

  return {
    components,
    selectedComponent,
    pages,
    currentPage,
    renderKey,
    setPages,
    getPageComponents,
    setPageComponents,
    updateCurrentPageLayout,
    addComponent,
    removeComponent,
    selectComponent,
    deselectComponent
  }
})