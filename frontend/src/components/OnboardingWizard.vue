<script setup>
  import { ref } from 'vue'

  const emit = defineEmits(['dismiss', 'go-upload'])
  const step = ref(0)

  const steps = [
    {
      title: 'Dobrodošli v DocAssist!',
      text: 'Tvoj AI asistent za dokumente. Nauči se, kako v treh korakih izkoristiš vse.',
      icon: 'welcome',
    },
    {
      title: '1. Naloži PDF dokument',
      text: 'Klikni "Naloži" v stranskem meniju ali povleci datoteke na nalagalno območje. Podpira se več datotek hkrati.',
      icon: 'upload',
    },
    {
      title: '2. Generiraj AI povzetek',
      text: 'Klikni gumb "Povzetek" na kartici dokumenta. AI bo prebral vsebino in ustvaril strukturiran povzetek.',
      icon: 'summary',
    },
    {
      title: '3. Zastavi vprašanje',
      text: 'Odpri chat in vprašaj karkoli o dokumentu. AI poišče odgovor v vsebini s pomočjo RAG-lite tehnologije.',
      icon: 'question',
    },
  ]

  function next() {
    if (step.value < steps.length - 1) step.value++
    else emit('go-upload')
  }

  function prev() {
    if (step.value > 0) step.value--
  }
</script>

<template>
  <div class="wizard-backdrop">
    <div class="wizard-card">
      <button class="wizard-close" @click="emit('dismiss')" title="Preskoči">&times;</button>

      <div class="wizard-progress">
        <div
          v-for="(s, i) in steps"
          :key="i"
          class="progress-dot"
          :class="{ active: i === step, done: i < step }"
          @click="step = i"
        ></div>
      </div>

      <Transition name="wizard-step" mode="out-in">
        <div :key="step" class="wizard-body">
          <div class="wizard-icon" :class="'wi-' + steps[step].icon">
            <svg
              v-if="steps[step].icon === 'welcome'"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              stroke-width="1.5"
            >
              <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z" />
              <polyline points="14 2 14 8 20 8" />
              <path d="M9 15l2 2 4-4" />
            </svg>
            <svg
              v-else-if="steps[step].icon === 'upload'"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              stroke-width="1.5"
            >
              <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4" />
              <polyline points="17 8 12 3 7 8" />
              <line x1="12" y1="3" x2="12" y2="15" />
            </svg>
            <svg
              v-else-if="steps[step].icon === 'summary'"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              stroke-width="1.5"
            >
              <circle cx="12" cy="12" r="3" />
              <path
                d="M12 1v2M12 21v2M4.22 4.22l1.42 1.42M18.36 18.36l1.42 1.42M1 12h2M21 12h2M4.22 19.78l1.42-1.42M18.36 5.64l1.42-1.42"
              />
            </svg>
            <svg v-else viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
              <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z" />
            </svg>
          </div>
          <h3 class="wizard-title">{{ steps[step].title }}</h3>
          <p class="wizard-text">{{ steps[step].text }}</p>
        </div>
      </Transition>

      <div class="wizard-actions">
        <button v-if="step > 0" class="wiz-btn wiz-btn-secondary" @click="prev">Nazaj</button>
        <span v-else></span>
        <button class="wiz-btn wiz-btn-primary" @click="next">
          {{ step < steps.length - 1 ? 'Naprej' : 'Začni z nalaganjem' }}
        </button>
      </div>
    </div>
  </div>
</template>

<style scoped>
  .wizard-backdrop {
    position: fixed;
    inset: 0;
    background: rgba(0, 0, 0, 0.4);
    backdrop-filter: blur(4px);
    display: flex;
    align-items: center;
    justify-content: center;
    z-index: 100;
    padding: 1rem;
  }
  .wizard-card {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: var(--radius-lg);
    padding: 2rem 2.5rem;
    max-width: 440px;
    width: 100%;
    text-align: center;
    position: relative;
    box-shadow: 0 20px 60px rgba(0, 0, 0, 0.2);
  }
  .wizard-close {
    position: absolute;
    top: 0.75rem;
    right: 0.75rem;
    width: 28px;
    height: 28px;
    border: none;
    background: var(--surface-alt);
    border-radius: 50%;
    font-size: 1.1rem;
    color: var(--text-light);
    cursor: pointer;
    display: flex;
    align-items: center;
    justify-content: center;
    transition: all 0.15s;
  }
  .wizard-close:hover {
    background: var(--border);
    color: var(--text);
  }
  .wizard-progress {
    display: flex;
    justify-content: center;
    gap: 0.5rem;
    margin-bottom: 1.5rem;
  }
  .progress-dot {
    width: 10px;
    height: 10px;
    border-radius: 50%;
    background: var(--border);
    cursor: pointer;
    transition: all 0.2s;
  }
  .progress-dot.active {
    background: var(--primary);
    transform: scale(1.2);
  }
  .progress-dot.done {
    background: #10b981;
  }
  .wizard-body {
    min-height: 200px;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
  }
  .wizard-icon {
    width: 72px;
    height: 72px;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    margin-bottom: 1rem;
  }
  .wizard-icon svg {
    width: 34px;
    height: 34px;
  }
  .wi-welcome {
    background: linear-gradient(135deg, var(--primary-light), rgba(99, 102, 241, 0.15));
    color: var(--primary);
  }
  .wi-upload {
    background: linear-gradient(135deg, rgba(16, 185, 129, 0.1), rgba(16, 185, 129, 0.18));
    color: #10b981;
  }
  .wi-summary {
    background: linear-gradient(135deg, rgba(245, 158, 11, 0.1), rgba(245, 158, 11, 0.18));
    color: #f59e0b;
  }
  .wi-question {
    background: linear-gradient(135deg, rgba(139, 92, 246, 0.1), rgba(139, 92, 246, 0.18));
    color: #8b5cf6;
  }
  .wizard-title {
    font-size: 1.1rem;
    font-weight: 700;
    margin: 0 0 0.5rem;
    color: var(--text);
  }
  .wizard-text {
    font-size: 0.88rem;
    color: var(--text-light);
    line-height: 1.6;
    margin: 0;
    max-width: 340px;
  }
  .wizard-actions {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-top: 1.5rem;
  }
  .wiz-btn {
    padding: 0.55rem 1.2rem;
    border-radius: var(--radius-sm);
    font-size: 0.85rem;
    font-weight: 600;
    cursor: pointer;
    transition: all 0.2s;
    border: none;
  }
  .wiz-btn-primary {
    background: linear-gradient(135deg, var(--primary), #818cf8);
    color: white;
    box-shadow: 0 2px 8px rgba(99, 102, 241, 0.25);
  }
  .wiz-btn-primary:hover {
    box-shadow: 0 4px 14px rgba(99, 102, 241, 0.35);
  }
  .wiz-btn-secondary {
    background: var(--surface-alt);
    color: var(--text);
    border: 1px solid var(--border);
  }
  .wiz-btn-secondary:hover {
    background: var(--border);
  }
  .wizard-step-enter-active,
  .wizard-step-leave-active {
    transition: all 0.25s ease;
  }
  .wizard-step-enter-from {
    opacity: 0;
    transform: translateX(20px);
  }
  .wizard-step-leave-to {
    opacity: 0;
    transform: translateX(-20px);
  }

  @media (max-width: 480px) {
    .wizard-card {
      padding: 1.5rem;
    }
  }
</style>
