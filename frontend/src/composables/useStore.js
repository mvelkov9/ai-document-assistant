import { computed, reactive, ref } from 'vue'

import {
  clearDocumentAnswers,
  createQuestionJob,
  createSummaryJob,
  deleteDocument,
  deleteDocumentAnswer,
  downloadDocument,
  getAdminStats,
  getAdminUsers,
  getJobStatus,
  getCurrentUser,
  listDocuments,
  listDocumentAnswers,
  loginUser,
  registerUser,
  setUserRole,
  updateDocumentTags,
  uploadDocument,
} from '../lib/api'
import { formatCountLabel, i18n, setI18nLanguage, translate } from '../lib/i18n'

const TOKEN_KEY = 'docassist-token'

/* ── State (module-level singletons) ── */
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
const documentAnswers = reactive({})
const searchQuery = ref('')
const sortField = ref('date')
const selectedTag = ref('')
const adminStats = ref(null)
const adminUsers = ref([])
const sidebarCollapsed = ref(false)
const LANGUAGE_KEY = 'docassist-language'
const language = ref(localStorage.getItem(LANGUAGE_KEY) || 'sl')

/* ── Dark mode ── */
const DARK_KEY = 'docassist-dark'
const darkMode = ref(localStorage.getItem(DARK_KEY) === 'true')
function applyDarkClass() {
  document.documentElement.classList.toggle('dark', darkMode.value)
}
applyDarkClass()

function applyLanguageAttr() {
  setI18nLanguage(language.value)
}

applyLanguageAttr()

function toggleDarkMode() {
  darkMode.value = !darkMode.value
  localStorage.setItem(DARK_KEY, darkMode.value)
  applyDarkClass()
}

function setLanguage(nextLanguage) {
  language.value = nextLanguage === 'en' ? 'en' : 'sl'
  localStorage.setItem(LANGUAGE_KEY, language.value)
  applyLanguageAttr()
}

function toggleLanguage() {
  setLanguage(language.value === 'sl' ? 'en' : 'sl')
}

function t(key, params) {
  language.value
  i18n.global.locale.value
  return translate(language.value, key, params)
}

function countLabel(count, forms) {
  language.value
  return formatCountLabel(language.value, count, forms)
}

function translateStatus(status) {
  if (!status) return ''
  return t(`status.${status}`)
}

function translateRole(role) {
  if (!role) return ''
  return t(`roles.${role}`)
}

/* ── Session bootstrap promise ── */
let _sessionReadyResolve
const sessionReady = new Promise((resolve) => {
  _sessionReadyResolve = resolve
})

/* ── Computed ── */
const isAuthenticated = computed(() => Boolean(sessionToken.value && currentUser.value))
const isAdmin = computed(() => currentUser.value?.role === 'admin')

const filteredDocuments = computed(() => {
  let docs = [...documents.value]
  const q = searchQuery.value.trim().toLowerCase()
  if (q) docs = docs.filter((d) => d.original_filename.toLowerCase().includes(q))
  if (selectedTag.value) docs = docs.filter((d) => (d.tags || []).includes(selectedTag.value))
  if (sortField.value === 'name')
    docs.sort((a, b) => a.original_filename.localeCompare(b.original_filename))
  else if (sortField.value === 'size') docs.sort((a, b) => b.size_bytes - a.size_bytes)
  else if (sortField.value === 'status')
    docs.sort((a, b) => a.processing_status.localeCompare(b.processing_status))
  else docs.sort((a, b) => new Date(b.created_at) - new Date(a.created_at))
  return docs
})

const allTags = computed(() => {
  const tagSet = new Set()
  documents.value.forEach((d) => (d.tags || []).forEach((t) => tagSet.add(t)))
  return [...tagSet].sort()
})

const summaryCount = computed(() => documents.value.filter((d) => d.summary_text).length)

const questionsCount = computed(() =>
  Object.values(documentAnswers).reduce((sum, arr) => sum + (arr?.length || 0), 0),
)

/* ── Helpers ── */
function setMessage(msg) {
  globalError.value = ''
  globalMessage.value = msg
}
function setError(msg) {
  globalMessage.value = ''
  globalError.value = msg
}
function persistToken(token) {
  sessionToken.value = token
  localStorage.setItem(TOKEN_KEY, token)
}
function clearSession() {
  sessionToken.value = ''
  currentUser.value = null
  documents.value = []
  localStorage.removeItem(TOKEN_KEY)
}

/* ── API actions ── */
async function refreshDocuments() {
  if (!sessionToken.value) return
  dashboardBusy.value = true
  try {
    const r = await listDocuments(sessionToken.value)
    documents.value = r.items || []
  } catch (e) {
    setError(e.message)
  } finally {
    dashboardBusy.value = false
  }
}

async function loadAnswersForDocument(documentId) {
  if (!sessionToken.value) return
  try {
    const answers = await listDocumentAnswers(sessionToken.value, documentId)
    documentAnswers[documentId] = answers || []
  } catch {
    /* silently fail — answers may not be available */
  }
}

async function loadAllAnswers() {
  if (!sessionToken.value || !documents.value.length) return
  await Promise.all(documents.value.map((d) => loadAnswersForDocument(d.id)))
}

async function bootstrapSession() {
  if (!sessionToken.value) {
    _sessionReadyResolve()
    return
  }
  dashboardBusy.value = true
  try {
    currentUser.value = await getCurrentUser(sessionToken.value)
    await refreshDocuments()
    await loadAllAnswers()
    if (isAdmin.value) await loadAdminData()
  } catch {
    clearSession()
  } finally {
    dashboardBusy.value = false
    _sessionReadyResolve()
  }
}

async function loadAdminData() {
  try {
    adminStats.value = await getAdminStats(sessionToken.value)
    adminUsers.value = await getAdminUsers(sessionToken.value)
  } catch {
    /* may fail for non-admin */
  }
}

async function handleLogin(form) {
  authBusy.value = true
  try {
    const tp = await loginUser(form)
    persistToken(tp.access_token)
    currentUser.value = await getCurrentUser(sessionToken.value)
    await refreshDocuments()
    if (isAdmin.value) await loadAdminData()
    setMessage(t('messages.loginSuccess'))
    return true
  } catch (e) {
    setError(e.message)
    return false
  } finally {
    authBusy.value = false
  }
}

async function handleRegister(form) {
  authBusy.value = true
  try {
    await registerUser(form)
    setMessage(t('messages.registerSuccess'))
  } catch (e) {
    setError(e.message)
  } finally {
    authBusy.value = false
  }
}

async function handleUpload(file) {
  uploadBusy.value = true
  try {
    await uploadDocument(sessionToken.value, file)
    await refreshDocuments()
    setMessage(t('messages.uploadSuccess'))
    return true
  } catch (e) {
    setError(e.message)
    return false
  } finally {
    uploadBusy.value = false
  }
}

async function pollJob(jobId, maxAttempts = 15) {
  for (let i = 0; i < maxAttempts; i++) {
    const job = await getJobStatus(sessionToken.value, jobId)
    if (job.status === 'completed') return job
    if (job.status === 'failed') throw new Error(job.error_message || 'Job failed.')
    await new Promise((r) => setTimeout(r, 1200))
  }
  return null
}

async function handleSummarize(documentId) {
  activeSummaryId.value = documentId
  try {
    const job = await createSummaryJob(sessionToken.value, documentId)
    const result = await pollJob(job.id)
    await refreshDocuments()
    setMessage(result ? t('messages.summaryReady') : t('messages.jobRunning'))
  } catch (e) {
    setError(e.message)
  } finally {
    activeSummaryId.value = ''
  }
}

async function handleAsk(documentId, question) {
  activeQuestionId.value = documentId

  // Show the user's question immediately as a pending bubble
  const pendingId = '__pending_' + Date.now()
  const pendingEntry = {
    id: pendingId,
    document_id: documentId,
    question_text: question,
    answer_text: '',
    source_mode: '',
    created_at: new Date().toISOString(),
    _pending: true,
  }
  if (!documentAnswers[documentId]) documentAnswers[documentId] = []
  documentAnswers[documentId].push(pendingEntry)

  try {
    const job = await createQuestionJob(sessionToken.value, documentId, question)
    const result = await pollJob(job.id)

    // Remove the pending entry and add the real one
    documentAnswers[documentId] = documentAnswers[documentId].filter((a) => a.id !== pendingId)
    if (result) {
      documentAnswers[documentId].push({
        id: result.id || Date.now().toString(),
        document_id: documentId,
        question_text: result.job_input || question,
        answer_text: result.result_text || t('messages.generatedNoContent'),
        source_mode: 'async-job',
        created_at: new Date().toISOString(),
      })
    }
    setMessage(result ? t('messages.answerReady') : t('messages.jobRunning'))
  } catch (e) {
    // Remove pending entry on error
    documentAnswers[documentId] = documentAnswers[documentId].filter((a) => a.id !== pendingId)
    setError(e.message)
  } finally {
    activeQuestionId.value = ''
  }
}

function logout() {
  clearSession()
  setMessage(t('messages.logoutSuccess'))
}

async function handleDelete(documentId) {
  try {
    await deleteDocument(sessionToken.value, documentId)
    delete documentAnswers[documentId]
    await refreshDocuments()
    setMessage(t('messages.documentDeleted'))
  } catch (e) {
    setError(e.message)
  }
}

async function handleDeleteAnswer(documentId, answerId) {
  try {
    await deleteDocumentAnswer(sessionToken.value, documentId, answerId)
    if (documentAnswers[documentId]) {
      documentAnswers[documentId] = documentAnswers[documentId].filter((a) => a.id !== answerId)
    }
    setMessage(t('messages.answerDeleted'))
  } catch (e) {
    setError(e.message)
  }
}

async function handleClearAnswers(documentId) {
  try {
    await clearDocumentAnswers(sessionToken.value, documentId)
    documentAnswers[documentId] = []
    setMessage(t('messages.conversationCleared'))
  } catch (e) {
    setError(e.message)
  }
}

async function handleUpdateTags(documentId, tags) {
  try {
    const updated = await updateDocumentTags(sessionToken.value, documentId, tags)
    const idx = documents.value.findIndex((d) => d.id === documentId)
    if (idx !== -1) documents.value[idx] = updated
  } catch (e) {
    setError(e.message)
  }
}

async function handleDownload(documentId, filename) {
  try {
    await downloadDocument(sessionToken.value, documentId, filename)
  } catch (e) {
    setError(e.message)
  }
}

async function handleSetRole(userId, role) {
  try {
    await setUserRole(sessionToken.value, userId, role)
    await loadAdminData()
    setMessage(t('messages.roleChanged', { role: translateRole(role) }))
  } catch (e) {
    setError(e.message)
  }
}

function formatDate(iso) {
  if (!iso) return ''
  return new Date(iso).toLocaleDateString(language.value === 'en' ? 'en-US' : 'sl-SI', {
    day: 'numeric',
    month: 'short',
    year: 'numeric',
  })
}

function formatDateTime(iso) {
  if (!iso) return ''
  const d = new Date(iso)
  const locale = language.value === 'en' ? 'en-US' : 'sl-SI'
  const date = d.toLocaleDateString(locale, {
    day: 'numeric',
    month: 'short',
    year: 'numeric',
  })
  const time = d.toLocaleTimeString(locale, { hour: '2-digit', minute: '2-digit' })
  return language.value === 'en' ? `${date} at ${time}` : `${date} ob ${time}`
}

export function useStore() {
  return {
    /* state */
    sessionToken,
    currentUser,
    documents,
    globalMessage,
    globalError,
    authBusy,
    dashboardBusy,
    uploadBusy,
    activeSummaryId,
    activeQuestionId,
    documentAnswers,
    searchQuery,
    sortField,
    selectedTag,
    adminStats,
    adminUsers,
    sidebarCollapsed,
    darkMode,
    language,

    /* computed */
    isAuthenticated,
    isAdmin,
    filteredDocuments,
    summaryCount,
    questionsCount,
    allTags,

    /* actions */
    setMessage,
    setError,
    clearSession,
    refreshDocuments,
    bootstrapSession,
    loadAdminData,
    handleLogin,
    handleRegister,
    handleUpload,
    handleSummarize,
    handleAsk,
    logout,
    handleDelete,
    handleDeleteAnswer,
    handleClearAnswers,
    handleUpdateTags,
    handleDownload,
    handleSetRole,
    toggleDarkMode,
    setLanguage,
    toggleLanguage,
    t,
    countLabel,
    translateStatus,
    translateRole,
    formatDate,
    formatDateTime,
    sessionReady,
  }
}
