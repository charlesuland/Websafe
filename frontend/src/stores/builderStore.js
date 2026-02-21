import { defineStore } from 'pinia'

export const useBuilderStore = defineStore('builder', {
  state: () => ({
    components: [
      {
        id: 'test1',
        type: 'text',
        props: { text: 'Hello, test' },
        children: []
      }
    ]
  }),

  actions: {
    addComponent(component) {
      this.components.push(component)
    }
  }
})