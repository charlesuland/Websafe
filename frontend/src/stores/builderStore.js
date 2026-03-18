import { defineStore } from 'pinia'
import { ref } from 'vue'

export const useBuilderStore = defineStore('builder', () => {
  const components = ref([])
  const selectedComponent = ref(null)
  const renderKey = ref(0)

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
    console.log("Selected component: " + component.id + " " + component.props)
    selectedComponent.value = component
  }

  function deselectComponent() {
    selectedComponent.value = null
  }

  return {
    components,
    selectedComponent,
    addComponent,
    removeComponent,
    selectComponent,
    deselectComponent
  }
})