<script setup>
  import { computed, nextTick, onMounted, onUnmounted, ref, shallowRef } from 'vue'
  import * as pdfjsLib from 'pdfjs-dist'
  import pdfjsWorker from 'pdfjs-dist/build/pdf.worker.min.mjs?url'

  // Use the bundled worker URL; Vite emits it as a static asset
  pdfjsLib.GlobalWorkerOptions.workerSrc = pdfjsWorker
  // Disable the worker range-request to avoid double-fetch issues in nginx
  pdfjsLib.GlobalWorkerOptions.workerPort = null

  const props = defineProps({
    documentId: { type: String, required: true },
    token: { type: String, required: true },
  })

  const emit = defineEmits(['close'])

  const canvasRef = ref(null)
  const containerRef = ref(null)
  const loading = ref(true)
  const rendering = ref(false)
  const error = ref('')
  const currentPage = ref(1)
  const pageInput = ref('1')
  const totalPages = ref(0)
  const zoom = ref(1)
  const fitWidth = ref(true)
  const baseScale = ref(1)
  const pdfDoc = shallowRef(null)
  const renderTask = shallowRef(null)
  let resizeObserver = null

  const scale = computed(() => Number((baseScale.value * zoom.value).toFixed(3)))
  const zoomPercent = computed(() => Math.round(scale.value * 100))

  function syncPageInput() {
    pageInput.value = String(currentPage.value)
  }

  function clampPage(pageNum) {
    return Math.min(Math.max(pageNum, 1), totalPages.value || 1)
  }

  async function getBaseScale(page) {
    if (!fitWidth.value || !containerRef.value) return 1
    const unscaledViewport = page.getViewport({ scale: 1 })
    const availableWidth = Math.max(containerRef.value.clientWidth - 48, 280)
    return availableWidth / unscaledViewport.width
  }

  async function loadPdf() {
    loading.value = true
    error.value = ''
    try {
      const apiBase = import.meta.env.VITE_API_BASE_URL || '/api/v1'
      const response = await fetch(`${apiBase}/documents/${props.documentId}/download`, {
        headers: { Authorization: `Bearer ${props.token}` },
      })
      if (!response.ok) throw new Error('Prenos datoteke PDF ni uspel')
      const arrayBuffer = await response.arrayBuffer()
      const data = new Uint8Array(arrayBuffer)
      const doc = await pdfjsLib.getDocument({ data }).promise
      pdfDoc.value = doc
      totalPages.value = doc.numPages
      currentPage.value = 1
      syncPageInput()
      await nextTick()
      await renderPage(1)
    } catch (e) {
      error.value = e.message || 'Datoteke PDF ni bilo mogoče naložiti'
    } finally {
      loading.value = false
    }
  }

  async function renderPage(pageNum) {
    if (!pdfDoc.value || !canvasRef.value) return
    rendering.value = true
    error.value = ''

    if (renderTask.value) {
      renderTask.value.cancel()
      renderTask.value = null
    }

    try {
      const safePage = clampPage(pageNum)
      currentPage.value = safePage
      syncPageInput()

      const page = await pdfDoc.value.getPage(safePage)
      baseScale.value = await getBaseScale(page)

      const viewport = page.getViewport({ scale: scale.value })
      const outputScale = window.devicePixelRatio || 1
      const canvas = canvasRef.value
      const ctx = canvas.getContext('2d')

      canvas.width = Math.floor(viewport.width * outputScale)
      canvas.height = Math.floor(viewport.height * outputScale)
      canvas.style.width = `${viewport.width}px`
      canvas.style.height = `${viewport.height}px`
      ctx.setTransform(outputScale, 0, 0, outputScale, 0, 0)

      renderTask.value = page.render({ canvasContext: ctx, viewport })
      await renderTask.value.promise
      renderTask.value = null
    } catch (e) {
      if (e?.name !== 'RenderingCancelledException') {
        error.value = e.message || 'Strani PDF ni bilo mogoče izrisati'
      }
    } finally {
      rendering.value = false
    }
  }

  function prevPage() {
    if (currentPage.value > 1) {
      renderPage(currentPage.value - 1)
    }
  }

  function nextPage() {
    if (currentPage.value < totalPages.value) {
      renderPage(currentPage.value + 1)
    }
  }

  function zoomIn() {
    fitWidth.value = false
    zoom.value = Math.min(zoom.value + 0.15, 3)
    renderPage(currentPage.value)
  }

  function zoomOut() {
    fitWidth.value = false
    zoom.value = Math.max(zoom.value - 0.15, 0.55)
    renderPage(currentPage.value)
  }

  function resetFitWidth() {
    fitWidth.value = true
    zoom.value = 1
    renderPage(currentPage.value)
  }

  function jumpToPage() {
    const numericPage = Number.parseInt(pageInput.value, 10)
    if (Number.isNaN(numericPage)) {
      syncPageInput()
      return
    }
    renderPage(numericPage)
  }

  function handleKeydown(e) {
    if (e.key === 'Escape') emit('close')
    if (e.key === 'ArrowLeft') prevPage()
    if (e.key === 'ArrowRight') nextPage()
  }

  onMounted(() => {
    loadPdf()
    window.addEventListener('keydown', handleKeydown)
    resizeObserver = new ResizeObserver(() => {
      if (pdfDoc.value && fitWidth.value && !loading.value) {
        renderPage(currentPage.value)
      }
    })
    if (containerRef.value) resizeObserver.observe(containerRef.value)
  })

  onUnmounted(() => {
    window.removeEventListener('keydown', handleKeydown)
    if (resizeObserver) resizeObserver.disconnect()
    if (renderTask.value) renderTask.value.cancel()
    if (pdfDoc.value) pdfDoc.value.destroy()
  })
</script>

<template>
  <div class="pdf-viewer-overlay" @click.self="emit('close')">
    <div class="pdf-viewer" ref="containerRef">
      <div class="pdf-toolbar">
        <div class="pdf-toolbar-left">
          <div class="pdf-badge">Predogled PDF</div>
          <button
            class="pdf-btn"
            @click="prevPage"
            :disabled="currentPage <= 1"
            title="Prejšnja stran"
          >
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <polyline points="15 18 9 12 15 6" />
            </svg>
          </button>
          <label class="pdf-page-jump">
            <input v-model="pageInput" type="number" min="1" :max="totalPages || 1" @change="jumpToPage" />
            <span>/ {{ totalPages }}</span>
          </label>
          <button
            class="pdf-btn"
            @click="nextPage"
            :disabled="currentPage >= totalPages"
            title="Naslednja stran"
          >
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <polyline points="9 18 15 12 9 6" />
            </svg>
          </button>
        </div>
        <div class="pdf-toolbar-center">
          <button class="pdf-btn" :class="{ active: fitWidth }" @click="resetFitWidth" title="Prilagodi širini">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M3 7V5a2 2 0 0 1 2-2h2" />
              <path d="M21 7V5a2 2 0 0 0-2-2h-2" />
              <path d="M3 17v2a2 2 0 0 0 2 2h2" />
              <path d="M21 17v2a2 2 0 0 1-2 2h-2" />
              <line x1="8" y1="12" x2="16" y2="12" />
            </svg>
          </button>
          <button class="pdf-btn" @click="zoomOut" title="Pomanjšaj">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <circle cx="11" cy="11" r="8" />
              <line x1="21" y1="21" x2="16.65" y2="16.65" />
              <line x1="8" y1="11" x2="14" y2="11" />
            </svg>
          </button>
          <span class="pdf-zoom-info">{{ zoomPercent }}%</span>
          <button class="pdf-btn" @click="zoomIn" title="Povečaj">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <circle cx="11" cy="11" r="8" />
              <line x1="21" y1="21" x2="16.65" y2="16.65" />
              <line x1="11" y1="8" x2="11" y2="14" />
              <line x1="8" y1="11" x2="14" y2="11" />
            </svg>
          </button>
        </div>
        <div class="pdf-toolbar-right">
          <button class="pdf-btn pdf-btn-close" @click="emit('close')" title="Zapri (Esc)">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <line x1="18" y1="6" x2="6" y2="18" />
              <line x1="6" y1="6" x2="18" y2="18" />
            </svg>
          </button>
        </div>
      </div>

      <div class="pdf-content">
        <div v-if="loading" class="pdf-loading">
          <svg
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            stroke-width="2"
            class="spin-icon"
          >
            <path d="M21 12a9 9 0 1 1-6.219-8.56" />
          </svg>
          <span>Nalagam PDF...</span>
        </div>
        <div v-else-if="error" class="pdf-error">
          <svg
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            stroke-width="2"
            class="err-icon"
          >
            <circle cx="12" cy="12" r="10" />
            <line x1="15" y1="9" x2="9" y2="15" />
            <line x1="9" y1="9" x2="15" y2="15" />
          </svg>
          <span>{{ error }}</span>
        </div>
        <div v-else class="pdf-canvas-wrap">
          <div class="pdf-surface-header">
            <div>
              <strong>Stran {{ currentPage }}</strong>
              <span>{{ fitWidth ? 'Prilagojeno širini' : 'Ročna povečava' }}</span>
            </div>
            <span v-if="rendering" class="pdf-rendering">Pripravljam prikaz...</span>
          </div>
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
    background:
      radial-gradient(circle at top, rgba(99, 102, 241, 0.18), transparent 36%),
      rgba(6, 10, 18, 0.78);
    backdrop-filter: blur(14px);
    display: flex;
    align-items: center;
    justify-content: center;
    padding: 1.25rem;
  }

  .pdf-viewer {
    width: 100%;
    max-width: min(1320px, 100%);
    height: min(94vh, 980px);
    background: color-mix(in srgb, var(--surface) 88%, #ffffff 12%);
    border-radius: calc(var(--radius-xl) + 8px);
    display: flex;
    flex-direction: column;
    overflow: hidden;
    box-shadow: 0 32px 80px rgba(2, 8, 23, 0.28);
    border: 1px solid color-mix(in srgb, var(--border) 68%, white 32%);
  }

  .pdf-toolbar {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 0.85rem 1rem;
    background: linear-gradient(180deg, color-mix(in srgb, var(--surface-alt) 82%, white 18%), var(--surface));
    border-bottom: 1px solid var(--border);
    flex-shrink: 0;
    gap: 1rem;
    flex-wrap: wrap;
  }

  .pdf-toolbar-left,
  .pdf-toolbar-center,
  .pdf-toolbar-right {
    display: flex;
    align-items: center;
    gap: 0.5rem;
  }

  .pdf-badge {
    padding: 0.35rem 0.7rem;
    border-radius: 999px;
    background: var(--primary-light);
    color: var(--primary);
    font-size: 0.75rem;
    font-weight: 700;
    letter-spacing: 0.06em;
    text-transform: uppercase;
  }

  .pdf-btn {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    width: 38px;
    height: 38px;
    border: 1px solid var(--border);
    border-radius: 12px;
    background: color-mix(in srgb, var(--surface) 88%, white 12%);
    color: var(--text);
    cursor: pointer;
    transition: all 0.18s ease;
  }
  .pdf-btn svg {
    width: 16px;
    height: 16px;
  }
  .pdf-btn:hover:not(:disabled) {
    background: color-mix(in srgb, var(--primary-light) 74%, white 26%);
    border-color: color-mix(in srgb, var(--primary) 52%, white 48%);
    color: var(--primary);
  }
  .pdf-btn:disabled {
    opacity: 0.35;
    cursor: default;
  }
  .pdf-btn.active {
    background: color-mix(in srgb, var(--primary) 16%, white 84%);
    border-color: color-mix(in srgb, var(--primary) 54%, white 46%);
    color: var(--primary);
  }
  .pdf-btn-close:hover {
    background: var(--danger-light);
    border-color: var(--danger);
    color: var(--danger);
  }

  .pdf-zoom-info {
    font-size: 0.82rem;
    font-weight: 700;
    color: var(--text-muted);
    min-width: 68px;
    text-align: center;
  }

  .pdf-page-jump {
    display: inline-flex;
    align-items: center;
    gap: 0.45rem;
    padding: 0.28rem 0.55rem;
    border: 1px solid var(--border);
    border-radius: 999px;
    background: color-mix(in srgb, var(--surface) 88%, white 12%);
    font-size: 0.8rem;
    font-weight: 700;
    color: var(--text-muted);
  }

  .pdf-page-jump input {
    width: 3.4rem;
    border: none;
    background: transparent;
    color: var(--text);
    text-align: right;
    font-weight: 700;
  }

  .pdf-page-jump input:focus {
    outline: none;
  }

  .pdf-content {
    flex: 1;
    overflow: auto;
    display: flex;
    align-items: stretch;
    justify-content: center;
    padding: 1.25rem;
    background:
      linear-gradient(180deg, color-mix(in srgb, var(--surface-alt) 76%, white 24%), var(--bg)),
      repeating-linear-gradient(
        45deg,
        transparent,
        transparent 16px,
        rgba(15, 23, 42, 0.015) 16px,
        rgba(15, 23, 42, 0.015) 32px
      );
  }

  .pdf-canvas-wrap {
    width: min(100%, 1120px);
    margin: 0 auto;
    padding: 1rem;
    border-radius: 28px;
    background: rgba(255, 255, 255, 0.6);
    border: 1px solid rgba(255, 255, 255, 0.55);
    box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.6);
  }

  .pdf-surface-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 1rem;
    margin-bottom: 1rem;
    color: var(--text-muted);
    font-size: 0.82rem;
  }

  .pdf-surface-header strong {
    display: block;
    font-size: 1rem;
    color: var(--text);
    margin-bottom: 0.15rem;
  }

  .pdf-rendering {
    padding: 0.35rem 0.65rem;
    border-radius: 999px;
    background: rgba(59, 130, 246, 0.12);
    color: #1d4ed8;
    font-weight: 700;
  }

  .pdf-canvas-wrap canvas {
    display: block;
    margin: 0 auto;
    box-shadow: 0 22px 46px rgba(15, 23, 42, 0.16);
    border-radius: 14px;
    max-width: none;
    height: auto;
    background: white;
  }

  .pdf-loading,
  .pdf-error {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 0.75rem;
    padding: 4rem 1.5rem;
    color: var(--text-muted);
    font-size: 0.9rem;
  }
  .spin-icon {
    width: 28px;
    height: 28px;
    animation: viewer-spin 1s linear infinite;
  }
  .err-icon {
    width: 28px;
    height: 28px;
    color: var(--danger);
  }
  @keyframes viewer-spin {
    to {
      transform: rotate(360deg);
    }
  }

  @media (max-width: 640px) {
    .pdf-viewer-overlay {
      padding: 0;
    }
    .pdf-viewer {
      max-width: 100%;
      height: 100vh;
      border-radius: 0;
    }
    .pdf-toolbar {
      padding: 0.6rem;
    }
    .pdf-zoom-info {
      display: none;
    }
    .pdf-content {
      padding: 0.75rem;
    }
    .pdf-canvas-wrap {
      padding: 0.75rem;
      border-radius: 18px;
    }
    .pdf-page-jump input {
      width: 2.6rem;
    }
  }
</style>
