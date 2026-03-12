<script setup>
  import { computed, defineAsyncComponent } from 'vue'
  import { useRouter } from 'vue-router'
  import { useStore } from '../composables/useStore'

  const DoughnutChart = defineAsyncComponent(() => import('../components/charts/DoughnutChart.vue'))
  const BarChart = defineAsyncComponent(() => import('../components/charts/BarChart.vue'))

  const router = useRouter()
  const {
    documentInsights,
    insightsBusy,
    t,
    formatDateTime,
    translateStatus,
    language,
    countLabel,
  } = useStore()

  const insights = computed(
    () =>
      documentInsights.value || {
        overview: {
          total_documents: 0,
          ready_documents: 0,
          summary_documents: 0,
          tagged_documents: 0,
          documents_with_questions: 0,
          total_questions: 0,
          total_size_bytes: 0,
          workspace_score: 0,
          summary_coverage_pct: 0,
          tag_coverage_pct: 0,
          question_coverage_pct: 0,
        },
        activity: {
          uploads_last_7_days: 0,
          questions_last_7_days: 0,
          last_upload_at: null,
          last_question_at: null,
        },
        status_breakdown: [],
        tag_breakdown: [],
        action_items: [],
        most_active_documents: [],
        ready_for_review: [],
        needs_attention: [],
        recently_uploaded: [],
      },
  )

  const overview = computed(() => insights.value.overview)

  const activity = computed(() => insights.value.activity)

  const hasDocuments = computed(() => overview.value.total_documents > 0)

  const scoreStyle = computed(() => ({
    background: `conic-gradient(var(--primary) ${overview.value.workspace_score}%, rgba(148, 163, 184, 0.16) 0)`,
  }))

  const statusChartData = computed(() => ({
    labels: insights.value.status_breakdown.map((item) => translateStatus(item.label)),
    datasets: [
      {
        data: insights.value.status_breakdown.map((item) => item.count),
        backgroundColor: ['#2563eb', '#0f766e', '#f59e0b', '#ef4444', '#475569', '#0ea5e9'],
        borderWidth: 0,
        hoverOffset: 8,
      },
    ],
  }))

  const tagChartData = computed(() => ({
    labels: insights.value.tag_breakdown.map((item) => item.label),
    datasets: [
      {
        label: t('workspace.tagsTitle'),
        data: insights.value.tag_breakdown.map((item) => item.count),
        backgroundColor: 'rgba(37, 99, 235, 0.78)',
        borderRadius: 10,
        borderSkipped: false,
      },
    ],
  }))

  const doughnutOptions = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: { legend: { display: false } },
  }

  const barOptions = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: { legend: { display: false } },
    scales: {
      x: { grid: { display: false } },
      y: { beginAtZero: true, ticks: { stepSize: 1 } },
    },
  }

  function formatBytes(bytes) {
    if (!bytes) return '0 B'
    const units = ['B', 'KB', 'MB', 'GB']
    let value = bytes
    let unitIndex = 0
    while (value >= 1024 && unitIndex < units.length - 1) {
      value /= 1024
      unitIndex += 1
    }
    return `${value >= 10 || unitIndex === 0 ? Math.round(value) : value.toFixed(1)} ${units[unitIndex]}`
  }

  function severityLabel(severity) {
    if (severity === 'high') return t('workspace.severityHigh')
    if (severity === 'medium') return t('workspace.severityMedium')
    return t('workspace.severityLow')
  }

  function badgeLabel(badge) {
    if (badge === 'hot') return t('workspace.badgeHot')
    if (badge === 'ready') return t('workspace.badgeReady')
    if (badge === 'attention') return t('workspace.badgeAttention')
    if (badge === 'next-step') return t('workspace.badgeNextStep')
    return t('workspace.badgeFresh')
  }

  function actionTitle(item) {
    return t(`workspace.actions.${item.key}.title`, { count: item.count })
  }

  function actionDescription(item) {
    if (language.value === 'sl') {
      if (item.key === 'improve-document-labeling') {
        return `${countLabel(item.count, {
          sl: ['dokument', 'dokumenta', 'dokumenti', 'dokumentov'],
          en: ['document', 'documents'],
        })} ${
          item.count === 1 ? 'nima oznak' : item.count === 2 ? 'nimata oznak' : 'nimajo oznak'
        }, zato sta filtriranje in segmentacija zbirke slabša, kot bi lahko bila.`
      }

      if (item.key === 'expand-document-interrogation') {
        return `${countLabel(item.count, {
          sl: ['dokument', 'dokumenta', 'dokumenti', 'dokumentov'],
          en: ['document', 'documents'],
        })} ${
          item.count === 1
            ? 'še ni bil pregledan z vprašanji in odgovori, zato njegova informacijska vrednost še ni izkoriščena.'
            : item.count === 2
              ? 'še nista bila pregledana z vprašanji in odgovori, zato njuna informacijska vrednost še ni izkoriščena.'
              : 'še niso bili pregledani z vprašanji in odgovori, zato njihova informacijska vrednost še ni izkoriščena.'
        }`
      }
    }

    return t(`workspace.actions.${item.key}.description`, { count: item.count })
  }

  function reasonLabel(item) {
    return t(`workspace.reasons.${item.reason_key}`)
  }

  function openUpload() {
    router.push('/upload')
  }

  function openDocuments() {
    router.push('/documents')
  }
</script>

<template>
  <section class="workspace-page">
    <div v-if="insightsBusy && !documentInsights" class="workspace-loading">
      <div class="loading-orb"></div>
      <span>{{ t('workspace.loading') }}</span>
    </div>

    <template v-else>
      <div class="workspace-hero">
        <div class="hero-copy">
          <span class="hero-kicker">{{ t('workspace.heroKicker') }}</span>
          <h2 class="hero-title">{{ t('workspace.heroTitle') }}</h2>
          <p class="hero-text">{{ t('workspace.heroText') }}</p>

          <div class="hero-actions">
            <button class="hero-btn hero-btn-primary" @click="openUpload">
              {{ t('workspace.goUpload') }}
            </button>
            <button class="hero-btn hero-btn-secondary" @click="openDocuments">
              {{ t('workspace.openDocuments') }}
            </button>
          </div>
        </div>

        <div class="hero-score-card">
          <div class="score-ring" :style="scoreStyle">
            <div class="score-ring-inner">
              <strong>{{ overview.workspace_score }}</strong>
              <span>{{ t('workspace.scorePoints') }}</span>
            </div>
          </div>
          <div class="score-meta">
            <span class="score-label">{{ t('workspace.workspaceScore') }}</span>
            <p>{{ t('workspace.scoreHint') }}</p>
          </div>
        </div>
      </div>

      <div class="workspace-metrics">
        <article class="metric-card accent-primary">
          <span>{{ t('workspace.summaryCoverage') }}</span>
          <strong>{{ overview.summary_coverage_pct }}%</strong>
        </article>
        <article class="metric-card accent-cyan">
          <span>{{ t('workspace.questionCoverage') }}</span>
          <strong>{{ overview.question_coverage_pct }}%</strong>
        </article>
        <article class="metric-card accent-slate">
          <span>{{ t('workspace.tagCoverage') }}</span>
          <strong>{{ overview.tag_coverage_pct }}%</strong>
        </article>
        <article class="metric-card accent-indigo">
          <span>{{ t('workspace.totalQuestions') }}</span>
          <strong>{{ overview.total_questions }}</strong>
        </article>
      </div>

      <div v-if="!hasDocuments" class="workspace-empty">
        <div class="empty-illustration"></div>
        <h3>{{ t('workspace.emptyWorkspace') }}</h3>
        <p>{{ t('workspace.emptyText') }}</p>
        <button class="hero-btn hero-btn-primary" @click="openUpload">
          {{ t('workspace.goUpload') }}
        </button>
      </div>

      <template v-else>
        <div class="activity-strip">
          <div class="activity-card">
            <span>{{ t('workspace.totalSize') }}</span>
            <strong>{{ formatBytes(overview.total_size_bytes) }}</strong>
          </div>
          <div class="activity-card">
            <span>{{ t('workspace.uploads7d') }}</span>
            <strong>{{ activity.uploads_last_7_days }}</strong>
          </div>
          <div class="activity-card">
            <span>{{ t('workspace.questions7d') }}</span>
            <strong>{{ activity.questions_last_7_days }}</strong>
          </div>
          <div class="activity-card activity-card-wide">
            <span>{{ t('workspace.lastUpload') }}</span>
            <strong>{{
              activity.last_upload_at
                ? formatDateTime(activity.last_upload_at)
                : t('workspace.noActivity')
            }}</strong>
          </div>
          <div class="activity-card activity-card-wide">
            <span>{{ t('workspace.lastQuestion') }}</span>
            <strong>{{
              activity.last_question_at
                ? formatDateTime(activity.last_question_at)
                : t('workspace.noActivity')
            }}</strong>
          </div>
        </div>

        <section class="action-section">
          <div class="section-head">
            <h3>{{ t('workspace.actionTitle') }}</h3>
          </div>
          <div v-if="insights.action_items.length" class="action-grid">
            <article
              v-for="item in insights.action_items"
              :key="item.key"
              class="action-card"
              :class="`severity-${item.severity}`"
            >
              <span class="severity-pill">{{ severityLabel(item.severity) }}</span>
              <h4>{{ actionTitle(item) }}</h4>
              <p>{{ actionDescription(item) }}</p>
            </article>
          </div>
          <div v-else class="action-empty">{{ t('workspace.actionEmpty') }}</div>
        </section>

        <div class="chart-grid">
          <article class="panel-card chart-card">
            <div class="section-head">
              <h3>{{ t('workspace.statusTitle') }}</h3>
            </div>
            <div class="chart-wrap doughnut-wrap">
              <DoughnutChart :data="statusChartData" :options="doughnutOptions" />
            </div>
            <div class="status-legend">
              <span v-for="item in insights.status_breakdown" :key="item.label" class="legend-row">
                <span>{{ translateStatus(item.label) }}</span>
                <strong>{{ item.count }}</strong>
              </span>
            </div>
          </article>

          <article class="panel-card chart-card">
            <div class="section-head">
              <h3>{{ t('workspace.tagsTitle') }}</h3>
            </div>
            <div v-if="insights.tag_breakdown.length" class="chart-wrap bar-wrap">
              <BarChart :data="tagChartData" :options="barOptions" />
            </div>
            <div v-else class="tag-empty">{{ t('workspace.tagsEmpty') }}</div>
          </article>
        </div>

        <div class="collections-grid">
          <article class="panel-card collection-card">
            <div class="section-head">
              <h3>{{ t('workspace.mostActive') }}</h3>
            </div>
            <div class="document-list">
              <div
                v-for="item in insights.most_active_documents"
                :key="item.id"
                class="document-row"
              >
                <div class="document-main">
                  <strong>{{ item.original_filename }}</strong>
                  <span>{{ item.answer_count }} · {{ badgeLabel(item.badge) }}</span>
                </div>
                <div class="document-score">{{ item.insight_score }}</div>
              </div>
            </div>
          </article>

          <article class="panel-card collection-card">
            <div class="section-head">
              <h3>{{ t('workspace.readyForReview') }}</h3>
            </div>
            <div class="document-list">
              <div
                v-for="item in insights.ready_for_review"
                :key="item.id"
                class="document-row detail-row"
              >
                <div class="document-main">
                  <strong>{{ item.original_filename }}</strong>
                  <span>{{ t('workspace.summaryReady') }}</span>
                </div>
                <span class="status-chip">{{ translateStatus(item.processing_status) }}</span>
              </div>
            </div>
          </article>

          <article class="panel-card collection-card">
            <div class="section-head">
              <h3>{{ t('workspace.needsAttention') }}</h3>
            </div>
            <div class="document-list">
              <div
                v-for="item in insights.needs_attention"
                :key="item.id"
                class="document-row detail-row"
              >
                <div class="document-main">
                  <strong>{{ item.original_filename }}</strong>
                  <span>{{ reasonLabel(item) }}</span>
                </div>
                <span class="badge-chip danger-chip">{{ badgeLabel(item.badge) }}</span>
              </div>
            </div>
          </article>

          <article class="panel-card collection-card">
            <div class="section-head">
              <h3>{{ t('workspace.recentlyUploaded') }}</h3>
            </div>
            <div class="document-list">
              <div
                v-for="item in insights.recently_uploaded"
                :key="item.id"
                class="document-row detail-row"
              >
                <div class="document-main">
                  <strong>{{ item.original_filename }}</strong>
                  <span>{{ formatDateTime(item.created_at) }}</span>
                </div>
                <span class="badge-chip">{{
                  item.has_summary ? t('workspace.summaryReady') : t('workspace.summaryMissing')
                }}</span>
              </div>
            </div>
          </article>
        </div>
      </template>
    </template>
  </section>
</template>

<style scoped>
  .workspace-page {
    padding: 1.5rem 2rem 2rem;
    display: grid;
    gap: 1.25rem;
  }

  .workspace-loading,
  .workspace-empty,
  .action-empty {
    display: grid;
    place-items: center;
    gap: 0.75rem;
    padding: 2.5rem;
    border-radius: 28px;
    border: 1px solid var(--panel-border);
    background:
      radial-gradient(circle at top left, rgba(37, 99, 235, 0.14), transparent 40%),
      linear-gradient(160deg, var(--panel-bg), color-mix(in srgb, var(--panel-bg) 88%, white 12%));
    box-shadow: var(--shadow-md);
    text-align: center;
  }

  .loading-orb,
  .empty-illustration {
    width: 64px;
    height: 64px;
    border-radius: 50%;
    background: radial-gradient(circle at 30% 30%, #60a5fa, #1d4ed8 70%);
    box-shadow: 0 18px 44px rgba(37, 99, 235, 0.22);
  }

  .loading-orb {
    animation: pulse 1.4s ease-in-out infinite;
  }

  .workspace-hero {
    display: grid;
    grid-template-columns: minmax(0, 1.6fr) minmax(300px, 0.85fr);
    gap: 1rem;
  }

  .hero-copy,
  .hero-score-card,
  .metric-card,
  .activity-card,
  .panel-card,
  .action-card {
    border-radius: 28px;
    border: 1px solid var(--panel-border);
    background:
      linear-gradient(180deg, color-mix(in srgb, var(--panel-bg) 90%, white 10%), var(--panel-bg)),
      var(--panel-bg);
    box-shadow: var(--shadow-md);
  }

  .hero-copy {
    padding: 1.6rem 1.7rem;
    background:
      radial-gradient(circle at top left, rgba(37, 99, 235, 0.18), transparent 42%),
      linear-gradient(160deg, color-mix(in srgb, var(--panel-bg) 80%, white 20%), var(--panel-bg));
  }

  .hero-kicker {
    display: inline-flex;
    padding: 0.3rem 0.7rem;
    border-radius: 999px;
    background: rgba(37, 99, 235, 0.12);
    color: var(--primary);
    font-size: 0.72rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.08em;
  }

  .hero-title {
    margin: 0.9rem 0 0;
    font-size: clamp(2rem, 3vw, 2.8rem);
    line-height: 1.05;
    max-width: 14ch;
    color: var(--text);
  }

  .hero-text {
    margin: 0.95rem 0 0;
    max-width: 62ch;
    color: var(--text-muted);
    font-size: 0.96rem;
    line-height: 1.65;
  }

  .hero-actions {
    display: flex;
    gap: 0.75rem;
    margin-top: 1.2rem;
  }

  .hero-btn {
    border-radius: 14px;
    padding: 0.85rem 1.1rem;
    font-weight: 700;
    border: 1px solid transparent;
  }

  .hero-btn-primary {
    background: linear-gradient(135deg, #2563eb, #1d4ed8);
    color: white;
    box-shadow: 0 16px 36px rgba(37, 99, 235, 0.2);
  }

  .hero-btn-secondary {
    background: rgba(37, 99, 235, 0.08);
    color: var(--primary);
    border-color: rgba(37, 99, 235, 0.16);
  }

  .hero-score-card {
    padding: 1.5rem;
    display: grid;
    place-items: center;
    gap: 1rem;
    text-align: center;
  }

  .score-ring {
    width: 176px;
    height: 176px;
    border-radius: 50%;
    display: grid;
    place-items: center;
    padding: 16px;
  }

  .score-ring-inner {
    width: 100%;
    height: 100%;
    border-radius: 50%;
    background: color-mix(in srgb, var(--panel-bg) 90%, white 10%);
    display: grid;
    place-items: center;
    align-content: center;
    gap: 0.25rem;
  }

  .score-ring-inner strong {
    font-size: 2.6rem;
    line-height: 1;
    color: var(--text);
  }

  .score-ring-inner span,
  .score-meta p,
  .metric-card span,
  .activity-card span,
  .document-main span,
  .tag-empty,
  .action-card p {
    color: var(--text-muted);
  }

  .score-label {
    display: block;
    font-size: 0.82rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    color: var(--primary);
  }

  .score-meta p {
    margin: 0.45rem 0 0;
    max-width: 28ch;
    line-height: 1.55;
  }

  .workspace-metrics,
  .activity-strip,
  .chart-grid,
  .collections-grid,
  .action-grid {
    display: grid;
    gap: 1rem;
  }

  .workspace-metrics {
    grid-template-columns: repeat(4, minmax(0, 1fr));
  }

  .metric-card,
  .activity-card {
    padding: 1.1rem 1.2rem;
  }

  .metric-card strong,
  .activity-card strong {
    display: block;
    margin-top: 0.35rem;
    font-size: 1.55rem;
    color: var(--text);
  }

  .accent-primary {
    box-shadow:
      inset 0 0 0 1px rgba(37, 99, 235, 0.08),
      var(--shadow-md);
  }

  .accent-cyan {
    box-shadow:
      inset 0 0 0 1px rgba(14, 165, 233, 0.08),
      var(--shadow-md);
  }

  .accent-slate {
    box-shadow:
      inset 0 0 0 1px rgba(71, 85, 105, 0.08),
      var(--shadow-md);
  }

  .accent-indigo {
    box-shadow:
      inset 0 0 0 1px rgba(79, 70, 229, 0.08),
      var(--shadow-md);
  }

  .activity-strip {
    grid-template-columns: repeat(5, minmax(0, 1fr));
  }

  .activity-card-wide {
    grid-column: span 1;
  }

  .action-card {
    padding: 1.15rem 1.2rem;
    position: relative;
    overflow: hidden;
  }

  .action-grid {
    grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
  }

  .severity-pill,
  .badge-chip,
  .status-chip {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    border-radius: 999px;
    padding: 0.24rem 0.58rem;
    font-size: 0.7rem;
    font-weight: 700;
  }

  .severity-high .severity-pill,
  .danger-chip {
    background: rgba(239, 68, 68, 0.12);
    color: #dc2626;
  }

  .severity-medium .severity-pill {
    background: rgba(245, 158, 11, 0.12);
    color: #b45309;
  }

  .severity-low .severity-pill,
  .badge-chip,
  .status-chip {
    background: rgba(37, 99, 235, 0.1);
    color: var(--primary);
  }

  .action-card h4,
  .section-head h3 {
    margin: 0.75rem 0 0;
    color: var(--text);
  }

  .panel-card {
    padding: 1.2rem;
  }

  .chart-grid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }

  .chart-wrap {
    height: 260px;
  }

  .status-legend {
    display: grid;
    gap: 0.45rem;
    margin-top: 1rem;
  }

  .legend-row,
  .document-row {
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 0.75rem;
  }

  .legend-row strong,
  .document-score {
    color: var(--text);
    font-weight: 800;
  }

  .collections-grid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }

  .document-list {
    display: grid;
    gap: 0.75rem;
    margin-top: 0.9rem;
  }

  .document-row {
    padding: 0.85rem 0.95rem;
    border-radius: 18px;
    background: color-mix(in srgb, var(--surface-alt) 82%, white 18%);
    border: 1px solid color-mix(in srgb, var(--border-subtle) 82%, white 18%);
  }

  .document-main {
    display: grid;
    gap: 0.2rem;
    min-width: 0;
  }

  .document-main strong {
    color: var(--text);
    word-break: break-word;
  }

  @keyframes pulse {
    0%,
    100% {
      transform: scale(0.96);
      opacity: 0.82;
    }
    50% {
      transform: scale(1.02);
      opacity: 1;
    }
  }

  @media (max-width: 1200px) {
    .workspace-hero,
    .chart-grid,
    .collections-grid {
      grid-template-columns: 1fr;
    }

    .workspace-metrics,
    .activity-strip {
      grid-template-columns: repeat(2, minmax(0, 1fr));
    }
  }

  @media (max-width: 720px) {
    .workspace-page {
      padding: 1rem;
    }

    .workspace-metrics,
    .activity-strip,
    .action-grid {
      grid-template-columns: 1fr;
    }

    .hero-actions {
      flex-direction: column;
    }

    .score-ring {
      width: 150px;
      height: 150px;
    }
  }
</style>
