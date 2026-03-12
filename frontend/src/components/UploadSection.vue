<script setup>
  import { ref, computed } from 'vue'

  defineProps({
    busy: { type: Boolean, default: false },
  })

  const emit = defineEmits(['upload', 'upload-batch'])
  const fileQueue = ref([])
  const isDragOver = ref(false)
  const isUploading = ref(false)

  const hasFiles = computed(() => fileQueue.value.length > 0)
  const allDone = computed(
    () =>
      hasFiles.value && fileQueue.value.every((f) => f.status === 'done' || f.status === 'failed'),
  )
  const pendingCount = computed(() => fileQueue.value.filter((f) => f.status === 'pending').length)
  const doneCount = computed(() => fileQueue.value.filter((f) => f.status === 'done').length)
  const failedCount = computed(() => fileQueue.value.filter((f) => f.status === 'failed').length)

  function addFiles(files) {
    for (const file of files) {
      if (file.type === 'application/pdf' || file.name.toLowerCase().endsWith('.pdf')) {
        const exists = fileQueue.value.some(
          (f) => f.file.name === file.name && f.file.size === file.size,
        )
        if (!exists) {
          fileQueue.value.push({ file, status: 'pending', progress: 0 })
        }
      }
    }
  }

  function onFileChange(event) {
    const files = event.target.files
    if (files?.length) addFiles(files)
    event.target.value = ''
  }

  function onDrop(event) {
    isDragOver.value = false
    const files = event.dataTransfer?.files
    if (files?.length) addFiles(files)
  }

  function removeFile(index) {
    if (fileQueue.value[index]?.status === 'pending') {
      fileQueue.value.splice(index, 1)
    }
  }

  function clearQueue() {
    fileQueue.value = []
    isUploading.value = false
  }

  async function handleUploadAll() {
    if (!hasFiles.value || isUploading.value) return
    isUploading.value = true

    for (const item of fileQueue.value) {
      if (item.status !== 'pending') continue
      item.status = 'uploading'
      item.progress = 30
      try {
        await new Promise((resolve) => {
          item.progress = 60
          emit('upload', item.file, (ok) => {
            item.progress = 100
            item.status = ok ? 'done' : 'failed'
            resolve()
          })
        })
      } catch {
        item.progress = 100
        item.status = 'failed'
      }
    }

    isUploading.value = false
  }

  function formatSize(bytes) {
    if (bytes < 1024) return bytes + ' B'
    if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB'
    return (bytes / (1024 * 1024)).toFixed(2) + ' MB'
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
    <div class="upload-summary-bar">
      <div class="summary-pill">
        <strong>{{ fileQueue.length }}</strong>
        <span>Izbranih datotek</span>
      </div>
      <div class="summary-pill">
        <strong>{{ pendingCount }}</strong>
        <span>Pripravljenih za nalaganje</span>
      </div>
      <div class="summary-pill" :class="{ success: doneCount }">
        <strong>{{ doneCount }}</strong>
        <span>Uspešno naloženih</span>
      </div>
      <div class="summary-pill" :class="{ danger: failedCount }">
        <strong>{{ failedCount }}</strong>
        <span>Napak</span>
      </div>
    </div>

    <div class="upload-prompt">
      <div class="upload-icon-wrap">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
          <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4" />
          <polyline points="17 8 12 3 7 8" />
          <line x1="12" y1="3" x2="12" y2="15" />
        </svg>
      </div>
      <p class="upload-title">Povleci PDF datoteke sem</p>
      <p class="upload-hint">ali</p>
      <label for="document-upload" class="upload-browse">
        <svg
          viewBox="0 0 24 24"
          fill="none"
          stroke="currentColor"
          stroke-width="2"
          class="browse-icon"
        >
          <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z" />
          <polyline points="14 2 14 8 20 8" />
        </svg>
        Izberi datoteke
      </label>
      <input
        id="document-upload"
        type="file"
        accept="application/pdf,.pdf"
        multiple
        class="sr-only"
        @change="onFileChange"
      />
      <p class="upload-formats">Podprti formati: PDF (do 15 MB na datoteko) · Več datotek hkrati</p>
    </div>

    <div class="upload-guidance">
      <div class="guidance-item">
        <span class="guidance-title">Več dokumentov</span>
        <span class="guidance-text">Dodaj več PDF datotek hkrati in nato upravljaj nadaljnjo obdelavo iz pregleda dokumentov.</span>
      </div>
      <div class="guidance-item">
        <span class="guidance-title">Jasen status</span>
        <span class="guidance-text">Vsaka datoteka v čakalni vrsti prikazuje stanje nalaganja in jasno označi morebitno napako.</span>
      </div>
      <div class="guidance-item">
        <span class="guidance-title">Naslednji korak</span>
        <span class="guidance-text">Po nalaganju odpri predogled dokumenta, sproži povzetek in nato zastavi vprašanja nad vsebino.</span>
      </div>
    </div>

    <Transition name="fade">
      <div v-if="hasFiles" class="file-queue">
        <div class="queue-header">
          <span class="queue-title">{{ fileQueue.length }} datotek v vrsti</span>
          <button v-if="!isUploading" class="queue-clear" @click="clearQueue">Počisti</button>
        </div>
        <TransitionGroup name="list" tag="div" class="queue-list">
          <div
            v-for="(item, idx) in fileQueue"
            :key="item.file.name + item.file.size"
            class="queue-item"
            :class="'qs-' + item.status"
          >
            <div class="qi-icon" :class="'qi-' + item.status">
              <svg
                v-if="item.status === 'done'"
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                stroke-width="2.5"
              >
                <polyline points="20 6 9 17 4 12" />
              </svg>
              <svg
                v-else-if="item.status === 'failed'"
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                stroke-width="2.5"
              >
                <line x1="18" y1="6" x2="6" y2="18" />
                <line x1="6" y1="6" x2="18" y2="18" />
              </svg>
              <svg
                v-else-if="item.status === 'uploading'"
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                stroke-width="2"
                class="spin"
              >
                <path d="M21 12a9 9 0 1 1-6.219-8.56" />
              </svg>
              <svg v-else viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
                <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z" />
                <polyline points="14 2 14 8 20 8" />
              </svg>
            </div>
            <div class="qi-info">
              <span class="qi-name">{{ item.file.name }}</span>
              <span class="qi-size">{{ formatSize(item.file.size) }}</span>
            </div>
            <div class="qi-bar-wrap" v-if="item.status === 'uploading'">
              <div class="qi-bar" :style="{ width: item.progress + '%' }"></div>
            </div>
            <span v-if="item.status === 'done'" class="qi-label qi-done-label">Naloženo</span>
            <span v-if="item.status === 'failed'" class="qi-label qi-fail-label">Napaka</span>
            <button
              v-if="item.status === 'pending'"
              class="qi-remove"
              @click="removeFile(idx)"
              title="Odstrani"
            >
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <line x1="18" y1="6" x2="6" y2="18" />
                <line x1="6" y1="6" x2="18" y2="18" />
              </svg>
            </button>
          </div>
        </TransitionGroup>
        <div class="queue-actions">
          <button
            class="btn-upload-all"
            :disabled="isUploading || !pendingCount"
            @click="handleUploadAll"
          >
            <svg
              v-if="isUploading"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              stroke-width="2"
              class="btn-icon spin"
            >
              <path d="M21 12a9 9 0 1 1-6.219-8.56" />
            </svg>
            <svg
              v-else
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              stroke-width="2"
              class="btn-icon"
            >
              <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4" />
              <polyline points="17 8 12 3 7 8" />
              <line x1="12" y1="3" x2="12" y2="15" />
            </svg>
            {{
              isUploading ? 'Nalagam...' : allDone ? 'Zaključeno' : `Naloži ${pendingCount} datotek`
            }}
          </button>
        </div>
      </div>
    </Transition>
  </div>
</template>

<style scoped>
  .upload-zone {
    border: 1px solid rgba(255, 255, 255, 0.62);
    border-radius: 28px;
    padding: 1.35rem;
    text-align: left;
    transition: all 0.3s ease;
    background: rgba(255, 255, 255, 0.72);
    box-shadow: var(--shadow-md);
    backdrop-filter: blur(12px);
    position: relative;
  }
  .upload-zone.drag-over {
    border-color: var(--primary);
    background: rgba(99, 102, 241, 0.06);
    box-shadow: inset 0 0 0 2px rgba(99, 102, 241, 0.08);
  }

  .upload-summary-bar {
    display: grid;
    grid-template-columns: repeat(4, minmax(0, 1fr));
    gap: 0.75rem;
    margin-bottom: 1rem;
  }

  .summary-pill {
    padding: 0.9rem 1rem;
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 18px;
  }

  .summary-pill strong {
    display: block;
    margin-bottom: 0.15rem;
    font-size: 1.05rem;
    color: var(--primary);
  }

  .summary-pill span {
    font-size: 0.74rem;
    color: var(--text-muted);
    line-height: 1.45;
  }

  .summary-pill.success strong {
    color: #059669;
  }

  .summary-pill.danger strong {
    color: #dc2626;
  }

  .upload-prompt {
    padding: 1.4rem 1.25rem;
    background: linear-gradient(180deg, rgba(99, 102, 241, 0.06), rgba(99, 102, 241, 0.01));
    border: 1px solid rgba(99, 102, 241, 0.09);
    border-radius: 24px;
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
    box-shadow: 0 2px 8px rgba(99, 102, 241, 0.25);
    margin-top: 0.25rem;
  }
  .upload-browse:hover {
    box-shadow: 0 4px 14px rgba(99, 102, 241, 0.35);
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

  .upload-guidance {
    display: grid;
    grid-template-columns: repeat(3, minmax(0, 1fr));
    gap: 0.75rem;
    margin-top: 1rem;
  }

  .guidance-item {
    padding: 0.9rem 1rem;
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 18px;
  }

  .guidance-title {
    display: block;
    margin-bottom: 0.3rem;
    font-size: 0.78rem;
    font-weight: 700;
    color: var(--text);
  }

  .guidance-text {
    display: block;
    font-size: 0.74rem;
    line-height: 1.55;
    color: var(--text-muted);
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

  /* ── File Queue ── */
  .file-queue {
    margin-top: 1.25rem;
    border-top: 1px solid var(--border);
    padding-top: 1rem;
    text-align: left;
  }
  .queue-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-bottom: 0.6rem;
  }
  .queue-title {
    font-size: 0.82rem;
    font-weight: 600;
    color: var(--text);
  }
  .queue-clear {
    border: none;
    background: transparent;
    color: var(--text-light);
    font-size: 0.75rem;
    font-weight: 600;
    cursor: pointer;
    padding: 0.2rem 0.5rem;
    border-radius: var(--radius-sm);
    transition: all 0.15s;
  }
  .queue-clear:hover {
    background: rgba(239, 68, 68, 0.08);
    color: #ef4444;
  }
  .queue-list {
    display: flex;
    flex-direction: column;
    gap: 0.35rem;
  }
  .queue-item {
    display: flex;
    align-items: center;
    gap: 0.6rem;
    padding: 0.5rem 0.7rem;
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: var(--radius-sm);
    transition: all 0.2s;
  }
  .queue-item.qs-done {
    border-color: rgba(16, 185, 129, 0.25);
    background: rgba(16, 185, 129, 0.04);
  }
  .queue-item.qs-failed {
    border-color: rgba(239, 68, 68, 0.25);
    background: rgba(239, 68, 68, 0.04);
  }
  .queue-item.qs-uploading {
    border-color: rgba(99, 102, 241, 0.25);
  }
  .qi-icon {
    width: 28px;
    height: 28px;
    border-radius: 6px;
    display: flex;
    align-items: center;
    justify-content: center;
    flex-shrink: 0;
    background: var(--primary-light);
    color: var(--primary);
  }
  .qi-icon svg {
    width: 14px;
    height: 14px;
  }
  .qi-icon.qi-done {
    background: rgba(16, 185, 129, 0.12);
    color: #10b981;
  }
  .qi-icon.qi-failed {
    background: rgba(239, 68, 68, 0.12);
    color: #ef4444;
  }
  .qi-icon.qi-uploading {
    background: rgba(99, 102, 241, 0.12);
    color: var(--primary);
  }
  .qi-info {
    flex: 1;
    min-width: 0;
  }
  .qi-name {
    display: block;
    font-size: 0.82rem;
    font-weight: 600;
    color: var(--text);
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
  }
  .qi-size {
    font-size: 0.7rem;
    color: var(--text-light);
  }
  .qi-bar-wrap {
    width: 80px;
    height: 4px;
    background: var(--border);
    border-radius: 2px;
    overflow: hidden;
    flex-shrink: 0;
  }
  .qi-bar {
    height: 100%;
    background: var(--primary);
    border-radius: 2px;
    transition: width 0.4s ease;
  }
  .qi-label {
    font-size: 0.7rem;
    font-weight: 700;
    flex-shrink: 0;
  }
  .qi-done-label {
    color: #10b981;
  }
  .qi-fail-label {
    color: #ef4444;
  }
  .qi-remove {
    width: 22px;
    height: 22px;
    border: none;
    background: transparent;
    color: var(--text-light);
    cursor: pointer;
    display: flex;
    align-items: center;
    justify-content: center;
    border-radius: 4px;
    transition: all 0.15s;
    flex-shrink: 0;
  }
  .qi-remove svg {
    width: 13px;
    height: 13px;
  }
  .qi-remove:hover {
    background: rgba(239, 68, 68, 0.08);
    color: #ef4444;
  }
  .queue-actions {
    margin-top: 0.75rem;
    display: flex;
    justify-content: flex-end;
  }
  .btn-upload-all {
    display: inline-flex;
    align-items: center;
    gap: 0.4rem;
    padding: 0.6rem 1.2rem;
    border: 0;
    border-radius: var(--radius-sm);
    background: linear-gradient(135deg, var(--primary), #818cf8);
    color: white;
    font-size: 0.85rem;
    font-weight: 600;
    cursor: pointer;
    transition: all 0.2s ease;
    box-shadow: 0 2px 8px rgba(99, 102, 241, 0.25);
  }
  .btn-upload-all:hover:not(:disabled) {
    box-shadow: 0 4px 14px rgba(99, 102, 241, 0.35);
  }
  .btn-upload-all:disabled {
    opacity: 0.6;
    cursor: not-allowed;
  }
  .btn-icon {
    width: 15px;
    height: 15px;
  }

  @keyframes spin {
    to {
      transform: rotate(360deg);
    }
  }
  .spin {
    animation: spin 1s linear infinite;
  }

  .fade-enter-active,
  .fade-leave-active {
    transition: opacity 0.25s ease;
  }
  .fade-enter-from,
  .fade-leave-to {
    opacity: 0;
  }
  .list-enter-active,
  .list-leave-active {
    transition: all 0.25s ease;
  }
  .list-enter-from,
  .list-leave-to {
    opacity: 0;
    transform: translateX(-8px);
  }

  @media (max-width: 520px) {
    .upload-zone {
      padding: 1.25rem;
    }
    .upload-summary-bar,
    .upload-guidance {
      grid-template-columns: 1fr;
    }
    .qi-bar-wrap {
      width: 50px;
    }
  }
</style>
