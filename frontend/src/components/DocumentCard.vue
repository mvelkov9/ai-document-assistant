<script setup>
import { ref } from 'vue'

const props = defineProps({
  document: { type: Object, required: true },
  summaryBusy: { type: Boolean, default: false },
  questionBusy: { type: Boolean, default: false },
  latestAnswer: { type: Object, default: null },
})

const emit = defineEmits(['summarize', 'ask', 'delete', 'download'])
const questionDraft = ref('')
const confirmingDelete = ref(false)

function handleAsk() {
  const q = questionDraft.value.trim()
  if (q.length < 3) return
  emit('ask', props.document.id, q)
  questionDraft.value = ''
}

function handleDelete() {
  emit('delete', props.document.id)
  confirmingDelete.value = false
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
  <article class="doc-card">
    <!-- ── Header ── -->
    <div class="doc-header">
      <div class="doc-icon-wrap">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
          <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/>
          <polyline points="14 2 14 8 20 8"/>
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
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" class="meta-icon"><rect x="3" y="4" width="18" height="18" rx="2" ry="2"/><line x1="16" y1="2" x2="16" y2="6"/><line x1="8" y1="2" x2="8" y2="6"/><line x1="3" y1="10" x2="21" y2="10"/></svg>
            {{ formatDate(document.created_at) }}
          </span>
        </div>
      </div>
      <div class="doc-actions">
        <button class="btn-action btn-download" @click="emit('download', document.id, document.original_filename)" title="Prenesi PDF">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" class="btn-icon"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="7 10 12 15 17 10"/><line x1="12" y1="15" x2="12" y2="3"/></svg>
          Prenesi
        </button>
        <button class="btn-action btn-summarize" :disabled="summaryBusy" @click="emit('summarize', document.id)">
          <svg v-if="summaryBusy" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" class="btn-icon spin"><path d="M21 12a9 9 0 1 1-6.219-8.56"/></svg>
          <svg v-else viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" class="btn-icon"><circle cx="12" cy="12" r="3"/><path d="M12 1v2M12 21v2M4.22 4.22l1.42 1.42M18.36 18.36l1.42 1.42M1 12h2M21 12h2M4.22 19.78l1.42-1.42M18.36 5.64l1.42-1.42"/></svg>
          {{ summaryBusy ? 'Generiranje...' : 'Povzetek' }}
        </button>
        <button class="btn-icon-only btn-danger" @click="confirmingDelete = true" title="Izbriši dokument">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="3 6 5 6 21 6"/><path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"/></svg>
        </button>
      </div>
    </div>

    <!-- ── Delete Confirmation ── -->
    <Transition name="fade">
      <div v-if="confirmingDelete" class="confirm-overlay">
        <div class="confirm-card">
          <div class="confirm-icon-wrap">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="3 6 5 6 21 6"/><path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"/></svg>
          </div>
          <p class="confirm-text">Izbrisati <strong>{{ document.original_filename }}</strong>?</p>
          <p class="confirm-sub">To bo trajno izbrisalo datoteko in vse povezane povzetke ter vprašanja.</p>
          <div class="confirm-actions">
            <button class="btn-confirm btn-cancel" @click="confirmingDelete = false">Prekliči</button>
            <button class="btn-confirm btn-delete" @click="handleDelete">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" class="btn-icon-xs"><polyline points="3 6 5 6 21 6"/><path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"/></svg>
              Izbriši
            </button>
          </div>
        </div>
      </div>
    </Transition>

    <!-- ── Summary Section ── -->
    <div class="section summary-section">
      <div class="section-label">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" class="label-icon"><line x1="17" y1="10" x2="3" y2="10"/><line x1="21" y1="6" x2="3" y2="6"/><line x1="21" y1="14" x2="3" y2="14"/><line x1="17" y1="18" x2="3" y2="18"/></svg>
        Povzetek
      </div>
      <div v-if="!document.summary_text" class="empty-summary">
        <div class="empty-summary-graphic">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
            <circle cx="12" cy="12" r="3"/><path d="M12 1v2M12 21v2M4.22 4.22l1.42 1.42M18.36 18.36l1.42 1.42M1 12h2M21 12h2M4.22 19.78l1.42-1.42M18.36 5.64l1.42-1.42"/>
          </svg>
        </div>
        <span>Klikni <strong>Povzetek</strong> za generiranje AI povzetka</span>
      </div>
      <div v-else class="summary-content">
        <p class="summary-text">{{ document.summary_text }}</p>
      </div>
    </div>

    <!-- ── Q&A Section ── -->
    <div class="section qa-section">
      <div class="section-label">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" class="label-icon"><path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/></svg>
        Vprašanje
      </div>
      <div class="qa-input-row">
        <textarea
          v-model="questionDraft"
          rows="2"
          maxlength="500"
          placeholder="Npr.: Kateri je glavni namen dokumenta?"
        />
        <button class="btn-send" :disabled="questionBusy || questionDraft.trim().length < 3" @click="handleAsk">
          <svg v-if="questionBusy" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" class="btn-icon spin"><path d="M21 12a9 9 0 1 1-6.219-8.56"/></svg>
          <svg v-else viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" class="btn-icon"><line x1="22" y1="2" x2="11" y2="13"/><polygon points="22 2 15 22 11 13 2 9 22 2"/></svg>
          Pošlji
        </button>
      </div>

      <Transition name="answer">
        <div v-if="latestAnswer" class="answer-box">
          <div class="answer-header">
            <div class="answer-label">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" class="label-icon"><path d="M21 11.5a8.38 8.38 0 0 1-.9 3.8 8.5 8.5 0 0 1-7.6 4.7 8.38 8.38 0 0 1-3.8-.9L3 21l1.9-5.7a8.38 8.38 0 0 1-.9-3.8 8.5 8.5 0 0 1 4.7-7.6 8.38 8.38 0 0 1 3.8-.9h.5a8.48 8.48 0 0 1 8 8v.5z"/></svg>
              <span>Odgovor</span>
            </div>
            <span class="source-badge">{{ latestAnswer.source_mode }}</span>
          </div>
          <div class="answer-bubble answer-q">
            <strong>V:</strong> {{ latestAnswer.question_text }}
          </div>
          <div class="answer-bubble answer-a">
            <strong>O:</strong> {{ latestAnswer.answer_text }}
          </div>
        </div>
      </Transition>
    </div>
  </article>
</template>

<style scoped>
.doc-card {
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: var(--radius-lg);
  overflow: hidden;
  position: relative;
  transition: border-color 0.25s ease, box-shadow 0.25s ease;
}

.doc-card:hover {
  border-color: rgba(99, 102, 241, 0.25);
  box-shadow: var(--shadow-md), 0 0 0 1px rgba(99, 102, 241, 0.05);
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

.doc-icon-wrap {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 42px;
  height: 42px;
  background: linear-gradient(135deg, var(--primary-light), rgba(99,102,241,0.12));
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
  box-shadow: 0 2px 8px rgba(99,102,241,0.15);
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
  to { transform: rotate(360deg); }
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
.qa-input-row {
  display: flex;
  gap: 0.5rem;
  align-items: flex-end;
}

.qa-input-row textarea {
  flex: 1;
  border: 1.5px solid var(--border);
  border-radius: var(--radius-sm);
  padding: 0.65rem 0.85rem;
  background: var(--surface-alt);
  font-size: 0.88rem;
  resize: vertical;
  min-height: 2.5rem;
  transition: all 0.2s ease;
}

.qa-input-row textarea:focus {
  outline: none;
  border-color: var(--primary);
  background: var(--surface);
  box-shadow: var(--shadow-glow);
}

.qa-input-row textarea::placeholder {
  color: var(--text-light);
}

.btn-send {
  display: inline-flex;
  align-items: center;
  gap: 0.35rem;
  padding: 0.55rem 0.9rem;
  border: 0;
  border-radius: var(--radius-sm);
  background: linear-gradient(135deg, var(--primary), #818cf8);
  color: white;
  font-size: 0.82rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s ease;
  flex-shrink: 0;
  box-shadow: 0 2px 6px rgba(99,102,241,0.25);
}

.btn-send:hover:not(:disabled) {
  box-shadow: 0 4px 12px rgba(99,102,241,0.35);
}

.btn-send:disabled {
  opacity: 0.45;
  cursor: not-allowed;
  box-shadow: none;
}

.btn-send .btn-icon {
  color: white;
}

/* ── Answer Box ── */
.answer-box {
  margin-top: 0.85rem;
  padding: 1rem;
  background: var(--surface-alt);
  border-radius: var(--radius-sm);
  border: 1px solid var(--border-subtle);
}

.answer-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 0.65rem;
}

.answer-label {
  display: flex;
  align-items: center;
  gap: 0.3rem;
  font-size: 0.72rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.06em;
  color: var(--text-light);
}

.source-badge {
  padding: 0.15rem 0.5rem;
  background: var(--primary-light);
  color: var(--primary);
  border-radius: 999px;
  font-size: 0.68rem;
  font-weight: 600;
}

.answer-bubble {
  padding: 0.65rem 0.85rem;
  border-radius: var(--radius-sm);
  font-size: 0.86rem;
  line-height: 1.65;
  margin-bottom: 0.5rem;
}

.answer-bubble:last-child {
  margin-bottom: 0;
}

.answer-q {
  background: var(--surface);
  border: 1px solid var(--border);
  color: var(--text-muted);
}

.answer-a {
  background: var(--primary-light);
  border: 1px solid rgba(99,102,241,0.12);
  color: var(--text);
}

.answer-enter-active {
  transition: all 0.3s ease;
}

.answer-enter-from {
  opacity: 0;
  transform: translateY(8px);
}

/* ── Confirm Overlay ── */
.confirm-overlay {
  position: absolute;
  inset: 0;
  background: rgba(0, 0, 0, 0.5);
  backdrop-filter: blur(6px);
  display: flex;
  align-items: center;
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
  box-shadow: 0 2px 8px rgba(239,68,68,0.3);
}

.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.2s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
</style>
