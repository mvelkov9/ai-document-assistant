<script setup>
  import { ref, nextTick, watch, computed } from 'vue'
  import { marked } from 'marked'

  marked.setOptions({ breaks: true, gfm: true })

  const props = defineProps({
    answers: { type: Array, default: () => [] },
    questionBusy: { type: Boolean, default: false },
  })

  const emit = defineEmits(['ask', 'delete-answer', 'clear-answers'])

  const questionDraft = ref('')
  const chatBody = ref(null)
  const confirmClear = ref(false)

  /* Answers sorted chronologically (oldest first for chat flow) */
  const sortedAnswers = computed(() => {
    if (!props.answers.length) return []
    return [...props.answers].sort(
      (a, b) => new Date(a.created_at) - new Date(b.created_at),
    )
  })

  function handleSend() {
    const q = questionDraft.value.trim()
    if (q.length < 3) return
    emit('ask', q)
    questionDraft.value = ''
  }

  function handleKeydown(e) {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSend()
    }
  }

  function renderMd(text) {
    return marked.parse(text || '')
  }

  function formatTime(iso) {
    if (!iso) return ''
    return new Date(iso).toLocaleTimeString('sl-SI', { hour: '2-digit', minute: '2-digit' })
  }

  function formatDate(iso) {
    if (!iso) return ''
    return new Date(iso).toLocaleDateString('sl-SI', { day: 'numeric', month: 'short' })
  }

  /* Auto-scroll to bottom when answers change */
  watch(
    () => props.answers.length,
    async () => {
      await nextTick()
      if (chatBody.value) chatBody.value.scrollTop = chatBody.value.scrollHeight
    },
  )
</script>

<template>
  <div class="chat-qa">
    <!-- Chat header with clear button -->
    <div v-if="sortedAnswers.length" class="chat-header">
      <span class="chat-header-count">{{ sortedAnswers.length }} sporočil</span>
      <button v-if="!confirmClear" class="chat-clear-btn" @click="confirmClear = true" title="Počisti pogovor">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <polyline points="3 6 5 6 21 6" />
          <path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2" />
        </svg>
        Počisti
      </button>
      <div v-else class="chat-clear-confirm">
        <span class="chat-clear-q">Počistiti ves pogovor?</span>
        <button class="chat-clear-yes" @click="emit('clear-answers'); confirmClear = false">Da</button>
        <button class="chat-clear-no" @click="confirmClear = false">Ne</button>
      </div>
    </div>

    <!-- Chat body -->
    <div class="chat-body" ref="chatBody">
      <!-- Empty state -->
      <div v-if="!sortedAnswers.length && !questionBusy" class="chat-empty">
        <div class="chat-empty-icon">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
            <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z" />
          </svg>
        </div>
        <p class="chat-empty-text">Zastavi vprašanje o tem dokumentu</p>
        <p class="chat-empty-hint">AI bo poiskal odgovor v vsebini datoteke</p>
      </div>

      <!-- Messages -->
      <template v-for="answer in sortedAnswers" :key="answer.id || answer.created_at">
        <!-- User question (right) -->
        <div class="chat-row chat-row-user">
          <div class="chat-bubble chat-bubble-user">
            <p class="chat-bubble-text">{{ answer.question_text }}</p>
            <span class="chat-time">{{ formatDate(answer.created_at) }} {{ formatTime(answer.created_at) }}</span>
          </div>
        </div>
        <!-- AI answer (left) -->
        <div class="chat-row chat-row-ai">
          <div class="chat-avatar-ai">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <circle cx="12" cy="12" r="3" />
              <path d="M12 1v2M12 21v2M4.22 4.22l1.42 1.42M18.36 18.36l1.42 1.42M1 12h2M21 12h2M4.22 19.78l1.42-1.42M18.36 5.64l1.42-1.42" />
            </svg>
          </div>
          <div class="chat-bubble chat-bubble-ai">
            <div class="chat-bubble-md" v-html="renderMd(answer.answer_text)"></div>
            <div class="chat-bubble-footer">
              <span class="chat-source">{{ answer.source_mode }}</span>
              <span class="chat-time">{{ formatTime(answer.created_at) }}</span>
              <button class="chat-delete-btn" title="Izbriši" @click="emit('delete-answer', answer.id)">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <polyline points="3 6 5 6 21 6" />
                  <path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2" />
                </svg>
              </button>
            </div>
          </div>
        </div>
      </template>

      <!-- Typing indicator -->
      <div v-if="questionBusy" class="chat-row chat-row-ai">
        <div class="chat-avatar-ai">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <circle cx="12" cy="12" r="3" />
            <path d="M12 1v2M12 21v2M4.22 4.22l1.42 1.42M18.36 18.36l1.42 1.42M1 12h2M21 12h2M4.22 19.78l1.42-1.42M18.36 5.64l1.42-1.42" />
          </svg>
        </div>
        <div class="chat-bubble chat-bubble-ai chat-typing">
          <span class="typing-dot"></span>
          <span class="typing-dot"></span>
          <span class="typing-dot"></span>
        </div>
      </div>
    </div>

    <!-- Input bar -->
    <div class="chat-input-bar">
      <textarea
        v-model="questionDraft"
        @keydown="handleKeydown"
        rows="1"
        maxlength="500"
        placeholder="Napiši vprašanje..."
        class="chat-textarea"
      />
      <button
        class="chat-send-btn"
        :disabled="questionBusy || questionDraft.trim().length < 3"
        @click="handleSend"
        title="Pošlji"
      >
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <line x1="22" y1="2" x2="11" y2="13" />
          <polygon points="22 2 15 22 11 13 2 9 22 2" />
        </svg>
      </button>
    </div>
  </div>
</template>

<style scoped>
.chat-qa {
  display: flex;
  flex-direction: column;
  border: 1px solid var(--border);
  border-radius: var(--radius-sm);
  overflow: hidden;
  background: var(--bg);
  max-height: 440px;
}

.chat-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0.4rem 0.75rem;
  border-bottom: 1px solid var(--border);
  background: var(--surface);
  min-height: 32px;
}
.chat-header-count {
  font-size: 0.7rem;
  font-weight: 600;
  color: var(--text-light);
}
.chat-clear-btn {
  display: inline-flex;
  align-items: center;
  gap: 0.3rem;
  border: none;
  background: transparent;
  color: var(--text-light);
  font-size: 0.7rem;
  font-weight: 600;
  cursor: pointer;
  padding: 0.2rem 0.5rem;
  border-radius: var(--radius-sm);
  transition: all 0.15s;
}
.chat-clear-btn svg { width: 12px; height: 12px; }
.chat-clear-btn:hover { background: rgba(239,68,68,0.08); color: #ef4444; }
.chat-clear-confirm {
  display: flex;
  align-items: center;
  gap: 0.4rem;
}
.chat-clear-q {
  font-size: 0.7rem;
  font-weight: 600;
  color: var(--text);
}
.chat-clear-yes, .chat-clear-no {
  border: none;
  padding: 0.15rem 0.55rem;
  border-radius: var(--radius-sm);
  font-size: 0.68rem;
  font-weight: 700;
  cursor: pointer;
  transition: all 0.15s;
}
.chat-clear-yes {
  background: #ef4444;
  color: white;
}
.chat-clear-yes:hover { background: #dc2626; }
.chat-clear-no {
  background: var(--surface-alt);
  color: var(--text);
}
.chat-clear-no:hover { background: var(--border); }

.chat-body {
  flex: 1;
  overflow-y: auto;
  padding: 0.75rem;
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  min-height: 120px;
  max-height: 340px;
}

/* Empty state */
.chat-empty {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 1.5rem 1rem;
  text-align: center;
  flex: 1;
}
.chat-empty-icon {
  width: 40px;
  height: 40px;
  background: var(--primary-light);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 0.5rem;
}
.chat-empty-icon svg { width: 20px; height: 20px; color: var(--primary); }
.chat-empty-text { margin: 0; font-size: 0.85rem; font-weight: 600; color: var(--text); }
.chat-empty-hint { margin: 0.2rem 0 0; font-size: 0.75rem; color: var(--text-light); }

/* Chat rows */
.chat-row { display: flex; gap: 0.4rem; }
.chat-row-user { justify-content: flex-end; }
.chat-row-ai { justify-content: flex-start; align-items: flex-start; }

/* Avatar */
.chat-avatar-ai {
  width: 28px;
  height: 28px;
  background: linear-gradient(135deg, var(--primary), #818cf8);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  margin-top: 2px;
}
.chat-avatar-ai svg { width: 14px; height: 14px; color: white; }

/* Bubbles */
.chat-bubble {
  max-width: 80%;
  padding: 0.55rem 0.8rem;
  border-radius: 12px;
  font-size: 0.84rem;
  line-height: 1.55;
  word-break: break-word;
}
.chat-bubble-user {
  background: linear-gradient(135deg, var(--primary), #818cf8);
  color: white;
  border-bottom-right-radius: 4px;
}
.chat-bubble-ai {
  background: var(--surface);
  border: 1px solid var(--border-subtle);
  color: var(--text);
  border-bottom-left-radius: 4px;
}

.chat-bubble-text { margin: 0; }

.chat-bubble-md { overflow: hidden; }
.chat-bubble-md :deep(p) { margin: 0 0 0.3rem; }
.chat-bubble-md :deep(p:last-child) { margin-bottom: 0; }
.chat-bubble-md :deep(ul), .chat-bubble-md :deep(ol) { margin: 0.3rem 0; padding-left: 1.2rem; }
.chat-bubble-md :deep(code) {
  background: rgba(99,102,241,0.08);
  padding: 0.1rem 0.3rem;
  border-radius: 3px;
  font-size: 0.8rem;
}
.chat-bubble-md :deep(pre) {
  background: var(--surface-alt);
  padding: 0.5rem;
  border-radius: 6px;
  overflow-x: auto;
  font-size: 0.78rem;
  margin: 0.3rem 0;
}
.chat-bubble-md :deep(strong) { font-weight: 700; }

/* Footer inside AI bubble */
.chat-bubble-footer {
  display: flex;
  align-items: center;
  gap: 0.4rem;
  margin-top: 0.35rem;
  padding-top: 0.3rem;
  border-top: 1px solid var(--border-subtle);
}

.chat-source {
  padding: 0.1rem 0.4rem;
  background: var(--primary-light);
  color: var(--primary);
  border-radius: 999px;
  font-size: 0.62rem;
  font-weight: 600;
}

.chat-time {
  font-size: 0.62rem;
  color: var(--text-light);
}

.chat-bubble-user .chat-time {
  display: block;
  text-align: right;
  margin-top: 0.2rem;
  opacity: 0.7;
  color: rgba(255,255,255,0.7);
}

.chat-delete-btn {
  margin-left: auto;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 20px;
  height: 20px;
  border: none;
  background: transparent;
  color: var(--text-light);
  border-radius: var(--radius-sm);
  cursor: pointer;
  padding: 0;
  transition: all 0.15s;
}
.chat-delete-btn svg { width: 12px; height: 12px; }
.chat-delete-btn:hover { background: rgba(239,68,68,0.1); color: #ef4444; }

/* Typing indicator */
.chat-typing {
  display: flex;
  align-items: center;
  gap: 4px;
  padding: 0.65rem 1rem;
}
.typing-dot {
  width: 7px;
  height: 7px;
  background: var(--text-light);
  border-radius: 50%;
  animation: typing-bounce 1.4s ease-in-out infinite;
}
.typing-dot:nth-child(2) { animation-delay: 0.2s; }
.typing-dot:nth-child(3) { animation-delay: 0.4s; }
@keyframes typing-bounce {
  0%, 60%, 100% { transform: translateY(0); opacity: 0.4; }
  30% { transform: translateY(-5px); opacity: 1; }
}

/* Input bar */
.chat-input-bar {
  display: flex;
  align-items: flex-end;
  gap: 0.4rem;
  padding: 0.5rem 0.65rem;
  border-top: 1px solid var(--border);
  background: var(--surface);
}

.chat-textarea {
  flex: 1;
  border: 1.5px solid var(--border);
  border-radius: 18px;
  padding: 0.5rem 0.85rem;
  background: var(--surface-alt);
  font-size: 0.84rem;
  resize: none;
  min-height: 36px;
  max-height: 80px;
  font-family: inherit;
  transition: border-color 0.2s;
}
.chat-textarea:focus {
  outline: none;
  border-color: var(--primary);
}
.chat-textarea::placeholder { color: var(--text-light); }

.chat-send-btn {
  width: 36px;
  height: 36px;
  border: none;
  border-radius: 50%;
  background: linear-gradient(135deg, var(--primary), #818cf8);
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  flex-shrink: 0;
  transition: all 0.2s;
  box-shadow: 0 2px 6px rgba(99,102,241,0.25);
}
.chat-send-btn svg { width: 16px; height: 16px; }
.chat-send-btn:hover:not(:disabled) { box-shadow: 0 4px 12px rgba(99,102,241,0.35); transform: scale(1.05); }
.chat-send-btn:disabled { opacity: 0.4; cursor: not-allowed; box-shadow: none; }

@media (max-width: 640px) {
  .chat-bubble { max-width: 90%; }
}
</style>
