import { defineStore } from 'pinia'

export const useBuilderStore = defineStore('builder', {
  state: () => ({
    components: []
  }),

  actions: {
    addComponent(component) {
      this.components.push(component)
    },

    removeComponent(component_id) {
      this.components = this.components.filter(c => c.id !== component_id)
    }
  }
})