<script setup>
  import { ref } from 'vue'
  import PdfViewer from './PdfViewer.vue'
  import ChatQA from './ChatQA.vue'

  const props = defineProps({
    document: { type: Object, required: true },
    summaryBusy: { type: Boolean, default: false },
    questionBusy: { type: Boolean, default: false },
    answers: { type: Array, default: () => [] },
    collapsed: { type: Boolean, default: false },
    token: { type: String, default: '' },
  })

  const emit = defineEmits(['summarize', 'ask', 'delete', 'delete-answer', 'clear-answers', 'download'])
  const confirmingDelete = ref(false)
  const isCollapsed = ref(props.collapsed)
  const copied = ref(false)
  const showPdfViewer = ref(false)

  function handleDelete() {
    emit('delete', props.document.id)
    confirmingDelete.value = false
  }

  function copyToClipboard(text) {
    navigator.clipboard.writeText(text).then(() => {
      copied.value = true
      setTimeout(() => (copied.value = false), 2000)
    })
  }

  function formatBytes(bytes) {
    if (bytes < 1024) return bytes + ' B'
    if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB'
    return (bytes / (1024 * 1024)).toFixed(1) + ' MB'
  }

  function formatDate(iso) {
    if (!iso) return ''
    const d = new Date(iso)
    return d.toLocaleDateString('sl-SI', { day: 'numeric', month: 'short', year: 'numeric' })
  }
</script>

<template>
  <article
    class="doc-card"
    :class="{ 'is-collapsed': isCollapsed, 'is-processing': summaryBusy || questionBusy }"
  >
    <!-- ── Header ── -->
    <div class="doc-header" @click="isCollapsed = !isCollapsed" style="cursor: pointer">
      <div class="doc-icon-wrap">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
          <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z" />
          <polyline points="14 2 14 8 20 8" />
        </svg>
      </div>
      <div class="doc-info">
        <h4 class="doc-name">{{ document.original_filename }}</h4>
        <div class="doc-meta">
          <span class="meta-badge">{{ formatBytes(document.size_bytes) }}</span>
          <span class="meta-badge" :class="'status-' + document.processing_status">
            <span class="status-dot"></span>
            {{ document.processing_status }}
          </span>
          <span v-if="document.created_at" class="meta-badge meta-date">
            <svg
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              stroke-width="2"
              class="meta-icon"
            >
              <rect x="3" y="4" width="18" height="18" rx="2" ry="2" />
              <line x1="16" y1="2" x2="16" y2="6" />
              <line x1="8" y1="2" x2="8" y2="6" />
              <line x1="3" y1="10" x2="21" y2="10" />
            </svg>
            {{ formatDate(document.created_at) }}
          </span>
          <span v-if="answers.length" class="meta-badge meta-qa-count">
            {{ answers.length }} V&amp;O
          </span>
        </div>
      </div>
      <div class="doc-actions" @click.stop>
        <button
          class="btn-collapse"
          @click="isCollapsed = !isCollapsed"
          :title="isCollapsed ? 'Razširi' : 'Skrči'"
        >
          <svg
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            stroke-width="2"
            class="btn-icon"
            :class="{ rotated: !isCollapsed }"
          >
            <polyline points="6 9 12 15 18 9" />
          </svg>
        </button>
        <button
          class="btn-action btn-view"
          @click="showPdfViewer = true"
          title="Preberi PDF"
        >
          <svg
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            stroke-width="2"
            class="btn-icon"
          >
            <path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z" />
            <circle cx="12" cy="12" r="3" />
          </svg>
          Preberi
        </button>
        <button
          class="btn-action btn-download"
          @click="emit('download', document.id, document.original_filename)"
          title="Prenesi PDF"
        >
          <svg
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            stroke-width="2"
            class="btn-icon"
          >
            <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4" />
            <polyline points="7 10 12 15 17 10" />
            <line x1="12" y1="15" x2="12" y2="3" />
          </svg>
          Prenesi
        </button>
        <button
          class="btn-action btn-summarize"
          :disabled="summaryBusy"
          @click="emit('summarize', document.id)"
        >
          <svg
            v-if="summaryBusy"
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
            <circle cx="12" cy="12" r="3" />
            <path
              d="M12 1v2M12 21v2M4.22 4.22l1.42 1.42M18.36 18.36l1.42 1.42M1 12h2M21 12h2M4.22 19.78l1.42-1.42M18.36 5.64l1.42-1.42"
            />
          </svg>
          {{ summaryBusy ? 'Generiranje...' : 'Povzetek' }}
        </button>
        <button
          class="btn-icon-only btn-danger"
          @click="confirmingDelete = true"
          title="Izbriši dokument"
        >
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <polyline points="3 6 5 6 21 6" />
            <path
              d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"
            />
          </svg>
        </button>
      </div>
    </div>

    <!-- ── Collapsible Body ── -->
    <Transition name="collapse">
      <div v-show="!isCollapsed" class="doc-body">
        <!-- ── Delete Confirmation ── -->
        <Transition name="fade">
          <div v-if="confirmingDelete" class="confirm-overlay">
            <div class="confirm-card">
              <div class="confirm-icon-wrap">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <polyline points="3 6 5 6 21 6" />
                  <path
                    d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"
                  />
                </svg>
              </div>
              <p class="confirm-text">
                Izbrisati <strong>{{ document.original_filename }}</strong
                >?
              </p>
              <p class="confirm-sub">
                To bo trajno izbrisalo datoteko in vse povezane povzetke ter vprašanja.
              </p>
              <div class="confirm-actions">
                <button class="btn-confirm btn-cancel" @click="confirmingDelete = false">
                  Prekliči
                </button>
                <button class="btn-confirm btn-delete" @click="handleDelete">
                  <svg
                    viewBox="0 0 24 24"
                    fill="none"
                    stroke="currentColor"
                    stroke-width="2"
                    class="btn-icon-xs"
                  >
                    <polyline points="3 6 5 6 21 6" />
                    <path
                      d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"
                    />
                  </svg>
                  Izbriši
                </button>
              </div>
            </div>
          </div>
        </Transition>

        <!-- ── Summary Section ── -->
        <div class="section summary-section">
          <div class="section-label">
            <svg
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              stroke-width="2"
              class="label-icon"
            >
              <line x1="17" y1="10" x2="3" y2="10" />
              <line x1="21" y1="6" x2="3" y2="6" />
              <line x1="21" y1="14" x2="3" y2="14" />
              <line x1="17" y1="18" x2="3" y2="18" />
            </svg>
            Povzetek
          </div>
          <div v-if="!document.summary_text" class="empty-summary">
            <div class="empty-summary-graphic">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
                <circle cx="12" cy="12" r="3" />
                <path
                  d="M12 1v2M12 21v2M4.22 4.22l1.42 1.42M18.36 18.36l1.42 1.42M1 12h2M21 12h2M4.22 19.78l1.42-1.42M18.36 5.64l1.42-1.42"
                />
              </svg>
            </div>
            <span>Klikni <strong>Povzetek</strong> za generiranje AI povzetka</span>
          </div>
          <div v-else class="summary-content">
            <p class="summary-text">{{ document.summary_text }}</p>
            <button
              class="btn-copy"
              @click="copyToClipboard(document.summary_text)"
              :title="copied ? 'Skopirano!' : 'Kopiraj povzetek'"
            >
              <svg
                v-if="copied"
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                stroke-width="2"
                class="copy-icon"
              >
                <polyline points="20 6 9 17 4 12" />
              </svg>
              <svg
                v-else
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                stroke-width="2"
                class="copy-icon"
              >
                <rect x="9" y="9" width="13" height="13" rx="2" ry="2" />
                <path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1" />
              </svg>
              {{ copied ? 'Skopirano' : 'Kopiraj' }}
            </button>
          </div>
        </div>

        <!-- ── Q&A Section (Chat) ── -->
        <div class="section qa-section">
          <div class="section-label">
            <svg
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              stroke-width="2"
              class="label-icon"
            >
              <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z" />
            </svg>
            Vprašanja &amp; Odgovori
          </div>
          <ChatQA
            :answers="answers"
            :question-busy="questionBusy"
            @ask="(q) => emit('ask', document.id, q)"
            @delete-answer="(answerId) => emit('delete-answer', document.id, answerId)"
            @clear-answers="emit('clear-answers', document.id)"
          />
        </div>
      </div>
    </Transition>

    <!-- PDF Viewer (teleported to body) -->
    <Teleport to="body">
      <PdfViewer
        v-if="showPdfViewer"
        :document-id="document.id"
        :token="token"
        @close="showPdfViewer = false"
      />
    </Teleport>
  </article>
</template>

<style scoped>
  .doc-card {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: var(--radius-lg);
    overflow: hidden;
    position: relative;
    transition:
      border-color 0.25s ease,
      box-shadow 0.25s ease;
  }

  .doc-card:hover {
    border-color: rgba(99, 102, 241, 0.25);
    box-shadow:
      var(--shadow-md),
      0 0 0 1px rgba(99, 102, 241, 0.05);
  }

  .doc-card.is-processing {
    border-color: rgba(99, 102, 241, 0.3);
    animation: pulse-border 2s ease-in-out infinite;
  }

  .doc-card.is-processing::before {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    height: 3px;
    background: linear-gradient(90deg, transparent, var(--primary), transparent);
    animation: shimmer 1.5s ease-in-out infinite;
    border-radius: var(--radius-lg) var(--radius-lg) 0 0;
  }

  @keyframes pulse-border {
    0%,
    100% {
      box-shadow: 0 0 0 0 rgba(99, 102, 241, 0.1);
    }
    50% {
      box-shadow: 0 0 0 4px rgba(99, 102, 241, 0.08);
    }
  }

  @keyframes shimmer {
    0% {
      transform: translateX(-100%);
    }
    100% {
      transform: translateX(100%);
    }
  }

  /* ── Collapse toggle ── */
  .btn-collapse {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    width: 32px;
    height: 32px;
    border: 1px solid var(--border);
    border-radius: var(--radius-sm);
    background: var(--surface);
    cursor: pointer;
    transition: all 0.2s ease;
    flex-shrink: 0;
  }

  .btn-collapse:hover {
    background: var(--surface-alt);
  }

  .btn-collapse .btn-icon {
    transition: transform 0.25s ease;
  }

  .btn-collapse .btn-icon.rotated {
    transform: rotate(180deg);
  }

  /* ── Collapse transition ── */
  .collapse-enter-active,
  .collapse-leave-active {
    transition: all 0.3s ease;
    overflow: hidden;
  }

  .collapse-enter-from,
  .collapse-leave-to {
    opacity: 0;
    max-height: 0;
  }

  .collapse-enter-to,
  .collapse-leave-from {
    opacity: 1;
    max-height: 2000px;
  }

  /* ── Header ── */
  .doc-header {
    display: flex;
    align-items: center;
    gap: 0.75rem;
    padding: 1rem 1.25rem;
    background: var(--surface-alt);
    border-bottom: 1px solid var(--border-subtle);
  }

  .is-collapsed .doc-header {
    border-bottom: none;
  }

  .doc-icon-wrap {
    display: flex;
    align-items: center;
    justify-content: center;
    width: 42px;
    height: 42px;
    background: linear-gradient(135deg, var(--primary-light), rgba(99, 102, 241, 0.12));
    border-radius: 10px;
    flex-shrink: 0;
  }

  .doc-icon-wrap svg {
    width: 20px;
    height: 20px;
    color: var(--primary);
  }

  .doc-info {
    flex: 1;
    min-width: 0;
  }

  .doc-name {
    margin: 0;
    font-size: 0.95rem;
    font-weight: 600;
    color: var(--text);
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
  }

  .doc-meta {
    display: flex;
    flex-wrap: wrap;
    gap: 0.4rem;
    margin-top: 0.35rem;
  }

  .meta-badge {
    display: inline-flex;
    align-items: center;
    gap: 0.25rem;
    padding: 0.18rem 0.55rem;
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 999px;
    font-size: 0.72rem;
    font-weight: 500;
    color: var(--text-muted);
  }

  .meta-icon {
    width: 11px;
    height: 11px;
  }

  .meta-qa-count {
    background: var(--primary-light);
    border-color: rgba(99, 102, 241, 0.15);
    color: var(--primary);
  }

  .status-dot {
    width: 6px;
    height: 6px;
    border-radius: 50%;
    background: currentColor;
  }

  .status-ready {
    background: var(--accent-light);
    border-color: #a7f3d0;
    color: #059669;
  }

  .status-processing {
    background: #fffbeb;
    border-color: #fde68a;
    color: #d97706;
  }

  .status-failed {
    background: var(--danger-light);
    border-color: #fecaca;
    color: #dc2626;
  }

  .doc-actions {
    display: flex;
    gap: 0.4rem;
    flex-shrink: 0;
  }

  .btn-action {
    display: inline-flex;
    align-items: center;
    gap: 0.35rem;
    padding: 0.5rem 0.9rem;
    border: 1px solid var(--border);
    border-radius: var(--radius-sm);
    background: var(--surface);
    color: var(--text);
    font-size: 0.82rem;
    font-weight: 500;
    cursor: pointer;
    transition: all 0.2s ease;
    flex-shrink: 0;
  }

  .btn-summarize:hover:not(:disabled) {
    background: var(--primary-light);
    border-color: var(--primary);
    color: var(--primary);
    box-shadow: 0 2px 8px rgba(99, 102, 241, 0.15);
  }

  .btn-download:hover {
    background: rgba(16, 185, 129, 0.08);
    border-color: var(--accent);
    color: var(--accent);
    box-shadow: 0 2px 8px rgba(16, 185, 129, 0.15);
  }

  .btn-action:disabled {
    opacity: 0.5;
    cursor: not-allowed;
  }

  .btn-icon {
    width: 15px;
    height: 15px;
  }

  .btn-icon-xs {
    width: 13px;
    height: 13px;
  }

  .btn-icon-only {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    width: 36px;
    height: 36px;
    border: 1px solid var(--border);
    border-radius: var(--radius-sm);
    background: var(--surface);
    cursor: pointer;
    transition: all 0.2s ease;
    flex-shrink: 0;
  }

  .btn-icon-only svg {
    width: 15px;
    height: 15px;
    color: var(--text-light);
  }

  .btn-danger:hover {
    background: var(--danger-light);
    border-color: var(--danger);
  }

  .btn-danger:hover svg {
    color: var(--danger);
  }

  @keyframes spin {
    to {
      transform: rotate(360deg);
    }
  }

  .spin {
    animation: spin 1s linear infinite;
  }

  /* ── Sections ── */
  .section {
    padding: 1rem 1.25rem;
  }

  .summary-section {
    border-bottom: 1px solid var(--border-subtle);
  }

  .section-label {
    display: flex;
    align-items: center;
    gap: 0.35rem;
    font-size: 0.72rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.06em;
    color: var(--text-light);
    margin-bottom: 0.6rem;
  }

  .label-icon {
    width: 13px;
    height: 13px;
  }

  .summary-content {
    padding: 0.85rem 1rem;
    background: var(--surface-alt);
    border-radius: var(--radius-sm);
    border-left: 3px solid var(--primary);
    position: relative;
  }

  .btn-copy {
    display: inline-flex;
    align-items: center;
    gap: 0.3rem;
    margin-top: 0.6rem;
    padding: 0.35rem 0.7rem;
    border: 1px solid var(--border);
    border-radius: var(--radius-sm);
    background: var(--surface);
    color: var(--text-muted);
    font-size: 0.75rem;
    font-weight: 500;
    cursor: pointer;
    transition: all 0.2s ease;
  }

  .btn-copy:hover {
    border-color: var(--primary);
    color: var(--primary);
    background: var(--primary-light);
  }

  .copy-icon {
    width: 13px;
    height: 13px;
  }

  .summary-text {
    margin: 0;
    font-size: 0.88rem;
    line-height: 1.7;
    color: var(--text);
  }

  .empty-summary {
    display: flex;
    align-items: center;
    gap: 0.65rem;
    padding: 0.85rem 1rem;
    background: var(--surface-alt);
    border-radius: var(--radius-sm);
    font-size: 0.85rem;
    color: var(--text-light);
    border: 1px dashed var(--border);
  }

  .empty-summary-graphic {
    width: 32px;
    height: 32px;
    background: var(--primary-light);
    border-radius: 8px;
    display: flex;
    align-items: center;
    justify-content: center;
    flex-shrink: 0;
  }

  .empty-summary-graphic svg {
    width: 16px;
    height: 16px;
    color: var(--primary);
  }

  /* ── Q&A ── */
  .qa-section {
    padding-top: 0.75rem;
  }

  .btn-view:hover {
    background: rgba(139, 92, 246, 0.08);
    border-color: #8b5cf6;
    color: #8b5cf6;
    box-shadow: 0 2px 8px rgba(139, 92, 246, 0.15);
  }
  .empty-qa {
    margin-top: 0.65rem;
    padding: 0.75rem 1rem;
    background: var(--surface-alt);
    border-radius: var(--radius-sm);
    font-size: 0.82rem;
    color: var(--text-light);
    border: 1px dashed var(--border);
    text-align: center;
    justify-content: center;
    z-index: 10;
    border-radius: var(--radius-lg);
  }

  .confirm-card {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: var(--radius-lg);
    padding: 1.75rem;
    text-align: center;
    max-width: 340px;
    box-shadow: var(--shadow-lg);
  }

  .confirm-icon-wrap {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    width: 48px;
    height: 48px;
    background: var(--danger-light);
    border-radius: 50%;
    margin-bottom: 0.85rem;
  }

  .confirm-icon-wrap svg {
    width: 22px;
    height: 22px;
    color: var(--danger);
  }

  .confirm-text {
    margin: 0 0 0.35rem;
    font-size: 0.95rem;
    font-weight: 700;
    color: var(--text);
  }

  .confirm-sub {
    margin: 0 0 1.5rem;
    font-size: 0.82rem;
    color: var(--text-muted);
    line-height: 1.5;
  }

  .confirm-actions {
    display: flex;
    gap: 0.5rem;
    justify-content: center;
  }

  .btn-confirm {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    gap: 0.3rem;
    padding: 0.55rem 1.25rem;
    border-radius: var(--radius-sm);
    font-size: 0.85rem;
    font-weight: 600;
    cursor: pointer;
    border: 1px solid var(--border);
    transition: all 0.15s ease;
  }

  .btn-cancel {
    background: var(--surface);
    color: var(--text);
  }

  .btn-cancel:hover {
    background: var(--surface-alt);
  }

  .btn-delete {
    background: var(--danger);
    color: white;
    border-color: var(--danger);
  }

  .btn-delete:hover {
    background: #dc2626;
    border-color: #dc2626;
    box-shadow: 0 2px 8px rgba(239, 68, 68, 0.3);
  }

  .fade-enter-active,
  .fade-leave-active {
    transition: opacity 0.2s ease;
  }

  .fade-enter-from,
  .fade-leave-to {
    opacity: 0;
  }

  @media (max-width: 640px) {
    .doc-header {
      flex-wrap: wrap;
      gap: 0.5rem;
    }
    .doc-actions {
      width: 100%;
      justify-content: flex-end;
      flex-wrap: wrap;
    }
    .doc-name {
      font-size: 0.85rem;
    }
    .btn-action {
      font-size: 0.75rem;
      padding: 0.4rem 0.6rem;
    }
  }
</style>
