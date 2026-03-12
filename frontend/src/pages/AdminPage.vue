<script setup>
  import { computed } from 'vue'
  import { useStore } from '../composables/useStore'
  import { Doughnut, Bar } from 'vue-chartjs'
  import {
    Chart as ChartJS,
    ArcElement,
    BarElement,
    CategoryScale,
    LinearScale,
    Tooltip,
    Legend,
  } from 'chart.js'

  ChartJS.register(ArcElement, BarElement, CategoryScale, LinearScale, Tooltip, Legend)

  const { adminStats, adminUsers, currentUser, handleSetRole, formatDate, formatDateTime } =
    useStore()

  function formatBytes(bytes) {
    if (!bytes || bytes === 0) return '0 B'
    if (bytes < 1024) return bytes + ' B'
    if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB'
    return (bytes / (1024 * 1024)).toFixed(1) + ' MB'
  }

  const statusChartData = computed(() => {
    if (!adminStats.value?.status_breakdown) return null
    const b = adminStats.value.status_breakdown
    const labels = Object.keys(b)
    const data = Object.values(b)
    const colors = {
      ready: '#10b981',
      uploaded: '#6366f1',
      processing: '#f59e0b',
      'summary-processing': '#f59e0b',
      'question-processing': '#f59e0b',
      'summary-failed': '#ef4444',
      failed: '#ef4444',
    }
    return {
      labels,
      datasets: [
        {
          data,
          backgroundColor: labels.map((l) => colors[l] || '#94a3b8'),
          borderWidth: 0,
          hoverOffset: 6,
        },
      ],
    }
  })

  const sourceChartData = computed(() => {
    if (!adminStats.value?.source_breakdown) return null
    const b = adminStats.value.source_breakdown
    const labels = Object.keys(b)
    const data = Object.values(b)
    return {
      labels,
      datasets: [
        {
          label: 'Odgovori po viru',
          data,
          backgroundColor: 'rgba(99, 102, 241, 0.7)',
          borderRadius: 6,
          borderSkipped: false,
        },
      ],
    }
  })

  const jobChartData = computed(() => {
    if (!adminStats.value?.job_breakdown) return null
    const b = adminStats.value.job_breakdown
    const labels = Object.keys(b)
    const data = Object.values(b)
    const colors = {
      completed: '#10b981',
      queued: '#6366f1',
      running: '#f59e0b',
      failed: '#ef4444',
    }
    return {
      labels,
      datasets: [
        {
          data,
          backgroundColor: labels.map((l) => colors[l] || '#94a3b8'),
          borderWidth: 0,
          hoverOffset: 6,
        },
      ],
    }
  })

  const chartOpts = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: { legend: { display: false }, tooltip: { boxPadding: 4 } },
  }
  const barOpts = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: { legend: { display: false }, tooltip: { boxPadding: 4 } },
    scales: { x: { grid: { display: false } }, y: { beginAtZero: true, ticks: { stepSize: 1 } } },
  }

  const readyPercent = computed(() => {
    if (!adminStats.value?.documents) return 0
    const ready = adminStats.value.status_breakdown?.ready || 0
    return Math.round((ready / adminStats.value.documents) * 100)
  })

  const queuedJobs = computed(() => adminStats.value?.job_breakdown?.queued || 0)

  const activeUsers = computed(() =>
    adminUsers.value.filter((user) => Boolean(user.last_login_at)).length,
  )
</script>

<template>
  <section class="page">
    <div class="admin-hero" v-if="adminStats">
      <div class="admin-hero-main">
        <span class="admin-kicker">Administracija</span>
        <h2 class="admin-title">Pregled sistema, uporabnikov in stanja obdelave dokumentov.</h2>
        <p class="admin-text">
          V enem pogledu spremljaš uporabo sistema, uspešnost obdelave ter upravljaš uporabniške vloge.
        </p>
      </div>
      <div class="admin-hero-side">
        <div class="admin-side-card">
          <span class="admin-side-label">Pripravljenost dokumentov</span>
          <strong>{{ readyPercent }}%</strong>
          <p>Dokumentov je že pripravljenih za pregled, vprašanja ali nadaljnjo uporabo.</p>
        </div>
        <div class="admin-side-card compact">
          <span>Aktivni uporabniki</span>
          <strong>{{ activeUsers }}</strong>
        </div>
        <div class="admin-side-card compact">
          <span>Opravila v čakalni vrsti</span>
          <strong>{{ queuedJobs }}</strong>
        </div>
      </div>
    </div>

    <div class="stats-row" v-if="adminStats">
      <div class="stat-tile">
        <span class="stat-num">{{ adminStats.users }}</span
        ><span class="stat-lbl">Uporabnikov</span>
      </div>
      <div class="stat-tile">
        <span class="stat-num">{{ adminStats.admins }}</span
        ><span class="stat-lbl">Adminov</span>
      </div>
      <div class="stat-tile">
        <span class="stat-num">{{ adminStats.documents }}</span
        ><span class="stat-lbl">Dokumentov</span>
      </div>
      <div class="stat-tile">
        <span class="stat-num">{{ adminStats.summaries }}</span
        ><span class="stat-lbl">Povzetkov</span>
      </div>
      <div class="stat-tile">
        <span class="stat-num">{{ adminStats.questions }}</span
        ><span class="stat-lbl">Vprašanj</span>
      </div>
      <div class="stat-tile">
        <span class="stat-num">{{ adminStats.jobs }}</span
        ><span class="stat-lbl">Opravil</span>
      </div>
      <div class="stat-tile">
        <span class="stat-num">{{ formatBytes(adminStats.total_storage_bytes) }}</span
        ><span class="stat-lbl">Poraba</span>
      </div>
    </div>

    <!-- Charts row -->
    <div v-if="adminStats" class="charts-row">
      <div v-if="statusChartData" class="chart-card">
        <h5 class="chart-title">Status dokumentov</h5>
        <div class="chart-wrap"><Doughnut :data="statusChartData" :options="chartOpts" /></div>
      </div>
      <div v-if="sourceChartData" class="chart-card chart-card-wide">
        <h5 class="chart-title">Odgovori po AI viru</h5>
        <div class="chart-wrap"><Bar :data="sourceChartData" :options="barOpts" /></div>
      </div>
      <div v-if="jobChartData" class="chart-card">
        <h5 class="chart-title">Opravila po statusu</h5>
        <div class="chart-wrap"><Doughnut :data="jobChartData" :options="chartOpts" /></div>
      </div>
    </div>

    <div class="table-card" v-if="adminUsers.length">
      <div class="table-header">
        <h3 class="table-title">
          <svg
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            stroke-width="2"
            class="table-title-icon"
          >
            <path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2" />
            <circle cx="9" cy="7" r="4" />
            <path d="M23 21v-2a4 4 0 0 0-3-3.87" />
            <path d="M16 3.13a4 4 0 0 1 0 7.75" />
          </svg>
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
              <th>Registriran</th>
              <th>Zadnja prijava</th>
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
              <td class="td-date">{{ formatDateTime(u.created_at) }}</td>
              <td class="td-date">{{ formatDateTime(u.last_login_at) || '—' }}</td>
              <td class="td-actions">
                <template v-if="u.id !== currentUser.id">
                  <button
                    v-if="u.role === 'user'"
                    class="btn-xs btn-promote"
                    @click="handleSetRole(u.id, 'admin')"
                    title="Povišaj v admina"
                  >
                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                      <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z" />
                    </svg>
                    Dodeli skrbnika
                  </button>
                  <button
                    v-else
                    class="btn-xs btn-demote"
                    @click="handleSetRole(u.id, 'user')"
                    title="Znižaj v uporabnika"
                  >
                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                      <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2" />
                      <circle cx="12" cy="7" r="4" />
                    </svg>
                    Nastavi uporabnika
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
</template>

<style scoped>
  .page {
    flex: 1;
    padding: 1.5rem 2rem;
  }

  .admin-hero {
    display: grid;
    grid-template-columns: minmax(0, 1.2fr) minmax(280px, 0.9fr);
    gap: 1rem;
    margin-bottom: 1.25rem;
  }

  .admin-hero-main,
  .admin-hero-side {
    padding: 1.3rem 1.4rem;
    background: rgba(255, 255, 255, 0.72);
    border: 1px solid rgba(255, 255, 255, 0.62);
    border-radius: 24px;
    box-shadow: var(--shadow-md);
    backdrop-filter: blur(12px);
  }

  .admin-kicker {
    display: inline-block;
    margin-bottom: 0.5rem;
    padding: 0.28rem 0.56rem;
    border-radius: 999px;
    background: var(--primary-light);
    color: var(--primary);
    font-size: 0.7rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.08em;
  }

  .admin-title {
    margin: 0;
    max-width: 18ch;
    font-size: clamp(1.8rem, 3vw, 2.4rem);
    line-height: 1.05;
    color: var(--text);
  }

  .admin-text {
    margin: 0.9rem 0 0;
    color: var(--text-muted);
    line-height: 1.7;
    max-width: 60ch;
  }

  .admin-hero-side {
    display: grid;
    grid-template-columns: repeat(2, minmax(0, 1fr));
    gap: 0.75rem;
    align-content: start;
  }

  .admin-side-card {
    padding: 1rem;
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 18px;
  }

  .admin-side-card:first-child {
    grid-column: 1 / -1;
  }

  .admin-side-label {
    display: inline-block;
    margin-bottom: 0.45rem;
    font-size: 0.68rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    color: var(--primary);
  }

  .admin-side-card strong {
    display: block;
    margin-bottom: 0.25rem;
    font-size: 1.3rem;
    color: var(--primary);
  }

  .admin-side-card p,
  .admin-side-card span {
    margin: 0;
    color: var(--text-muted);
    line-height: 1.55;
    font-size: 0.8rem;
  }

  .stats-row {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(120px, 1fr));
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
    border-radius: 18px;
    box-shadow: var(--shadow-sm);
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

  .charts-row {
    display: grid;
    grid-template-columns: 1fr 2fr 1fr;
    gap: 0.75rem;
    margin-bottom: 1.5rem;
  }
  .chart-card {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 22px;
    padding: 1rem;
    box-shadow: var(--shadow-sm);
  }
  .chart-card-wide {
  }
  .chart-title {
    margin: 0 0 0.5rem;
    font-size: 0.78rem;
    font-weight: 700;
    color: var(--text);
  }
  .chart-wrap {
    position: relative;
    height: 160px;
  }

  .table-card {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: var(--radius-lg);
    overflow: hidden;
    box-shadow: var(--shadow-md);
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

  .table-title-icon {
    width: 18px;
    height: 18px;
    color: var(--primary);
  }

  .table-count {
    font-size: 0.75rem;
    font-weight: 700;
    padding: 0.15rem 0.55rem;
    background: var(--primary-light);
    color: var(--primary);
    border-radius: 999px;
  }

  .table-wrap {
    overflow-x: auto;
  }

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

  .data-table tr:last-child td {
    border-bottom: none;
  }

  .data-table tr:hover td {
    background: var(--surface-alt);
  }

  .td-email {
    font-weight: 500;
  }

  .td-date {
    font-size: 0.8rem;
    color: var(--text-light);
    white-space: nowrap;
  }

  .td-actions {
    white-space: nowrap;
  }

  .role-pill {
    display: inline-block;
    padding: 0.18rem 0.55rem;
    border-radius: 999px;
    font-size: 0.72rem;
    font-weight: 600;
    text-transform: capitalize;
  }

  .rp-admin {
    background: #fef3c7;
    color: #92400e;
  }
  .rp-user {
    background: var(--primary-light);
    color: var(--primary);
  }

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

  .btn-xs svg {
    width: 13px;
    height: 13px;
  }

  .btn-promote {
    color: #d97706;
    border-color: #fde68a;
  }
  .btn-promote:hover {
    background: #fef3c7;
  }

  .btn-demote {
    color: var(--primary);
    border-color: rgba(99, 102, 241, 0.2);
  }
  .btn-demote:hover {
    background: var(--primary-light);
  }

  .td-you {
    font-size: 0.75rem;
    color: var(--text-light);
    font-style: italic;
  }

  @media (max-width: 860px) {
    .page {
      padding: 1.25rem 1rem;
    }
    .admin-hero,
    .admin-hero-side {
      grid-template-columns: 1fr;
    }
    .stats-row {
      grid-template-columns: repeat(2, 1fr);
    }
    .charts-row {
      grid-template-columns: 1fr;
    }
  }

  @media (max-width: 540px) {
    .stats-row {
      grid-template-columns: 1fr;
    }
    .users-table {
      font-size: 0.78rem;
    }
    .users-table th,
    .users-table td {
      padding: 0.5rem 0.4rem;
    }
  }
</style>
