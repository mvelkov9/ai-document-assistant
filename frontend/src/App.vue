<script setup>
import { computed, onMounted, reactive, ref } from 'vue'

import AuthPanel from './components/AuthPanel.vue'
import DocumentCard from './components/DocumentCard.vue'
import UploadSection from './components/UploadSection.vue'

import {
  createQuestionJob,
  createSummaryJob,
  deleteDocument,
  downloadDocument,
  getAdminStats,
  getAdminUsers,
  getJobStatus,
  getCurrentUser,
  listDocuments,
  loginUser,
  registerUser,
  setUserRole,
  uploadDocument,
} from './lib/api'

const TOKEN_KEY = 'docassist-token'

/* ── State ── */
const sessionToken = ref(localStorage.getItem(TOKEN_KEY) || '')
const currentUser = ref(null)
const documents = ref([])
const globalMessage = ref('')
const globalError = ref('')
const authBusy = ref(false)
const dashboardBusy = ref(false)
const uploadBusy = ref(false)
const activeSummaryId = ref('')
const activeQuestionId = ref('')
const latestAnswers = reactive({})
const searchQuery = ref('')
const sortField = ref('date')
const adminStats = ref(null)
const adminUsers = ref([])
const sidebarCollapsed = ref(false)
const currentPage = ref('documents')

/* ── Computed ── */
const isAuthenticated = computed(() => Boolean(sessionToken.value && currentUser.value))
const isAdmin = computed(() => currentUser.value?.role === 'admin')

const filteredDocuments = computed(() => {
  let docs = [...documents.value]
  const q = searchQuery.value.trim().toLowerCase()
  if (q) docs = docs.filter(d => d.original_filename.toLowerCase().includes(q))
  if (sortField.value === 'name') docs.sort((a, b) => a.original_filename.localeCompare(b.original_filename))
  else if (sortField.value === 'size') docs.sort((a, b) => b.size_bytes - a.size_bytes)
  else if (sortField.value === 'status') docs.sort((a, b) => a.processing_status.localeCompare(b.processing_status))
  else docs.sort((a, b) => new Date(b.created_at) - new Date(a.created_at))
  return docs
})

const summaryCount = computed(() => documents.value.filter(d => d.summary_text).length)

/* ── Helpers ── */
function setMessage(msg) { globalError.value = ''; globalMessage.value = msg }
function setError(msg) { globalMessage.value = ''; globalError.value = msg }
function persistToken(token) { sessionToken.value = token; localStorage.setItem(TOKEN_KEY, token) }
function clearSession() { sessionToken.value = ''; currentUser.value = null; documents.value = []; localStorage.removeItem(TOKEN_KEY) }

/* ── API actions ── */
async function refreshDocuments() {
  if (!sessionToken.value) return
  dashboardBusy.value = true
  try { const r = await listDocuments(sessionToken.value); documents.value = r.items || [] }
  catch (e) { setError(e.message) }
  finally { dashboardBusy.value = false }
}

async function bootstrapSession() {
  if (!sessionToken.value) return
  dashboardBusy.value = true
  try {
    currentUser.value = await getCurrentUser(sessionToken.value)
    await refreshDocuments()
    if (isAdmin.value) await loadAdminData()
  } catch { clearSession() }
  finally { dashboardBusy.value = false }
}

async function loadAdminData() {
  try {
    adminStats.value = await getAdminStats(sessionToken.value)
    adminUsers.value = await getAdminUsers(sessionToken.value)
  } catch { /* may fail for non-admin */ }
}

async function handleLogin(form) {
  authBusy.value = true
  try {
    const tp = await loginUser(form)
    persistToken(tp.access_token)
    currentUser.value = await getCurrentUser(sessionToken.value)
    await refreshDocuments()
    if (isAdmin.value) await loadAdminData()
    setMessage('Prijava je uspela.')
  } catch (e) { setError(e.message) }
  finally { authBusy.value = false }
}

async function handleRegister(form) {
  authBusy.value = true
  try { await registerUser(form); setMessage('Registracija je uspela. Zdaj se prijavi z novim računom.') }
  catch (e) { setError(e.message) }
  finally { authBusy.value = false }
}

async function handleUpload(file) {
  uploadBusy.value = true
  try { await uploadDocument(sessionToken.value, file); await refreshDocuments(); setMessage('Dokument je bil uspešno naložen.'); currentPage.value = 'documents' }
  catch (e) { setError(e.message) }
  finally { uploadBusy.value = false }
}

async function pollJob(jobId, maxAttempts = 15) {
  for (let i = 0; i < maxAttempts; i++) {
    const job = await getJobStatus(sessionToken.value, jobId)
    if (job.status === 'completed') return job
    if (job.status === 'failed') throw new Error(job.error_message || 'Job failed.')
    await new Promise(r => setTimeout(r, 1200))
  }
  return null
}

async function handleSummarize(documentId) {
  activeSummaryId.value = documentId
  try {
    const job = await createSummaryJob(sessionToken.value, documentId)
    const result = await pollJob(job.id)
    await refreshDocuments()
    setMessage(result ? 'Povzetek je bil generiran.' : 'Job se v teku. Osveži pozneje.')
  } catch (e) { setError(e.message) }
  finally { activeSummaryId.value = '' }
}

async function handleAsk(documentId, question) {
  activeQuestionId.value = documentId
  try {
    const job = await createQuestionJob(sessionToken.value, documentId, question)
    const result = await pollJob(job.id)
    if (result) {
      latestAnswers[documentId] = {
        question_text: result.job_input || question,
        answer_text: result.result_text || 'Odgovor generiran brez vsebine.',
        source_mode: 'async-job',
      }
    }
    await refreshDocuments()
    setMessage(result ? 'Odgovor je bil generiran.' : 'Job se v teku. Osveži pozneje.')
  } catch (e) { setError(e.message) }
  finally { activeQuestionId.value = '' }
}

function logout() { clearSession(); currentPage.value = 'documents'; setMessage('Odjava je bila uspešna.') }

async function handleDelete(documentId) {
  try { await deleteDocument(sessionToken.value, documentId); delete latestAnswers[documentId]; await refreshDocuments(); setMessage('Dokument je bil izbrisan.') }
  catch (e) { setError(e.message) }
}

async function handleDownload(documentId, filename) {
  try { await downloadDocument(sessionToken.value, documentId, filename) }
  catch (e) { setError(e.message) }
}

async function handleSetRole(userId, role) {
  try {
    await setUserRole(sessionToken.value, userId, role)
    await loadAdminData()
    setMessage(`Vloga uporabnika je bila spremenjena na "${role}".`)
  } catch (e) { setError(e.message) }
}

function formatDate(iso) {
  if (!iso) return ''
  return new Date(iso).toLocaleDateString('sl-SI', { day: 'numeric', month: 'short', year: 'numeric' })
}

onMounted(() => bootstrapSession())
</script>

<template>
  <div class="app-shell">
    <!-- ════════════════════ LANDING (not authenticated) ════════════════════ -->
    <template v-if="!isAuthenticated">
      <div class="landing">
        <div class="landing-bg"></div>

        <nav class="landing-nav">
          <div class="landing-nav-inner">
            <div class="landing-brand">
              <div class="brand-icon">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/><path d="M9 15l2 2 4-4"/></svg>
              </div>
              <span class="brand-name">AI Document Assistant</span>
              <span class="brand-version">v1.2.1</span>
            </div>
            <div class="landing-nav-links">
              <a href="/docs" class="nav-link-top">API Docs</a>
              <a href="/redoc" class="nav-link-top">ReDoc</a>
            </div>
          </div>
        </nav>

        <main class="landing-content">
          <div class="landing-grid">
            <div class="landing-hero">
              <span class="hero-chip">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" class="chip-icon"><path d="M12 2L2 7l10 5 10-5-10-5z"/><path d="M2 17l10 5 10-5"/><path d="M2 12l10 5 10-5"/></svg>
                Projektna naloga 2025/26 -  Integracija spletnih strani in servisi
              </span>
              <h1 class="landing-title">
                Pametni<br>
                <span class="gradient-text">Dokumentni</span><br>
                Pomočnik
              </h1>
              <p class="landing-desc">
                Varno naloži PDF dokumente, generiraj AI povzetke in postavljaj
                vprašanja nad vsebino dokumentov.
              </p>
              <div class="feature-grid">
                <div class="feature-item"><span class="feature-dot dot-indigo"></span>JWT avtentikacija</div>
                <div class="feature-item"><span class="feature-dot dot-emerald"></span>MinIO hramba</div>
                <div class="feature-item"><span class="feature-dot dot-amber"></span>AI povzetki (Groq)</div>
                <div class="feature-item"><span class="feature-dot dot-rose"></span>RAG-lite Q&amp;A</div>
                <div class="feature-item"><span class="feature-dot dot-sky"></span>Admin panel</div>
                <div class="feature-item"><span class="feature-dot dot-violet"></span>Prometheus</div>
              </div>
              <div class="tech-chips">
                <span class="tech-chip">Vue 3</span>
                <span class="tech-chip">FastAPI</span>
                <span class="tech-chip">PostgreSQL</span>
                <span class="tech-chip">Docker</span>
                <span class="tech-chip">Groq AI</span>
                <span class="tech-chip">MinIO</span>
              </div>
            </div>

            <div class="landing-auth">
              <AuthPanel :busy="authBusy" @login="handleLogin" @register="handleRegister" />
            </div>
          </div>
        </main>

        <footer class="landing-footer">
          <span>AI Document Assistant v1.2.1</span>
          <span class="footer-dot">&middot;</span>
          <span>ALMA MATER EUROPAEA 2025/26</span>
          <span class="footer-dot">&middot;</span>
          <a href="/docs" class="footer-link">API Docs</a>
        </footer>
      </div>
    </template>

    <!-- ════════════════════ AUTHENTICATED SHELL ════════════════════ -->
    <template v-else>
      <div class="shell">
        <!-- ── Sidebar ── -->
        <aside class="sidebar" :class="{ collapsed: sidebarCollapsed }">
          <div class="sidebar-header">
            <div class="sidebar-brand" v-if="!sidebarCollapsed">
              <div class="sb-icon">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/><path d="M9 15l2 2 4-4"/></svg>
              </div>
              <div class="sb-text">
                <span class="sb-name">DocAssist</span>
                <span class="sb-ver">v1.2.1</span>
              </div>
            </div>
            <button class="sidebar-toggle" @click="sidebarCollapsed = !sidebarCollapsed" :title="sidebarCollapsed ? 'Razširi' : 'Skrči'">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="3" y1="12" x2="21" y2="12"/><line x1="3" y1="6" x2="21" y2="6"/><line x1="3" y1="18" x2="21" y2="18"/></svg>
            </button>
          </div>

          <nav class="sidebar-nav">
            <button class="nav-item" :class="{ active: currentPage === 'documents' }" @click="currentPage = 'documents'">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/></svg>
              <span class="nav-label" v-if="!sidebarCollapsed">Dokumenti</span>
              <span class="nav-badge" v-if="!sidebarCollapsed && documents.length">{{ documents.length }}</span>
            </button>
            <button class="nav-item" :class="{ active: currentPage === 'upload' }" @click="currentPage = 'upload'">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="17 8 12 3 7 8"/><line x1="12" y1="3" x2="12" y2="15"/></svg>
              <span class="nav-label" v-if="!sidebarCollapsed">Naloži</span>
            </button>
            <button class="nav-item" :class="{ active: currentPage === 'profile' }" @click="currentPage = 'profile'">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"/><circle cx="12" cy="7" r="4"/></svg>
              <span class="nav-label" v-if="!sidebarCollapsed">Profil</span>
            </button>
            <button v-if="isAdmin" class="nav-item" :class="{ active: currentPage === 'admin' }" @click="currentPage = 'admin'">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/></svg>
              <span class="nav-label" v-if="!sidebarCollapsed">Admin</span>
            </button>
          </nav>

          <div class="sidebar-bottom">
            <div class="sidebar-user" v-if="!sidebarCollapsed">
              <div class="user-avatar-sm">{{ currentUser.full_name?.charAt(0)?.toUpperCase() }}</div>
              <div class="user-meta">
                <span class="user-name-sm">{{ currentUser.full_name }}</span>
                <span class="user-role-sm" :class="'role-' + currentUser.role">{{ currentUser.role }}</span>
              </div>
            </div>
            <button class="nav-item nav-item-logout" @click="logout">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4"/><polyline points="16 17 21 12 16 7"/><line x1="21" y1="12" x2="9" y2="12"/></svg>
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
                <template v-if="currentPage === 'documents'">Dokumenti</template>
                <template v-else-if="currentPage === 'upload'">Naloži dokument</template>
                <template v-else-if="currentPage === 'profile'">Uporabniški profil</template>
                <template v-else-if="currentPage === 'admin'">Administracija</template>
              </h1>
              <p class="page-subtitle">
                <template v-if="currentPage === 'documents'">Pregled, iskanje in upravljanje dokumentov</template>
                <template v-else-if="currentPage === 'upload'">PDF datoteke do 15 MB</template>
                <template v-else-if="currentPage === 'profile'">Podatki o tvojem računu</template>
                <template v-else-if="currentPage === 'admin'">Sistemske statistike in uporabniki</template>
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

          <!-- ── Page: Documents ── -->
          <section v-if="currentPage === 'documents'" class="page">
            <div class="toolbar">
              <div class="search-wrap">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" class="search-svg"><circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/></svg>
                <input v-model="searchQuery" type="text" placeholder="Išči po imenu datoteke..." class="search-input" />
              </div>
              <select v-model="sortField" class="sort-select">
                <option value="date">Najnovejši</option>
                <option value="name">Po imenu</option>
                <option value="size">Po velikosti</option>
                <option value="status">Po statusu</option>
              </select>
              <span class="result-count">{{ filteredDocuments.length }} rezultatov</span>
            </div>

            <div v-if="dashboardBusy" class="state-box">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" class="state-icon spin"><path d="M21 12a9 9 0 1 1-6.219-8.56"/></svg>
              <span>Nalagam dokumente...</span>
            </div>

            <div v-else-if="!documents.length" class="state-box state-empty">
              <div class="empty-circle">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><path d="M13 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V9z"/><polyline points="13 2 13 9 20 9"/></svg>
              </div>
              <p class="empty-title">Ni dokumentov</p>
              <p class="empty-sub">Naloži prvi PDF za začetek</p>
              <button class="btn-primary-sm" @click="currentPage = 'upload'">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" class="btn-ico"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="17 8 12 3 7 8"/><line x1="12" y1="3" x2="12" y2="15"/></svg>
                Naloži dokument
              </button>
            </div>

            <div v-else class="doc-grid">
              <TransitionGroup name="list">
                <DocumentCard
                  v-for="doc in filteredDocuments"
                  :key="doc.id"
                  :document="doc"
                  :summary-busy="activeSummaryId === doc.id"
                  :question-busy="activeQuestionId === doc.id"
                  :latest-answer="latestAnswers[doc.id] || null"
                  @summarize="handleSummarize"
                  @ask="handleAsk"
                  @delete="handleDelete"
                  @download="handleDownload"
                />
              </TransitionGroup>
            </div>
          </section>

          <!-- ── Page: Upload ── -->
          <section v-else-if="currentPage === 'upload'" class="page">
            <div class="upload-wrap">
              <UploadSection :busy="uploadBusy" @upload="handleUpload" />
            </div>
          </section>

          <!-- ── Page: Profile ── -->
          <section v-else-if="currentPage === 'profile'" class="page">
            <div class="profile-card-wrap">
              <div class="profile-avatar-lg">{{ currentUser.full_name?.charAt(0)?.toUpperCase() }}</div>
              <h2 class="profile-name">{{ currentUser.full_name }}</h2>
              <span class="profile-role-tag" :class="'role-tag-' + currentUser.role">{{ currentUser.role }}</span>
            </div>
            <div class="info-grid">
              <div class="info-item">
                <span class="info-label">Email</span>
                <span class="info-value">{{ currentUser.email }}</span>
              </div>
              <div class="info-item">
                <span class="info-label">Vloga</span>
                <span class="info-value capitalize">{{ currentUser.role }}</span>
              </div>
              <div class="info-item">
                <span class="info-label">Dokumenti</span>
                <span class="info-value">{{ documents.length }}</span>
              </div>
              <div class="info-item">
                <span class="info-label">Povzetki</span>
                <span class="info-value">{{ summaryCount }}</span>
              </div>
            </div>
          </section>

          <!-- ── Page: Admin ── -->
          <section v-else-if="currentPage === 'admin' && isAdmin" class="page">
            <div class="stats-row" v-if="adminStats">
              <div class="stat-tile"><span class="stat-num">{{ adminStats.users }}</span><span class="stat-lbl">Uporabnikov</span></div>
              <div class="stat-tile"><span class="stat-num">{{ adminStats.documents }}</span><span class="stat-lbl">Dokumentov</span></div>
              <div class="stat-tile"><span class="stat-num">{{ adminStats.summaries }}</span><span class="stat-lbl">Povzetkov</span></div>
              <div class="stat-tile"><span class="stat-num">{{ adminStats.questions }}</span><span class="stat-lbl">Vprašanj</span></div>
              <div class="stat-tile"><span class="stat-num">{{ adminStats.jobs }}</span><span class="stat-lbl">Opravil</span></div>
            </div>

            <div class="table-card" v-if="adminUsers.length">
              <div class="table-header">
                <h3 class="table-title">
                  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" class="table-title-icon"><path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M23 21v-2a4 4 0 0 0-3-3.87"/><path d="M16 3.13a4 4 0 0 1 0 7.75"/></svg>
                  Registrirani uporabniki
                </h3>
                <span class="table-count">{{ adminUsers.length }}</span>
              </div>
              <div class="table-wrap">
                <table class="data-table">
                  <thead>
                    <tr>
                      <th>Email</th>
                      <th>Ime</th>
                      <th>Vloga</th>
                      <th>Akcije</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr v-for="u in adminUsers" :key="u.id">
                      <td class="td-email">{{ u.email }}</td>
                      <td>{{ u.full_name }}</td>
                      <td>
                        <span class="role-pill" :class="'rp-' + u.role">{{ u.role }}</span>
                      </td>
                      <td class="td-actions">
                        <template v-if="u.id !== currentUser.id">
                          <button
                            v-if="u.role === 'user'"
                            class="btn-xs btn-promote"
                            @click="handleSetRole(u.id, 'admin')"
                            title="Povišaj v admina"
                          >
                            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/></svg>
                            Admin
                          </button>
                          <button
                            v-else
                            class="btn-xs btn-demote"
                            @click="handleSetRole(u.id, 'user')"
                            title="Znižaj v uporabnika"
                          >
                            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"/><circle cx="12" cy="7" r="4"/></svg>
                            User
                          </button>
                        </template>
                        <span v-else class="td-you">Ti</span>
                      </td>
                    </tr>
                  </tbody>
                </table>
              </div>
            </div>
          </section>

          <!-- Footer -->
          <footer class="main-footer">
            <span>AI Document Assistant v1.2.1</span>
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
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" class="toast-svg"><path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/><polyline points="22 4 12 14.01 9 11.01"/></svg>
        <span>{{ globalMessage }}</span>
        <button class="toast-x" @click.stop="globalMessage = ''">&times;</button>
      </div>
    </Transition>
    <Transition name="toast">
      <div v-if="globalError" class="toast toast-err" @click="globalError = ''">
        <div class="toast-accent accent-err"></div>
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" class="toast-svg"><circle cx="12" cy="12" r="10"/><line x1="15" y1="9" x2="9" y2="15"/><line x1="9" y1="9" x2="15" y2="15"/></svg>
        <span>{{ globalError }}</span>
        <button class="toast-x" @click.stop="globalError = ''">&times;</button>
      </div>
    </Transition>
  </div>
</template>

<style scoped>
/* ═══════════════════ LANDING PAGE ═══════════════════ */
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
    radial-gradient(ellipse at 25% 0%, rgba(99,102,241,0.10) 0%, transparent 50%),
    radial-gradient(ellipse at 75% 100%, rgba(16,185,129,0.08) 0%, transparent 50%);
  pointer-events: none;
  z-index: 0;
}

.landing-nav {
  position: sticky;
  top: 0;
  z-index: 20;
  background: rgba(255,255,255,0.85);
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

.brand-icon svg { width: 17px; height: 17px; }

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
  border: 1px solid rgba(99,102,241,0.12);
  margin-bottom: 1.5rem;
}

.chip-icon { width: 14px; height: 14px; }

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

.dot-indigo { background: var(--primary); }
.dot-emerald { background: var(--accent); }
.dot-amber { background: var(--warning); }
.dot-rose { background: var(--danger); }
.dot-sky { background: #0ea5e9; }
.dot-violet { background: #8b5cf6; }

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

.footer-dot { color: var(--border); }

.footer-link {
  color: var(--primary);
  text-decoration: none;
  font-weight: 500;
}

.footer-link:hover { text-decoration: underline; }

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
  border-bottom: 1px solid rgba(255,255,255,0.07);
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

.sb-icon svg { width: 16px; height: 16px; color: white; }

.sb-text {
  display: flex;
  flex-direction: column;
  line-height: 1.2;
}

.sb-name { font-weight: 700; font-size: 0.88rem; }
.sb-ver { font-size: 0.62rem; color: #8b92a0; }

.sidebar-toggle {
  width: 32px;
  height: 32px;
  border: none;
  background: rgba(255,255,255,0.06);
  border-radius: 6px;
  color: #8b92a0;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.sidebar-toggle svg { width: 16px; height: 16px; }
.sidebar-toggle:hover { background: rgba(255,255,255,0.12); color: #e2e8ef; }

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

.nav-item svg { width: 18px; height: 18px; flex-shrink: 0; }

.nav-item:hover {
  background: rgba(255,255,255,0.06);
  color: #e2e8ef;
}

.nav-item.active {
  background: rgba(99,102,241,0.15);
  color: #a5b4fc;
}

.nav-badge {
  margin-left: auto;
  background: rgba(99,102,241,0.2);
  color: #a5b4fc;
  font-size: 0.7rem;
  font-weight: 700;
  padding: 0.12rem 0.5rem;
  border-radius: 999px;
}

.sidebar-bottom {
  padding: 0.75rem 0.5rem;
  border-top: 1px solid rgba(255,255,255,0.07);
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

.role-admin { color: #fbbf24; }
.role-user { color: #8b92a0; }

.nav-item-logout { color: #ef4444; }
.nav-item-logout:hover { background: rgba(239,68,68,0.12); color: #f87171; }

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

/* ── Page ── */
.page {
  flex: 1;
  padding: 1.5rem 2rem;
}

/* ── Toolbar ── */
.toolbar {
  display: flex;
  gap: 0.75rem;
  align-items: center;
  margin-bottom: 1.25rem;
}

.search-wrap {
  flex: 1;
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.55rem 0.9rem;
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: var(--radius-sm);
  transition: border-color 0.2s, box-shadow 0.2s;
}

.search-wrap:focus-within {
  border-color: var(--primary);
  box-shadow: var(--shadow-glow);
}

.search-svg { width: 16px; height: 16px; color: var(--text-light); flex-shrink: 0; }

.search-input {
  border: none;
  outline: none;
  background: transparent;
  font-size: 0.85rem;
  color: var(--text);
  width: 100%;
  font-family: inherit;
}

.search-input::placeholder { color: var(--text-light); }

.sort-select {
  padding: 0.55rem 0.9rem;
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: var(--radius-sm);
  font-size: 0.82rem;
  color: var(--text);
  font-family: inherit;
  cursor: pointer;
  outline: none;
}

.sort-select:focus { border-color: var(--primary); box-shadow: var(--shadow-glow); }

.result-count {
  font-size: 0.78rem;
  color: var(--text-light);
  white-space: nowrap;
}

/* ── Document Grid ── */
.doc-grid {
  display: grid;
  gap: 1rem;
}

/* ── States ── */
.state-box {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 0.75rem;
  padding: 4rem 2rem;
  text-align: center;
  color: var(--text-muted);
  font-size: 0.95rem;
}

.state-icon { width: 24px; height: 24px; }

.empty-circle {
  width: 72px;
  height: 72px;
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
}

.empty-circle svg { width: 28px; height: 28px; color: var(--text-light); }
.empty-title { margin: 0; font-weight: 600; color: var(--text); }
.empty-sub { margin: 0.15rem 0 1rem; font-size: 0.85rem; color: var(--text-light); }

.btn-primary-sm {
  display: inline-flex;
  align-items: center;
  gap: 0.4rem;
  padding: 0.55rem 1.1rem;
  border: 0;
  border-radius: var(--radius-sm);
  background: linear-gradient(135deg, var(--primary), #818cf8);
  color: white;
  font-size: 0.85rem;
  font-weight: 600;
  box-shadow: 0 2px 8px rgba(99,102,241,0.25);
}

.btn-primary-sm:hover { box-shadow: 0 4px 14px rgba(99,102,241,0.35); }
.btn-ico { width: 15px; height: 15px; }

/* ── Upload ── */
.upload-wrap {
  max-width: 640px;
}

/* ── Profile ── */
.profile-card-wrap {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 2rem 1.5rem;
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: var(--radius-lg);
  margin-bottom: 1.5rem;
  text-align: center;
}

.profile-avatar-lg {
  width: 72px;
  height: 72px;
  background: linear-gradient(135deg, var(--primary), #818cf8);
  border-radius: 50%;
  color: white;
  font-size: 1.8rem;
  font-weight: 700;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 0.75rem;
}

.profile-name {
  margin: 0;
  font-size: 1.25rem;
  font-weight: 700;
  color: var(--text);
}

.profile-role-tag {
  display: inline-block;
  padding: 0.2rem 0.7rem;
  border-radius: 999px;
  font-size: 0.72rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.04em;
  margin-top: 0.5rem;
}

.role-tag-admin { background: #fef3c7; color: #92400e; }
.role-tag-user { background: var(--primary-light); color: var(--primary); }

.info-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(220px, 1fr));
  gap: 0.75rem;
}

.info-item {
  padding: 0.85rem 1rem;
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: var(--radius-sm);
  display: flex;
  flex-direction: column;
  gap: 0.2rem;
}

.info-label {
  font-size: 0.68rem;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.04em;
  color: var(--text-light);
}

.info-value {
  font-size: 0.95rem;
  font-weight: 500;
  color: var(--text);
}

.capitalize { text-transform: capitalize; }

/* ── Admin Stats ── */
.stats-row {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(140px, 1fr));
  gap: 0.75rem;
  margin-bottom: 1.5rem;
}

.stat-tile {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 1rem;
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: var(--radius);
}

.stat-num {
  font-size: 1.6rem;
  font-weight: 800;
  color: var(--primary);
  line-height: 1;
}

.stat-lbl {
  font-size: 0.68rem;
  font-weight: 500;
  text-transform: uppercase;
  letter-spacing: 0.04em;
  color: var(--text-light);
  margin-top: 0.2rem;
}

/* ── Admin Table ── */
.table-card {
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: var(--radius-lg);
  overflow: hidden;
}

.table-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 1rem 1.25rem;
  border-bottom: 1px solid var(--border);
}

.table-title {
  margin: 0;
  font-size: 0.95rem;
  font-weight: 700;
  color: var(--text);
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.table-title-icon { width: 18px; height: 18px; color: var(--primary); }

.table-count {
  font-size: 0.75rem;
  font-weight: 700;
  padding: 0.15rem 0.55rem;
  background: var(--primary-light);
  color: var(--primary);
  border-radius: 999px;
}

.table-wrap { overflow-x: auto; }

.data-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 0.85rem;
}

.data-table th {
  text-align: left;
  padding: 0.7rem 1.25rem;
  font-size: 0.72rem;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.04em;
  color: var(--text-light);
  background: var(--surface-alt);
  border-bottom: 1px solid var(--border);
}

.data-table td {
  padding: 0.7rem 1.25rem;
  border-bottom: 1px solid var(--border-subtle);
  color: var(--text);
}

.data-table tr:last-child td { border-bottom: none; }

.data-table tr:hover td { background: var(--surface-alt); }

.td-email { font-weight: 500; }

.td-actions { white-space: nowrap; }

.role-pill {
  display: inline-block;
  padding: 0.18rem 0.55rem;
  border-radius: 999px;
  font-size: 0.72rem;
  font-weight: 600;
  text-transform: capitalize;
}

.rp-admin { background: #fef3c7; color: #92400e; }
.rp-user { background: var(--primary-light); color: var(--primary); }

.btn-xs {
  display: inline-flex;
  align-items: center;
  gap: 0.3rem;
  padding: 0.3rem 0.65rem;
  border: 1px solid var(--border);
  border-radius: var(--radius-sm);
  background: var(--surface);
  font-size: 0.75rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.15s;
}

.btn-xs svg { width: 13px; height: 13px; }

.btn-promote {
  color: #d97706;
  border-color: #fde68a;
}
.btn-promote:hover { background: #fef3c7; }

.btn-demote {
  color: var(--primary);
  border-color: rgba(99,102,241,0.2);
}
.btn-demote:hover { background: var(--primary-light); }

.td-you {
  font-size: 0.75rem;
  color: var(--text-light);
  font-style: italic;
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

.accent-ok { background: var(--accent); }
.accent-err { background: var(--danger); }

.toast-ok .toast-svg { color: var(--accent); }
.toast-err .toast-svg { color: var(--danger); }

.toast-svg { width: 18px; height: 18px; flex-shrink: 0; }

.toast-x {
  margin-left: auto;
  background: none;
  border: none;
  font-size: 1.15rem;
  color: var(--text-light);
  padding: 0 0 0 0.4rem;
  line-height: 1;
}
.toast-x:hover { color: var(--text); transform: none; }

.toast-enter-active, .toast-leave-active { transition: all 0.3s cubic-bezier(0.4,0,0.2,1); }
.toast-enter-from { opacity: 0; transform: translateX(2rem); }
.toast-leave-to { opacity: 0; transform: translateY(1rem); }

/* ── List transitions ── */
.list-enter-active, .list-leave-active { transition: all 0.3s ease; }
.list-enter-from { opacity: 0; transform: translateY(-8px); }
.list-leave-to { opacity: 0; transform: translateX(20px); }
.list-move { transition: transform 0.3s ease; }

@keyframes spin { to { transform: rotate(360deg); } }
.spin { animation: spin 1s linear infinite; }

/* ── Responsive ── */
@media (max-width: 860px) {
  .landing-grid {
    grid-template-columns: 1fr;
    gap: 2.5rem;
    padding: 2rem 1.5rem;
  }

  .landing-auth { position: static; }
  .landing-title { font-size: 2.2rem; }
  .feature-grid { grid-template-columns: repeat(2, auto); }

  .sidebar {
    position: fixed;
    left: 0;
    top: 0;
    bottom: 0;
    width: 256px;
    transform: translateX(-100%);
    transition: transform 0.25s ease;
  }

  .sidebar:not(.collapsed) { transform: translateX(0); }

  .page { padding: 1.25rem 1rem; }
  .topbar { padding: 1rem 1.25rem; }

  .stats-row { grid-template-columns: repeat(2, 1fr); }
}

@media (max-width: 540px) {
  .topbar-stats { display: none; }
  .toolbar { flex-wrap: wrap; }
  .info-grid { grid-template-columns: 1fr; }
}
</style>
