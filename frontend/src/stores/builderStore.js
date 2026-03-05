import { defineStore } from 'pinia'

export const useBuilderStore = defineStore('builder', {
  state: () => ({
    components: []
  }),

  actions: {
    addComponent(component) {
      this.components.push(component)
    }
  }
})