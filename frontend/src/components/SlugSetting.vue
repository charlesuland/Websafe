<script setup>
import { ref, watch, computed, onMounted } from 'vue'
import { getProjectSlug, setProjectSlug } from '@/DatabaseFunctions'

const props = defineProps({
  projectId: { type: Number, required: true },
  projectName: { type: String, default: '' }
})

const inputVal = ref('')
const currentSlug = ref(null)
const saving = ref(false)
const errorMsg = ref('')
const successMsg = ref('')

// Live preview of what the URL will look like after slugification
const slugPreview = computed(() => {
  if (!inputVal.value.trim()) return ''
  return inputVal.value
    .toLowerCase()
    .trim()
    .replace(/[^\w\s-]/g, '')
    .replace(/[\s_]+/g, '-')
    .replace(/-+/g, '-')
    .replace(/^-+|-+$/g, '')
})

const previewUrl = computed(() =>
  slugPreview.value ? `/site/${slugPreview.value}/Home` : ''
)

const isChanged = computed(() => slugPreview.value && slugPreview.value !== currentSlug.value)

onMounted(async () => {
  try {
    const data = await getProjectSlug(props.projectId)
    currentSlug.value = data.slug
    inputVal.value = data.slug || ''
  } catch {
    // no slug set yet, fine
  }
})

async function save() {
  if (!isChanged.value) return
  saving.value = true
  errorMsg.value = ''
  successMsg.value = ''
  try {
    const data = await setProjectSlug(props.projectId, inputVal.value)
    currentSlug.value = data.slug
    inputVal.value = data.slug
    successMsg.value = 'URL saved!'
    setTimeout(() => (successMsg.value = ''), 3000)
  } catch (err) {
    errorMsg.value = err.message
  } finally {
    saving.value = false
  }
}
</script>

<template>
  <div class="slug-setting">
    <div class="slug-label">Custom store URL</div>
    <p class="slug-hint">
      This is the link people will use to visit your published store.
    </p>

    <div class="slug-input-row">
      <span class="slug-prefix">websafe.com/site/</span>
      <input
        v-model="inputVal"
        class="slug-input"
        type="text"
        placeholder="my-shop-name"
        :disabled="saving"
        @keyup.enter="save"
      />
    </div>

    <div class="slug-preview" v-if="slugPreview">
      Preview: <a :href="previewUrl" target="_blank">{{ previewUrl }}</a>
    </div>

    <div class="slug-error" v-if="errorMsg">{{ errorMsg }}</div>
    <div class="slug-success" v-if="successMsg">{{ successMsg }}</div>

    <button
      class="slug-save"
      :disabled="!isChanged || saving"
      @click="save"
    >
      {{ saving ? 'Saving...' : 'Save URL' }}
    </button>
  </div>
</template>

<style scoped>
.slug-setting {
  padding: 20px 0;
  max-width: 480px;
}

.slug-label {
  font-size: 0.85rem;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.08em;
  color: #475569;
  margin-bottom: 4px;
}

.slug-hint {
  font-size: 0.88rem;
  color: #64748b;
  margin-bottom: 14px;
}

.slug-input-row {
  display: flex;
  align-items: center;
  border: 1px solid #cbd5e1;
  border-radius: 8px;
  overflow: hidden;
  background: #fff;
}

.slug-prefix {
  padding: 9px 10px 9px 14px;
  font-size: 0.88rem;
  color: #94a3b8;
  background: #f8fafc;
  border-right: 1px solid #e2e8f0;
  white-space: nowrap;
  user-select: none;
}

.slug-input {
  flex: 1;
  padding: 9px 12px;
  font-size: 0.92rem;
  border: none;
  outline: none;
  color: #0f172a;
  background: transparent;
}

.slug-preview {
  margin-top: 8px;
  font-size: 0.82rem;
  color: #64748b;
}

.slug-preview a {
  color: #2563eb;
  text-decoration: none;
}

.slug-preview a:hover {
  text-decoration: underline;
}

.slug-error {
  margin-top: 8px;
  font-size: 0.84rem;
  color: #dc2626;
}

.slug-success {
  margin-top: 8px;
  font-size: 0.84rem;
  color: #16a34a;
}

.slug-save {
  margin-top: 14px;
  padding: 9px 22px;
  font-size: 0.9rem;
  font-weight: 500;
  border: none;
  border-radius: 8px;
  background: #2563eb;
  color: #fff;
  cursor: pointer;
  transition: background 0.15s, opacity 0.15s;
}

.slug-save:disabled {
  opacity: 0.45;
  cursor: not-allowed;
}

.slug-save:not(:disabled):hover {
  background: #1d4ed8;
}
</style>