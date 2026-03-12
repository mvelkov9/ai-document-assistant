<script setup>
  import { onMounted, provide } from 'vue'
  import { useRoute, useRouter } from 'vue-router'
  import { useStore } from './composables/useStore'

  const route = useRoute()
  const router = useRouter()
  const store = useStore()

  const {
    isAuthenticated,
    isAdmin,
    currentUser,
    documents,
    summaryCount,
    globalMessage,
    globalError,
    sidebarCollapsed,
    darkMode,
    authBusy,
    handleLogin,
    handleRegister,
    toggleDarkMode,
    logout: storeLogout,
    bootstrapSession,
  } = store

  /* Provide store slices for child pages (e.g. LandingPage needs auth handlers) */
  async function loginAndRedirect(form) {
    const ok = await handleLogin(form)
    if (ok) router.push('/documents')
  }
  provide('app', { authBusy, handleLogin: loginAndRedirect, handleRegister })

  function handleLogout() {
    storeLogout()
    router.push('/')
  }

  /* Page metadata driven by current route */
  const pageMeta = {
    documents: { title: 'Dokumenti', subtitle: 'Pregled, iskanje in upravljanje dokumentov' },
    upload: { title: 'Naloži dokument', subtitle: 'PDF datoteke do 15 MB' },
    profile: { title: 'Uporabniški profil', subtitle: 'Podatki o tvojem računu' },
    admin: { title: 'Administracija', subtitle: 'Sistemske statistike in uporabniki' },
  }

  onMounted(async () => {
    await bootstrapSession()
  })
</script>

<template>
  <div class="app-shell">
    <!-- ════════════ GUEST LAYOUT (landing etc.) ════════════ -->
    <template v-if="!isAuthenticated">
      <router-view />
    </template>

    <!-- ════════════ AUTHENTICATED SHELL ════════════ -->
    <template v-else>
      <div class="shell">
        <!-- ── Sidebar ── -->
        <aside class="sidebar" :class="{ collapsed: sidebarCollapsed }">
          <div class="sidebar-header">
            <div class="sidebar-brand" v-if="!sidebarCollapsed">
              <div class="sb-icon">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z" />
                  <polyline points="14 2 14 8 20 8" />
                  <path d="M9 15l2 2 4-4" />
                </svg>
              </div>
              <div class="sb-text">
                <span class="sb-name">DocAssist</span>
                <span class="sb-ver">v1.4.0</span>
              </div>
            </div>
            <button
              class="sidebar-toggle"
              @click="sidebarCollapsed = !sidebarCollapsed"
              :title="sidebarCollapsed ? 'Razširi' : 'Skrči'"
            >
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <line x1="3" y1="12" x2="21" y2="12" />
                <line x1="3" y1="6" x2="21" y2="6" />
                <line x1="3" y1="18" x2="21" y2="18" />
              </svg>
            </button>
          </div>

          <nav class="sidebar-nav">
            <router-link to="/documents" class="nav-item" active-class="active">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z" />
                <polyline points="14 2 14 8 20 8" />
              </svg>
              <span class="nav-label" v-if="!sidebarCollapsed">Dokumenti</span>
              <span class="nav-badge" v-if="!sidebarCollapsed && documents.length">{{
                documents.length
              }}</span>
            </router-link>
            <router-link to="/upload" class="nav-item" active-class="active">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4" />
                <polyline points="17 8 12 3 7 8" />
                <line x1="12" y1="3" x2="12" y2="15" />
              </svg>
              <span class="nav-label" v-if="!sidebarCollapsed">Naloži</span>
            </router-link>
            <router-link to="/profile" class="nav-item" active-class="active">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2" />
                <circle cx="12" cy="7" r="4" />
              </svg>
              <span class="nav-label" v-if="!sidebarCollapsed">Profil</span>
            </router-link>
            <router-link v-if="isAdmin" to="/admin" class="nav-item" active-class="active">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z" />
              </svg>
              <span class="nav-label" v-if="!sidebarCollapsed">Admin</span>
            </router-link>

            <div v-if="isAdmin && !sidebarCollapsed" class="nav-divider"></div>
            <span v-if="isAdmin && !sidebarCollapsed" class="nav-section-label">Orodja</span>

            <a v-if="isAdmin" href="/docs" target="_blank" class="nav-item nav-item-ext">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z" />
                <polyline points="14 2 14 8 20 8" />
                <line x1="16" y1="13" x2="8" y2="13" />
                <line x1="16" y1="17" x2="8" y2="17" />
                <polyline points="10 9 9 9 8 9" />
              </svg>
              <span class="nav-label" v-if="!sidebarCollapsed">API Docs</span>
              <svg
                v-if="!sidebarCollapsed"
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                stroke-width="2"
                class="ext-icon"
              >
                <path d="M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6" />
                <polyline points="15 3 21 3 21 9" />
                <line x1="10" y1="14" x2="21" y2="3" />
              </svg>
            </a>
            <a v-if="isAdmin" href="/redoc" target="_blank" class="nav-item nav-item-ext">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M2 3h6a4 4 0 0 1 4 4v14a3 3 0 0 0-3-3H2z" />
                <path d="M22 3h-6a4 4 0 0 0-4 4v14a3 3 0 0 1 3-3h7z" />
              </svg>
              <span class="nav-label" v-if="!sidebarCollapsed">ReDoc</span>
              <svg
                v-if="!sidebarCollapsed"
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                stroke-width="2"
                class="ext-icon"
              >
                <path d="M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6" />
                <polyline points="15 3 21 3 21 9" />
                <line x1="10" y1="14" x2="21" y2="3" />
              </svg>
            </a>
          </nav>

          <div class="sidebar-bottom">
            <div class="sidebar-user" v-if="!sidebarCollapsed">
              <div class="user-avatar-sm">
                {{ currentUser.full_name?.charAt(0)?.toUpperCase() }}
              </div>
              <div class="user-meta">
                <span class="user-name-sm">{{ currentUser.full_name }}</span>
                <span class="user-role-sm" :class="'role-' + currentUser.role">{{
                  currentUser.role
                }}</span>
              </div>
            </div>
            <button class="nav-item nav-item-theme" @click="toggleDarkMode" :title="darkMode ? 'Svetli način' : 'Temni način'">
              <svg v-if="darkMode" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <circle cx="12" cy="12" r="5" />
                <line x1="12" y1="1" x2="12" y2="3" />
                <line x1="12" y1="21" x2="12" y2="23" />
                <line x1="4.22" y1="4.22" x2="5.64" y2="5.64" />
                <line x1="18.36" y1="18.36" x2="19.78" y2="19.78" />
                <line x1="1" y1="12" x2="3" y2="12" />
                <line x1="21" y1="12" x2="23" y2="12" />
                <line x1="4.22" y1="19.78" x2="5.64" y2="18.36" />
                <line x1="18.36" y1="5.64" x2="19.78" y2="4.22" />
              </svg>
              <svg v-else viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z" />
              </svg>
              <span class="nav-label" v-if="!sidebarCollapsed">{{ darkMode ? 'Svetli način' : 'Temni način' }}</span>
            </button>
            <button class="nav-item nav-item-logout" @click="handleLogout">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4" />
                <polyline points="16 17 21 12 16 7" />
                <line x1="21" y1="12" x2="9" y2="12" />
              </svg>
              <span class="nav-label" v-if="!sidebarCollapsed">Odjava</span>
            </button>
          </div>
        </aside>

        <!-- ── Main Content ── -->
        <main class="main">
          <!-- Top bar -->
          <header class="topbar">
            <div class="topbar-left">
              <h1 class="page-title">
                {{ pageMeta[route.name]?.title || '' }}
              </h1>
              <p class="page-subtitle">
                {{ pageMeta[route.name]?.subtitle || '' }}
              </p>
            </div>
            <div class="topbar-stats">
              <div class="mini-stat">
                <span class="mini-stat-num">{{ documents.length }}</span>
                <span class="mini-stat-lbl">Dokumentov</span>
              </div>
              <div class="mini-stat">
                <span class="mini-stat-num">{{ summaryCount }}</span>
                <span class="mini-stat-lbl">Povzetkov</span>
              </div>
            </div>
          </header>

          <!-- Routed page content -->
          <router-view />

          <!-- Footer -->
          <footer class="main-footer">
            <span>AI Document Assistant v1.4.0</span>
            <span class="footer-dot">&middot;</span>
            <span>ALMA MATER EUROPAEA 2025/26</span>
            <span class="footer-dot">&middot;</span>
            <a href="/docs" class="footer-link">API Docs</a>
            <span class="footer-dot">&middot;</span>
            <a href="/redoc" class="footer-link">ReDoc</a>
          </footer>
        </main>
      </div>
    </template>

    <!-- ── Toasts ── -->
    <Transition name="toast">
      <div v-if="globalMessage" class="toast toast-ok" @click="globalMessage = ''">
        <div class="toast-accent accent-ok"></div>
        <svg
          viewBox="0 0 24 24"
          fill="none"
          stroke="currentColor"
          stroke-width="2"
          class="toast-svg"
        >
          <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14" />
          <polyline points="22 4 12 14.01 9 11.01" />
        </svg>
        <span>{{ globalMessage }}</span>
        <button class="toast-x" @click.stop="globalMessage = ''">&times;</button>
      </div>
    </Transition>
    <Transition name="toast">
      <div v-if="globalError" class="toast toast-err" @click="globalError = ''">
        <div class="toast-accent accent-err"></div>
        <svg
          viewBox="0 0 24 24"
          fill="none"
          stroke="currentColor"
          stroke-width="2"
          class="toast-svg"
        >
          <circle cx="12" cy="12" r="10" />
          <line x1="15" y1="9" x2="9" y2="15" />
          <line x1="9" y1="9" x2="15" y2="15" />
        </svg>
        <span>{{ globalError }}</span>
        <button class="toast-x" @click.stop="globalError = ''">&times;</button>
      </div>
    </Transition>
  </div>
</template>

<style scoped>
  /* ═══════════════════ SHELL (sidebar + main) ═══════════════════ */
  .shell {
    display: flex;
    min-height: 100vh;
  }

  /* ── Sidebar ── */
  .sidebar {
    width: 256px;
    background: #1a1d23;
    color: #e2e8ef;
    display: flex;
    flex-direction: column;
    flex-shrink: 0;
    transition: width 0.25s cubic-bezier(0.4, 0, 0.2, 1);
    position: sticky;
    top: 0;
    height: 100vh;
    overflow-y: auto;
    z-index: 30;
  }

  .sidebar.collapsed {
    width: 64px;
  }

  .sidebar-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 1rem;
    border-bottom: 1px solid rgba(255, 255, 255, 0.07);
    min-height: 60px;
  }

  .sidebar-brand {
    display: flex;
    align-items: center;
    gap: 0.6rem;
  }

  .sb-icon {
    width: 32px;
    height: 32px;
    background: linear-gradient(135deg, var(--primary), #818cf8);
    border-radius: 8px;
    display: flex;
    align-items: center;
    justify-content: center;
    flex-shrink: 0;
  }

  .sb-icon svg {
    width: 16px;
    height: 16px;
    color: white;
  }

  .sb-text {
    display: flex;
    flex-direction: column;
    line-height: 1.2;
  }

  .sb-name {
    font-weight: 700;
    font-size: 0.88rem;
  }
  .sb-ver {
    font-size: 0.62rem;
    color: #8b92a0;
  }

  .sidebar-toggle {
    width: 32px;
    height: 32px;
    border: none;
    background: rgba(255, 255, 255, 0.06);
    border-radius: 6px;
    color: #8b92a0;
    display: flex;
    align-items: center;
    justify-content: center;
    flex-shrink: 0;
  }

  .sidebar-toggle svg {
    width: 16px;
    height: 16px;
  }
  .sidebar-toggle:hover {
    background: rgba(255, 255, 255, 0.12);
    color: #e2e8ef;
  }

  .sidebar-nav {
    flex: 1;
    padding: 0.75rem 0.5rem;
    display: flex;
    flex-direction: column;
    gap: 0.2rem;
  }

  .nav-item {
    display: flex;
    align-items: center;
    gap: 0.7rem;
    padding: 0.6rem 0.85rem;
    border: none;
    background: transparent;
    color: #8b92a0;
    border-radius: 8px;
    font-size: 0.85rem;
    font-weight: 500;
    transition: all 0.15s;
    width: 100%;
    text-align: left;
  }

  .nav-item svg {
    width: 18px;
    height: 18px;
    flex-shrink: 0;
  }

  .nav-item:hover {
    background: rgba(255, 255, 255, 0.06);
    color: #e2e8ef;
  }

  .nav-item.active {
    background: rgba(99, 102, 241, 0.15);
    color: #a5b4fc;
  }

  .nav-badge {
    margin-left: auto;
    background: rgba(99, 102, 241, 0.2);
    color: #a5b4fc;
    font-size: 0.7rem;
    font-weight: 700;
    padding: 0.12rem 0.5rem;
    border-radius: 999px;
  }

  .nav-divider {
    height: 1px;
    background: rgba(255, 255, 255, 0.07);
    margin: 0.5rem 0.85rem;
  }

  .nav-section-label {
    display: block;
    padding: 0.2rem 0.85rem 0.4rem;
    font-size: 0.62rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    color: #5a6070;
  }

  .nav-item-ext {
    text-decoration: none;
  }

  .ext-icon {
    width: 12px;
    height: 12px;
    margin-left: auto;
    opacity: 0.5;
  }

  .sidebar-bottom {
    padding: 0.75rem 0.5rem;
    border-top: 1px solid rgba(255, 255, 255, 0.07);
  }

  .sidebar-user {
    display: flex;
    align-items: center;
    gap: 0.6rem;
    padding: 0.5rem 0.85rem;
    margin-bottom: 0.25rem;
  }

  .user-avatar-sm {
    width: 30px;
    height: 30px;
    border-radius: 50%;
    background: linear-gradient(135deg, var(--primary), #818cf8);
    color: white;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 0.72rem;
    font-weight: 700;
    flex-shrink: 0;
  }

  .user-meta {
    display: flex;
    flex-direction: column;
    line-height: 1.2;
    min-width: 0;
  }

  .user-name-sm {
    font-size: 0.8rem;
    font-weight: 600;
    color: #e2e8ef;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
  }

  .user-role-sm {
    font-size: 0.62rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.04em;
  }

  .role-admin {
    color: #fbbf24;
  }
  .role-user {
    color: #8b92a0;
  }

  .nav-item-theme {
    color: #a78bfa;
  }
  .nav-item-theme:hover {
    background: rgba(167, 139, 250, 0.12);
    color: #c4b5fd;
  }

  .nav-item-logout {
    color: #ef4444;
  }
  .nav-item-logout:hover {
    background: rgba(239, 68, 68, 0.12);
    color: #f87171;
  }

  /* ── Main Area ── */
  .main {
    flex: 1;
    display: flex;
    flex-direction: column;
    min-height: 100vh;
    background: var(--bg);
    overflow-x: hidden;
  }

  /* ── Topbar ── */
  .topbar {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 1.25rem 2rem;
    background: var(--surface);
    border-bottom: 1px solid var(--border);
    position: sticky;
    top: 0;
    z-index: 10;
  }

  .page-title {
    margin: 0;
    font-size: 1.4rem;
    font-weight: 700;
    color: var(--text);
    letter-spacing: -0.02em;
  }

  .page-subtitle {
    margin: 0.15rem 0 0;
    font-size: 0.85rem;
    color: var(--text-muted);
  }

  .topbar-stats {
    display: flex;
    gap: 0.75rem;
  }

  .mini-stat {
    display: flex;
    flex-direction: column;
    align-items: center;
    padding: 0.4rem 1rem;
    background: var(--surface-alt);
    border: 1px solid var(--border-subtle);
    border-radius: var(--radius);
    min-width: 72px;
  }

  .mini-stat-num {
    font-size: 1.15rem;
    font-weight: 800;
    color: var(--primary);
    line-height: 1;
  }

  .mini-stat-lbl {
    font-size: 0.62rem;
    font-weight: 500;
    text-transform: uppercase;
    letter-spacing: 0.04em;
    color: var(--text-light);
    margin-top: 0.1rem;
  }

  /* ── Main Footer ── */
  .main-footer {
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 0.5rem;
    padding: 1rem 2rem;
    border-top: 1px solid var(--border);
    font-size: 0.75rem;
    color: var(--text-light);
    margin-top: auto;
    background: var(--surface);
  }

  /* ── Toasts ── */
  .toast {
    position: fixed;
    bottom: 1.5rem;
    right: 1.5rem;
    display: flex;
    align-items: center;
    gap: 0.6rem;
    padding: 0.85rem 1.2rem;
    border-radius: var(--radius);
    font-size: 0.86rem;
    font-weight: 500;
    z-index: 200;
    cursor: pointer;
    box-shadow: var(--shadow-lg);
    max-width: 420px;
    background: var(--surface);
    border: 1px solid var(--border);
    color: var(--text);
    overflow: hidden;
  }

  .toast-accent {
    position: absolute;
    left: 0;
    top: 0;
    bottom: 0;
    width: 4px;
  }

  .accent-ok {
    background: var(--accent);
  }
  .accent-err {
    background: var(--danger);
  }

  .toast-ok .toast-svg {
    color: var(--accent);
  }
  .toast-err .toast-svg {
    color: var(--danger);
  }

  .toast-svg {
    width: 18px;
    height: 18px;
    flex-shrink: 0;
  }

  .toast-x {
    margin-left: auto;
    background: none;
    border: none;
    font-size: 1.15rem;
    color: var(--text-light);
    padding: 0 0 0 0.4rem;
    line-height: 1;
  }
  .toast-x:hover {
    color: var(--text);
    transform: none;
  }

  .toast-enter-active,
  .toast-leave-active {
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  }
  .toast-enter-from {
    opacity: 0;
    transform: translateX(2rem);
  }
  .toast-leave-to {
    opacity: 0;
    transform: translateY(1rem);
  }

  /* ── List transitions ── */
  .list-enter-active,
  .list-leave-active {
    transition: all 0.3s ease;
  }
  .list-enter-from {
    opacity: 0;
    transform: translateY(-8px);
  }
  .list-leave-to {
    opacity: 0;
    transform: translateX(20px);
  }
  .list-move {
    transition: transform 0.3s ease;
  }

  @keyframes spin {
    to {
      transform: rotate(360deg);
    }
  }
  .spin {
    animation: spin 1s linear infinite;
  }

  /* ── Responsive ── */
  @media (max-width: 860px) {
    .sidebar {
      position: fixed;
      left: 0;
      top: 0;
      bottom: 0;
      width: 256px;
      transform: translateX(-100%);
      transition: transform 0.25s ease;
    }

    .sidebar:not(.collapsed) {
      transform: translateX(0);
    }

    .topbar {
      padding: 1rem 1.25rem;
    }
  }

  @media (max-width: 540px) {
    .topbar-stats {
      display: none;
    }
  }
</style>
