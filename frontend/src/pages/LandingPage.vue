<script setup>
  import { inject } from 'vue'
  import { useStore } from '../composables/useStore'
  import AuthPanel from '../components/AuthPanel.vue'

  const { authBusy, handleLogin, handleRegister } = inject('app')
  const { language, toggleLanguage, t } = useStore()
</script>

<template>
  <div class="landing">
    <div class="landing-bg"></div>

    <nav class="landing-nav">
      <div class="landing-nav-inner">
        <div class="landing-brand">
          <div class="brand-icon">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z" />
              <polyline points="14 2 14 8 20 8" />
              <path d="M9 15l2 2 4-4" />
            </svg>
          </div>
          <span class="brand-name">{{ t('shell.appName') }}</span>
          <span class="brand-version">v1.5.3</span>
        </div>
        <div class="landing-nav-links">
          <a href="/docs" class="nav-link-top">{{ t('shell.apiDocs') }}</a>
          <a href="/redoc" class="nav-link-top">{{ t('shell.redoc') }}</a>
          <button class="lang-toggle" @click="toggleLanguage">
            {{ language === 'sl' ? 'EN' : 'SL' }}
          </button>
        </div>
      </div>
    </nav>

    <main class="landing-content">
      <div class="landing-grid">
        <div class="landing-hero">
          <span class="hero-chip">
            <svg
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              stroke-width="2"
              class="chip-icon"
            >
              <path d="M12 2L2 7l10 5 10-5-10-5z" />
              <path d="M2 17l10 5 10-5" />
              <path d="M2 12l10 5 10-5" />
            </svg>
            {{ t('landing.project') }}
          </span>
          <h1 class="landing-title">
            {{ t('landing.title1') }}<br />
            <span class="gradient-text">{{ t('landing.title2') }}</span
            ><br />
            {{ t('landing.title3') }}
          </h1>
          <p class="landing-desc">
            {{ t('landing.desc') }}
          </p>
          <div class="hero-panels">
            <div class="hero-panel">
              <span class="hero-panel-label">{{ t('landing.secureLabel') }}</span>
              <strong>{{ t('landing.secureTitle') }}</strong>
              <p>{{ t('landing.secureText') }}</p>
            </div>
            <div class="hero-panel">
              <span class="hero-panel-label">{{ t('landing.fastLabel') }}</span>
              <strong>{{ t('landing.fastTitle') }}</strong>
              <p>{{ t('landing.fastText') }}</p>
            </div>
          </div>
          <div class="feature-grid">
            <div class="feature-item">
              <span class="feature-dot dot-indigo"></span>{{ t('landing.jwtAuth') }}
            </div>
            <div class="feature-item">
              <span class="feature-dot dot-emerald"></span>{{ t('landing.minioStorage') }}
            </div>
            <div class="feature-item">
              <span class="feature-dot dot-amber"></span>{{ t('landing.aiSummaries') }}
            </div>
            <div class="feature-item">
              <span class="feature-dot dot-rose"></span>{{ t('landing.ragQa') }}
            </div>
            <div class="feature-item">
              <span class="feature-dot dot-sky"></span>{{ t('landing.adminPanel') }}
            </div>
            <div class="feature-item">
              <span class="feature-dot dot-violet"></span>{{ t('landing.prometheus') }}
            </div>
          </div>
          <div class="tech-chips">
            <span class="tech-chip">Vue 3</span>
            <span class="tech-chip">FastAPI</span>
            <span class="tech-chip">PostgreSQL</span>
            <span class="tech-chip">Docker</span>
            <span class="tech-chip">Groq AI</span>
            <span class="tech-chip">MinIO</span>
          </div>
          <div class="trust-strip">
            <span>{{ t('landing.previewPdf') }}</span>
            <span>{{ t('landing.userAdmin') }}</span>
            <span>{{ t('landing.multiUser') }}</span>
            <span>{{ t('landing.metrics') }}</span>
          </div>
        </div>

        <div class="landing-auth">
          <AuthPanel :busy="authBusy" @login="handleLogin" @register="handleRegister" />
        </div>
      </div>
    </main>

    <footer class="landing-footer">
      <span>{{ t('shell.appName') }} v1.5.3</span>
      <span class="footer-dot">&middot;</span>
      <span>{{ t('shell.footerSchool') }}</span>
      <span class="footer-dot">&middot;</span>
      <a href="/docs" class="footer-link">{{ t('shell.apiDocs') }}</a>
    </footer>
  </div>
</template>

<style scoped>
  .landing {
    min-height: 100vh;
    display: flex;
    flex-direction: column;
    position: relative;
  }

  .landing-bg {
    position: fixed;
    inset: 0;
    background:
      radial-gradient(ellipse at 25% 0%, rgba(99, 102, 241, 0.1) 0%, transparent 50%),
      radial-gradient(ellipse at 75% 100%, rgba(16, 185, 129, 0.08) 0%, transparent 50%);
    pointer-events: none;
    z-index: 0;
  }

  .landing-nav {
    position: sticky;
    top: 0;
    z-index: 20;
    background: var(--panel-bg-strong);
    backdrop-filter: blur(14px);
    border-bottom: 1px solid var(--border-subtle);
  }

  .landing-nav-inner {
    display: flex;
    align-items: center;
    justify-content: space-between;
    max-width: 1200px;
    margin: 0 auto;
    padding: 0.7rem 2rem;
  }

  .landing-brand {
    display: flex;
    align-items: center;
    gap: 0.6rem;
  }

  .brand-icon {
    width: 34px;
    height: 34px;
    background: linear-gradient(135deg, var(--primary), #818cf8);
    border-radius: 10px;
    display: flex;
    align-items: center;
    justify-content: center;
    color: white;
  }
  .brand-icon svg {
    width: 17px;
    height: 17px;
  }

  .brand-name {
    font-weight: 700;
    font-size: 0.95rem;
    color: var(--text);
  }

  .brand-version {
    font-size: 0.65rem;
    font-weight: 600;
    padding: 0.15rem 0.45rem;
    background: var(--primary-light);
    color: var(--primary);
    border-radius: 999px;
  }

  .landing-nav-links {
    display: flex;
    gap: 0.75rem;
    align-items: center;
  }

  .nav-link-top {
    font-size: 0.82rem;
    font-weight: 500;
    color: var(--text-muted);
    text-decoration: none;
    padding: 0.35rem 0.65rem;
    border-radius: var(--radius-sm);
    transition: all 0.15s;
  }
  .nav-link-top:hover {
    background: var(--surface-alt);
    color: var(--text);
  }

  .lang-toggle {
    border: 1px solid var(--border-subtle);
    background: var(--panel-bg-soft);
    color: var(--text-muted);
    border-radius: 999px;
    padding: 0.35rem 0.7rem;
    font-size: 0.78rem;
    font-weight: 700;
  }

  .landing-content {
    flex: 1;
    display: flex;
    align-items: center;
    position: relative;
    z-index: 1;
  }

  .landing-grid {
    display: grid;
    grid-template-columns: 1fr 420px;
    gap: 4rem;
    align-items: center;
    max-width: 1200px;
    margin: 0 auto;
    padding: 3rem 2rem;
    width: 100%;
  }

  .hero-chip {
    display: inline-flex;
    align-items: center;
    gap: 0.4rem;
    padding: 0.4rem 0.9rem;
    background: var(--primary-light);
    color: var(--primary);
    border-radius: 999px;
    font-size: 0.73rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    border: 1px solid rgba(99, 102, 241, 0.12);
    margin-bottom: 1.5rem;
  }
  .chip-icon {
    width: 14px;
    height: 14px;
  }

  .landing-title {
    margin: 0 0 1.25rem;
    font-size: clamp(2.6rem, 5vw, 3.6rem);
    font-weight: 800;
    line-height: 1.06;
    color: var(--text);
    letter-spacing: -0.03em;
  }

  .gradient-text {
    background: linear-gradient(135deg, var(--primary), #818cf8, var(--accent));
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
  }

  .landing-desc {
    margin: 0 0 2rem;
    font-size: 1.08rem;
    line-height: 1.75;
    color: var(--text-muted);
    max-width: 48ch;
  }

  .hero-panels {
    display: grid;
    grid-template-columns: repeat(2, minmax(0, 1fr));
    gap: 0.85rem;
    margin-bottom: 1.4rem;
  }

  .hero-panel {
    padding: 1rem 1.05rem;
    background: var(--panel-bg);
    border: 1px solid var(--panel-border);
    border-radius: 18px;
    box-shadow: var(--shadow-sm);
  }

  .hero-panel-label {
    display: inline-block;
    margin-bottom: 0.45rem;
    font-size: 0.68rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    color: var(--primary);
  }

  .hero-panel strong {
    display: block;
    margin-bottom: 0.35rem;
    font-size: 0.92rem;
    color: var(--text);
  }

  .hero-panel p {
    margin: 0;
    font-size: 0.8rem;
    line-height: 1.55;
    color: var(--text-muted);
  }

  .feature-grid {
    display: grid;
    grid-template-columns: repeat(3, auto);
    gap: 0.5rem 1rem;
    margin-bottom: 1.5rem;
  }
  .feature-item {
    display: flex;
    align-items: center;
    gap: 0.4rem;
    font-size: 0.82rem;
    font-weight: 500;
    color: var(--text-muted);
  }
  .feature-dot {
    width: 7px;
    height: 7px;
    border-radius: 50%;
    flex-shrink: 0;
  }
  .dot-indigo {
    background: var(--primary);
  }
  .dot-emerald {
    background: var(--accent);
  }
  .dot-amber {
    background: var(--warning);
  }
  .dot-rose {
    background: var(--danger);
  }
  .dot-sky {
    background: #0ea5e9;
  }
  .dot-violet {
    background: #8b5cf6;
  }

  .tech-chips {
    display: flex;
    flex-wrap: wrap;
    gap: 0.4rem;
  }
  .tech-chip {
    padding: 0.22rem 0.6rem;
    background: var(--surface-alt);
    border: 1px solid var(--border-subtle);
    border-radius: var(--radius-sm);
    font-size: 0.7rem;
    font-weight: 600;
    color: var(--text-light);
  }

  .trust-strip {
    display: flex;
    flex-wrap: wrap;
    gap: 0.55rem;
    margin-top: 1.2rem;
  }

  .trust-strip span {
    padding: 0.35rem 0.65rem;
    border-radius: 999px;
    background: var(--panel-bg-soft);
    border: 1px solid var(--border-subtle);
    font-size: 0.74rem;
    font-weight: 600;
    color: var(--text-muted);
  }

  .landing-auth {
    position: sticky;
    top: 72px;
  }

  .landing-footer {
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 0.5rem;
    padding: 1rem 2rem;
    border-top: 1px solid var(--border);
    font-size: 0.75rem;
    color: var(--text-light);
    background: var(--surface);
    position: relative;
    z-index: 1;
  }

  .footer-dot {
    color: var(--border);
  }
  .footer-link {
    color: var(--primary);
    text-decoration: none;
    font-weight: 500;
  }
  .footer-link:hover {
    text-decoration: underline;
  }

  @media (max-width: 860px) {
    .landing-grid {
      grid-template-columns: 1fr;
      gap: 2.5rem;
      padding: 2rem 1.5rem;
    }
    .landing-auth {
      position: static;
    }
    .hero-panels {
      grid-template-columns: 1fr;
    }
    .landing-title {
      font-size: 2.2rem;
    }
    .feature-grid {
      grid-template-columns: repeat(2, auto);
    }
  }

  @media (max-width: 540px) {
    .landing-grid {
      padding: 1.5rem 1rem;
    }
    .landing-title {
      font-size: 1.7rem;
    }
    .landing-desc {
      font-size: 0.9rem;
    }
    .feature-grid {
      grid-template-columns: 1fr;
    }
    .tech-chips {
      justify-content: center;
    }
    .landing-nav-inner {
      padding: 0 1rem;
    }
    .landing-nav-links {
      display: none;
    }
    .landing-footer {
      flex-wrap: wrap;
      gap: 0.25rem;
      justify-content: center;
    }
  }
</style>
