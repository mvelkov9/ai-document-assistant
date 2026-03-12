<script setup>
  import { ref, onMounted, onUnmounted, watch, nextTick } from 'vue'
  import * as pdfjsLib from 'pdfjs-dist'

  pdfjsLib.GlobalWorkerOptions.workerSrc = new URL(
    'pdfjs-dist/build/pdf.worker.mjs',
    import.meta.url,
  ).toString()

  const props = defineProps({
    documentId: { type: String, required: true },
    token: { type: String, required: true },
  })

  const emit = defineEmits(['close'])

  const canvasRef = ref(null)
  const containerRef = ref(null)
  const loading = ref(true)
  const error = ref('')
  const currentPage = ref(1)
  const totalPages = ref(0)
  const scale = ref(1.2)
  const pdfDoc = ref(null)

  async function loadPdf() {
    loading.value = true
    error.value = ''
    try {
      const apiBase = import.meta.env.VITE_API_BASE_URL || '/api/v1'
      const response = await fetch(`${apiBase}/documents/${props.documentId}/download`, {
        headers: { Authorization: `Bearer ${props.token}` },
      })
      if (!response.ok) throw new Error('Failed to download PDF')
      const arrayBuffer = await response.arrayBuffer()
      const doc = await pdfjsLib.getDocument({ data: arrayBuffer }).promise
      pdfDoc.value = doc
      totalPages.value = doc.numPages
      currentPage.value = 1
      await renderPage(1)
    } catch (e) {
      error.value = e.message || 'Could not load PDF'
    } finally {
      loading.value = false
    }
  }

  async function renderPage(pageNum) {
    if (!pdfDoc.value || !canvasRef.value) return
    const page = await pdfDoc.value.getPage(pageNum)
    const viewport = page.getViewport({ scale: scale.value })
    const canvas = canvasRef.value
    const ctx = canvas.getContext('2d')
    canvas.height = viewport.height
    canvas.width = viewport.width
    await page.render({ canvasContext: ctx, viewport }).promise
  }

  function prevPage() {
    if (currentPage.value > 1) {
      currentPage.value--
      renderPage(currentPage.value)
    }
  }

  function nextPage() {
    if (currentPage.value < totalPages.value) {
      currentPage.value++
      renderPage(currentPage.value)
    }
  }

  function zoomIn() {
    scale.value = Math.min(scale.value + 0.2, 3.0)
    renderPage(currentPage.value)
  }

  function zoomOut() {
    scale.value = Math.max(scale.value - 0.2, 0.4)
    renderPage(currentPage.value)
  }

  function handleKeydown(e) {
    if (e.key === 'Escape') emit('close')
    if (e.key === 'ArrowLeft') prevPage()
    if (e.key === 'ArrowRight') nextPage()
  }

  onMounted(() => {
    loadPdf()
    window.addEventListener('keydown', handleKeydown)
  })

  onUnmounted(() => {
    window.removeEventListener('keydown', handleKeydown)
    if (pdfDoc.value) pdfDoc.value.destroy()
  })
</script>

<template>
  <div class="pdf-viewer-overlay" @click.self="emit('close')">
    <div class="pdf-viewer" ref="containerRef">
      <!-- Toolbar -->
      <div class="pdf-toolbar">
        <div class="pdf-toolbar-left">
          <button class="pdf-btn" @click="prevPage" :disabled="currentPage <= 1" title="Prejšnja stran">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="15 18 9 12 15 6"/></svg>
          </button>
          <span class="pdf-page-info">{{ currentPage }} / {{ totalPages }}</span>
          <button class="pdf-btn" @click="nextPage" :disabled="currentPage >= totalPages" title="Naslednja stran">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="9 18 15 12 9 6"/></svg>
          </button>
        </div>
        <div class="pdf-toolbar-center">
          <button class="pdf-btn" @click="zoomOut" title="Pomanjšaj">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/><line x1="8" y1="11" x2="14" y2="11"/></svg>
          </button>
          <span class="pdf-zoom-info">{{ Math.round(scale * 100) }}%</span>
          <button class="pdf-btn" @click="zoomIn" title="Povečaj">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/><line x1="11" y1="8" x2="11" y2="14"/><line x1="8" y1="11" x2="14" y2="11"/></svg>
          </button>
        </div>
        <div class="pdf-toolbar-right">
          <button class="pdf-btn pdf-btn-close" @click="emit('close')" title="Zapri (Esc)">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/></svg>
          </button>
        </div>
      </div>

      <!-- Content -->
      <div class="pdf-content">
        <div v-if="loading" class="pdf-loading">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" class="spin-icon">
            <path d="M21 12a9 9 0 1 1-6.219-8.56"/>
          </svg>
          <span>Nalagam PDF...</span>
        </div>
        <div v-else-if="error" class="pdf-error">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" class="err-icon">
            <circle cx="12" cy="12" r="10"/><line x1="15" y1="9" x2="9" y2="15"/><line x1="9" y1="9" x2="15" y2="15"/>
          </svg>
          <span>{{ error }}</span>
        </div>
        <div v-else class="pdf-canvas-wrap">
          <canvas ref="canvasRef"></canvas>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.pdf-viewer-overlay {
  position: fixed;
  inset: 0;
  z-index: 100;
  background: rgba(0, 0, 0, 0.7);
  backdrop-filter: blur(4px);
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 1rem;
}

.pdf-viewer {
  width: 100%;
  max-width: 900px;
  max-height: 92vh;
  background: var(--surface);
  border-radius: var(--radius-lg);
  display: flex;
  flex-direction: column;
  overflow: hidden;
  box-shadow: 0 24px 48px rgba(0,0,0,0.3);
  border: 1px solid var(--border);
}

.pdf-toolbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0.6rem 1rem;
  background: var(--surface-alt);
  border-bottom: 1px solid var(--border);
  flex-shrink: 0;
}

.pdf-toolbar-left,
.pdf-toolbar-center,
.pdf-toolbar-right {
  display: flex;
  align-items: center;
  gap: 0.4rem;
}

.pdf-btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 34px;
  height: 34px;
  border: 1px solid var(--border);
  border-radius: var(--radius-sm);
  background: var(--surface);
  color: var(--text);
  cursor: pointer;
  transition: all 0.15s;
}
.pdf-btn svg { width: 16px; height: 16px; }
.pdf-btn:hover:not(:disabled) { background: var(--primary-light); border-color: var(--primary); color: var(--primary); }
.pdf-btn:disabled { opacity: 0.35; cursor: default; }
.pdf-btn-close:hover { background: var(--danger-light); border-color: var(--danger); color: var(--danger); }

.pdf-page-info, .pdf-zoom-info {
  font-size: 0.78rem;
  font-weight: 600;
  color: var(--text-muted);
  min-width: 60px;
  text-align: center;
}

.pdf-content {
  flex: 1;
  overflow: auto;
  display: flex;
  align-items: flex-start;
  justify-content: center;
  padding: 1rem;
  background: var(--bg);
}

.pdf-canvas-wrap {
  display: flex;
  justify-content: center;
}

.pdf-canvas-wrap canvas {
  box-shadow: 0 4px 20px rgba(0,0,0,0.15);
  border-radius: 4px;
  max-width: 100%;
  height: auto;
}

.pdf-loading, .pdf-error {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.75rem;
  padding: 3rem 1.5rem;
  color: var(--text-muted);
  font-size: 0.9rem;
}
.spin-icon { width: 28px; height: 28px; animation: viewer-spin 1s linear infinite; }
.err-icon { width: 28px; height: 28px; color: var(--danger); }
@keyframes viewer-spin { to { transform: rotate(360deg); } }

@media (max-width: 640px) {
  .pdf-viewer-overlay { padding: 0; }
  .pdf-viewer { max-width: 100%; max-height: 100vh; border-radius: 0; }
  .pdf-toolbar { padding: 0.4rem 0.5rem; }
  .pdf-zoom-info { display: none; }
}
</style>
