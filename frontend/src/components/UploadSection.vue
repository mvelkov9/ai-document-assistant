<script setup>
import { ref } from 'vue'

defineProps({
  busy: { type: Boolean, default: false },
})

const emit = defineEmits(['upload'])
const selectedFile = ref(null)
const isDragOver = ref(false)

function onFileChange(event) {
  selectedFile.value = event.target.files?.[0] || null
}

function onDrop(event) {
  isDragOver.value = false
  const file = event.dataTransfer?.files?.[0]
  if (file && file.type === 'application/pdf') {
    selectedFile.value = file
  }
}

function handleUpload() {
  if (!selectedFile.value) return
  emit('upload', selectedFile.value)
  selectedFile.value = null
  const fileInput = document.getElementById('document-upload')
  if (fileInput) fileInput.value = ''
}
</script>

<template>
  <div
    class="upload-zone"
    :class="{ 'drag-over': isDragOver }"
    @dragover.prevent="isDragOver = true"
    @dragleave="isDragOver = false"
    @drop.prevent="onDrop"
  >
    <Transition name="upload-switch" mode="out-in">
      <div v-if="!selectedFile" key="prompt" class="upload-prompt">
        <div class="upload-icon-wrap">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
            <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/>
            <polyline points="17 8 12 3 7 8"/>
            <line x1="12" y1="3" x2="12" y2="15"/>
          </svg>
        </div>
        <p class="upload-title">Povleci PDF datoteko sem</p>
        <p class="upload-hint">ali</p>
        <label for="document-upload" class="upload-browse">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" class="browse-icon"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/></svg>
          Izberi datoteko
        </label>
        <input id="document-upload" type="file" accept="application/pdf,.pdf" class="sr-only" @change="onFileChange" />
        <p class="upload-formats">Podprti formati: PDF (do 15 MB)</p>
      </div>

      <div v-else key="ready" class="upload-ready">
        <div class="file-preview">
          <div class="file-icon-wrap">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
              <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/>
              <polyline points="14 2 14 8 20 8"/>
            </svg>
          </div>
          <div class="file-details">
            <p class="file-name">{{ selectedFile.name }}</p>
            <p class="file-size">{{ (selectedFile.size / (1024 * 1024)).toFixed(2) }} MB</p>
          </div>
        </div>
        <div class="upload-actions">
          <button class="btn-cancel" @click="selectedFile = null">Prekliči</button>
          <button class="btn-upload" :disabled="busy" @click="handleUpload">
            <svg v-if="busy" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" class="btn-icon spin"><path d="M21 12a9 9 0 1 1-6.219-8.56"/></svg>
            <svg v-else viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" class="btn-icon"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="17 8 12 3 7 8"/><line x1="12" y1="3" x2="12" y2="15"/></svg>
            {{ busy ? 'Nalagam...' : 'Naloži' }}
          </button>
        </div>
      </div>
    </Transition>
  </div>
</template>

<style scoped>
.upload-zone {
  border: 2px dashed var(--border);
  border-radius: var(--radius);
  padding: 2.25rem;
  text-align: center;
  transition: all 0.3s ease;
  background: var(--surface-alt);
  position: relative;
}

.upload-zone.drag-over {
  border-color: var(--primary);
  background: var(--primary-light);
  box-shadow: inset 0 0 0 2px rgba(99,102,241,0.08);
}

.upload-prompt {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.35rem;
}

.upload-icon-wrap {
  width: 56px;
  height: 56px;
  border-radius: 50%;
  background: var(--primary-light);
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 0.5rem;
}

.upload-icon-wrap svg {
  width: 26px;
  height: 26px;
  color: var(--primary);
}

.upload-title {
  margin: 0;
  font-size: 0.95rem;
  font-weight: 600;
  color: var(--text);
}

.upload-hint {
  margin: 0;
  font-size: 0.82rem;
  color: var(--text-light);
}

.upload-browse {
  display: inline-flex;
  align-items: center;
  gap: 0.35rem;
  padding: 0.55rem 1.1rem;
  background: linear-gradient(135deg, var(--primary), #818cf8);
  color: white;
  border-radius: var(--radius-sm);
  font-weight: 600;
  font-size: 0.85rem;
  cursor: pointer;
  transition: all 0.2s ease;
  box-shadow: 0 2px 8px rgba(99,102,241,0.25);
  margin-top: 0.25rem;
}

.upload-browse:hover {
  box-shadow: 0 4px 14px rgba(99,102,241,0.35);
  transform: translateY(-1px);
}

.browse-icon {
  width: 15px;
  height: 15px;
}

.upload-formats {
  margin: 0.5rem 0 0;
  font-size: 0.72rem;
  color: var(--text-light);
}

.sr-only {
  position: absolute;
  width: 1px;
  height: 1px;
  padding: 0;
  margin: -1px;
  overflow: hidden;
  clip: rect(0, 0, 0, 0);
  border: 0;
}

.upload-ready {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 1rem;
}

.file-preview {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.file-icon-wrap {
  width: 44px;
  height: 44px;
  background: linear-gradient(135deg, var(--primary-light), rgba(99,102,241,0.12));
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.file-icon-wrap svg {
  width: 22px;
  height: 22px;
  color: var(--primary);
}

.file-details {
  min-width: 0;
}

.file-name {
  margin: 0;
  font-size: 0.9rem;
  font-weight: 600;
  color: var(--text);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  max-width: 320px;
}

.file-size {
  margin: 0.1rem 0 0;
  font-size: 0.76rem;
  color: var(--text-light);
}

.upload-actions {
  display: flex;
  gap: 0.5rem;
  flex-shrink: 0;
}

.btn-cancel {
  padding: 0.55rem 1rem;
  border: 1px solid var(--border);
  border-radius: var(--radius-sm);
  background: var(--surface);
  color: var(--text-muted);
  font-size: 0.85rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.15s ease;
}

.btn-cancel:hover {
  background: var(--surface-alt);
  border-color: var(--text-light);
}

.btn-upload {
  display: inline-flex;
  align-items: center;
  gap: 0.4rem;
  padding: 0.55rem 1.1rem;
  border: 0;
  border-radius: var(--radius-sm);
  background: linear-gradient(135deg, var(--primary), #818cf8);
  color: white;
  font-size: 0.85rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s ease;
  box-shadow: 0 2px 8px rgba(99,102,241,0.25);
}

.btn-upload:hover:not(:disabled) {
  box-shadow: 0 4px 14px rgba(99,102,241,0.35);
}

.btn-upload:disabled {
  opacity: 0.6;
  cursor: not-allowed;
  box-shadow: none;
}

.btn-icon {
  width: 15px;
  height: 15px;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.spin {
  animation: spin 1s linear infinite;
}

.upload-switch-enter-active,
.upload-switch-leave-active {
  transition: all 0.25s ease;
}

.upload-switch-enter-from {
  opacity: 0;
  transform: scale(0.97);
}

.upload-switch-leave-to {
  opacity: 0;
  transform: scale(0.97);
}

@media (max-width: 520px) {
  .upload-ready {
    flex-direction: column;
    align-items: stretch;
  }
}
</style>
