<script setup>
  import { reactive, ref } from 'vue'

  defineProps({
    busy: { type: Boolean, default: false },
  })

  const emit = defineEmits(['login', 'register'])

  const mode = ref('login')

  const loginForm = reactive({ email: '', password: '' })
  const registerForm = reactive({ full_name: '', email: '', password: '' })

  function submitLogin() {
    emit('login', { ...loginForm })
  }

  function submitRegister() {
    emit('register', { ...registerForm })
  }
</script>

<template>
  <div class="auth-panel">
    <div class="auth-header">
      <div class="auth-icon-wrap">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z" />
        </svg>
      </div>
      <h3 class="auth-title">{{ mode === 'login' ? 'Dobrodošli nazaj' : 'Ustvari račun' }}</h3>
      <p class="auth-subtitle">
        {{ mode === 'login' ? 'Prijavi se za dostop do dokumentov' : 'Registriraj se za začetek' }}
      </p>
    </div>

    <div class="auth-tabs">
      <button class="auth-tab" :class="{ active: mode === 'login' }" @click="mode = 'login'">
        <svg
          viewBox="0 0 24 24"
          fill="none"
          stroke="currentColor"
          stroke-width="2"
          class="tab-icon"
        >
          <path d="M15 3h4a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2h-4" />
          <polyline points="10 17 15 12 10 7" />
          <line x1="15" y1="12" x2="3" y2="12" />
        </svg>
        Prijava
      </button>
      <button class="auth-tab" :class="{ active: mode === 'register' }" @click="mode = 'register'">
        <svg
          viewBox="0 0 24 24"
          fill="none"
          stroke="currentColor"
          stroke-width="2"
          class="tab-icon"
        >
          <path d="M16 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2" />
          <circle cx="8.5" cy="7" r="4" />
          <line x1="20" y1="8" x2="20" y2="14" />
          <line x1="23" y1="11" x2="17" y2="11" />
        </svg>
        Registracija
      </button>
    </div>

    <Transition name="form-switch" mode="out-in">
      <form v-if="mode === 'login'" key="login" class="auth-form" @submit.prevent="submitLogin">
        <div class="form-group">
          <label for="login-email">
            <svg
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              stroke-width="2"
              class="field-icon"
            >
              <path
                d="M4 4h16c1.1 0 2 .9 2 2v12c0 1.1-.9 2-2 2H4c-1.1 0-2-.9-2-2V6c0-1.1.9-2 2-2z"
              />
              <polyline points="22,6 12,13 2,6" />
            </svg>
            Email
          </label>
          <input
            id="login-email"
            v-model="loginForm.email"
            type="email"
            placeholder="ime@primer.com"
            autocomplete="email"
            required
          />
        </div>
        <div class="form-group">
          <label for="login-password">
            <svg
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              stroke-width="2"
              class="field-icon"
            >
              <rect x="3" y="11" width="18" height="11" rx="2" ry="2" />
              <path d="M7 11V7a5 5 0 0 1 10 0v4" />
            </svg>
            Geslo
          </label>
          <input
            id="login-password"
            v-model="loginForm.password"
            type="password"
            placeholder="Najmanj 8 znakov"
            minlength="8"
            autocomplete="current-password"
            required
          />
        </div>
        <button class="btn-primary" type="submit" :disabled="busy">
          <svg
            v-if="busy"
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
            <path d="M15 3h4a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2h-4" />
            <polyline points="10 17 15 12 10 7" />
            <line x1="15" y1="12" x2="3" y2="12" />
          </svg>
          {{ busy ? 'Prijavljam...' : 'Prijavi se' }}
        </button>
      </form>

      <form v-else key="register" class="auth-form" @submit.prevent="submitRegister">
        <div class="form-group">
          <label for="reg-name">
            <svg
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              stroke-width="2"
              class="field-icon"
            >
              <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2" />
              <circle cx="12" cy="7" r="4" />
            </svg>
            Polno ime
          </label>
          <input
            id="reg-name"
            v-model="registerForm.full_name"
            type="text"
            placeholder="Janez Novak"
            autocomplete="name"
            required
          />
        </div>
        <div class="form-group">
          <label for="reg-email">
            <svg
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              stroke-width="2"
              class="field-icon"
            >
              <path
                d="M4 4h16c1.1 0 2 .9 2 2v12c0 1.1-.9 2-2 2H4c-1.1 0-2-.9-2-2V6c0-1.1.9-2 2-2z"
              />
              <polyline points="22,6 12,13 2,6" />
            </svg>
            Email
          </label>
          <input
            id="reg-email"
            v-model="registerForm.email"
            type="email"
            placeholder="ime@primer.com"
            autocomplete="email"
            required
          />
        </div>
        <div class="form-group">
          <label for="reg-password">
            <svg
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              stroke-width="2"
              class="field-icon"
            >
              <rect x="3" y="11" width="18" height="11" rx="2" ry="2" />
              <path d="M7 11V7a5 5 0 0 1 10 0v4" />
            </svg>
            Geslo
          </label>
          <input
            id="reg-password"
            v-model="registerForm.password"
            type="password"
            placeholder="Najmanj 8 znakov"
            minlength="8"
            autocomplete="new-password"
            required
          />
        </div>
        <button class="btn-primary" type="submit" :disabled="busy">
          <svg
            v-if="busy"
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
            <path d="M16 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2" />
            <circle cx="8.5" cy="7" r="4" />
            <line x1="20" y1="8" x2="20" y2="14" />
            <line x1="23" y1="11" x2="17" y2="11" />
          </svg>
          {{ busy ? 'Registriram...' : 'Ustvari račun' }}
        </button>
      </form>
    </Transition>
  </div>
</template>

<style scoped>
  .auth-panel {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: var(--radius-xl, 20px);
    padding: 2rem 1.75rem;
    box-shadow: var(--shadow-md);
  }

  .auth-header {
    text-align: center;
    margin-bottom: 1.5rem;
  }

  .auth-icon-wrap {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    width: 48px;
    height: 48px;
    background: linear-gradient(135deg, var(--primary), #818cf8);
    border-radius: 14px;
    margin-bottom: 0.75rem;
  }

  .auth-icon-wrap svg {
    width: 22px;
    height: 22px;
    color: white;
  }

  .auth-title {
    margin: 0;
    font-size: 1.2rem;
    font-weight: 700;
    color: var(--text);
  }

  .auth-subtitle {
    margin: 0.3rem 0 0;
    font-size: 0.85rem;
    color: var(--text-muted);
  }

  .auth-tabs {
    display: flex;
    gap: 0.25rem;
    margin-bottom: 1.5rem;
    background: var(--surface-alt);
    border-radius: var(--radius-sm);
    padding: 0.3rem;
  }

  .auth-tab {
    flex: 1;
    display: inline-flex;
    align-items: center;
    justify-content: center;
    gap: 0.35rem;
    padding: 0.6rem 1rem;
    border: 0;
    border-radius: 6px;
    background: transparent;
    color: var(--text-muted);
    font-weight: 500;
    font-size: 0.85rem;
    cursor: pointer;
    transition: all 0.2s ease;
  }

  .auth-tab.active {
    background: var(--surface);
    color: var(--text);
    box-shadow: var(--shadow-sm);
  }

  .tab-icon {
    width: 15px;
    height: 15px;
  }

  .auth-form {
    display: grid;
    gap: 1rem;
  }

  .form-group {
    display: grid;
    gap: 0.4rem;
  }

  .form-group label {
    display: inline-flex;
    align-items: center;
    gap: 0.35rem;
    font-size: 0.8rem;
    font-weight: 600;
    color: var(--text-muted);
  }

  .field-icon {
    width: 13px;
    height: 13px;
  }

  .form-group input {
    width: 100%;
    border: 1.5px solid var(--border);
    border-radius: var(--radius-sm);
    padding: 0.7rem 0.85rem;
    background: var(--surface-alt);
    font-size: 0.9rem;
    transition: all 0.2s ease;
  }

  .form-group input:focus {
    outline: none;
    border-color: var(--primary);
    background: var(--surface);
    box-shadow: var(--shadow-glow);
  }

  .form-group input::placeholder {
    color: var(--text-light);
  }

  .btn-primary {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    gap: 0.45rem;
    width: 100%;
    padding: 0.8rem 1rem;
    border: 0;
    border-radius: var(--radius-sm);
    background: linear-gradient(135deg, var(--primary), #818cf8);
    color: white;
    font-weight: 600;
    font-size: 0.9rem;
    cursor: pointer;
    transition: all 0.2s ease;
    margin-top: 0.25rem;
    box-shadow: 0 2px 8px rgba(99, 102, 241, 0.3);
  }

  .btn-primary:hover:not(:disabled) {
    box-shadow: 0 4px 16px rgba(99, 102, 241, 0.4);
  }

  .btn-primary:disabled {
    opacity: 0.6;
    cursor: not-allowed;
  }

  .btn-icon {
    width: 16px;
    height: 16px;
  }

  @keyframes spin {
    to {
      transform: rotate(360deg);
    }
  }

  .spin {
    animation: spin 1s linear infinite;
  }

  .form-switch-enter-active,
  .form-switch-leave-active {
    transition: all 0.2s ease;
  }

  .form-switch-enter-from {
    opacity: 0;
    transform: translateY(8px);
  }

  .form-switch-leave-to {
    opacity: 0;
    transform: translateY(-8px);
  }
</style>
