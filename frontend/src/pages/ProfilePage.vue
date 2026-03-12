<script setup>
  import { computed } from 'vue'
  import { useStore } from '../composables/useStore'

  const {
    currentUser,
    documents,
    summaryCount,
    questionsCount,
    formatDate,
    formatDateTime,
    t,
    translateRole,
    translateStatus,
  } = useStore()

  const totalSize = computed(() => {
    const bytes = documents.value.reduce((sum, d) => sum + (d.size_bytes || 0), 0)
    if (bytes < 1024) return bytes + ' B'
    if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB'
    return (bytes / (1024 * 1024)).toFixed(1) + ' MB'
  })

  const processedPercent = computed(() => {
    if (!documents.value.length) return 0
    return Math.round((summaryCount.value / documents.value.length) * 100)
  })

  const latestDocument = computed(() => documents.value[0] || null)
</script>

<template>
  <section class="page">
    <div class="profile-hero">
      <div class="profile-card-wrap">
        <div class="profile-avatar-lg">
          {{ currentUser.full_name?.charAt(0)?.toUpperCase() }}
        </div>
        <div class="profile-headline">
          <span class="profile-kicker">{{ t('profile.kicker') }}</span>
          <h2 class="profile-name">{{ currentUser.full_name }}</h2>
          <p class="profile-subtitle">{{ t('profile.subtitle') }}</p>
        </div>
        <span class="profile-role-tag" :class="'role-tag-' + currentUser.role">{{
          translateRole(currentUser.role)
        }}</span>
      </div>

      <div class="profile-summary-grid">
        <div class="summary-card">
          <strong>{{ documents.length }}</strong>
          <span>{{ t('profile.docsCollection') }}</span>
        </div>
        <div class="summary-card">
          <strong>{{ summaryCount }}</strong>
          <span>{{ t('profile.readySummaries') }}</span>
        </div>
        <div class="summary-card">
          <strong>{{ processedPercent }}%</strong>
          <span>{{ t('profile.completionRate') }}</span>
        </div>
      </div>
    </div>

    <div class="profile-panels">
      <div class="profile-panel">
        <div class="panel-header">
          <h3>{{ t('profile.basics') }}</h3>
          <span class="panel-chip">{{ t('profile.account') }}</span>
        </div>
        <div class="info-grid">
          <div class="info-item">
            <span class="info-label">{{ t('common.email') }}</span>
            <span class="info-value">{{ currentUser.email }}</span>
          </div>
          <div class="info-item">
            <span class="info-label">{{ t('profile.role') }}</span>
            <span class="info-value capitalize">{{ translateRole(currentUser.role) }}</span>
          </div>
          <div class="info-item">
            <span class="info-label">{{ t('profile.documents') }}</span>
            <span class="info-value">{{ documents.length }}</span>
          </div>
          <div class="info-item">
            <span class="info-label">{{ t('profile.summaries') }}</span>
            <span class="info-value">{{ summaryCount }}</span>
          </div>
          <div class="info-item">
            <span class="info-label">{{ t('profile.questions') }}</span>
            <span class="info-value">{{ questionsCount }}</span>
          </div>
          <div class="info-item">
            <span class="info-label">{{ t('profile.totalSize') }}</span>
            <span class="info-value">{{ totalSize }}</span>
          </div>
          <div class="info-item">
            <span class="info-label">{{ t('profile.registered') }}</span>
            <span class="info-value">{{ formatDateTime(currentUser.created_at) || '—' }}</span>
          </div>
          <div class="info-item">
            <span class="info-label">{{ t('profile.lastLogin') }}</span>
            <span class="info-value">{{ formatDateTime(currentUser.last_login_at) || '—' }}</span>
          </div>
        </div>
      </div>

      <div class="profile-panel profile-panel-side">
        <div class="panel-header">
          <h3>{{ t('profile.recentActivity') }}</h3>
          <span class="panel-chip">{{ t('profile.overview') }}</span>
        </div>

        <div class="activity-card">
          <span class="activity-label">{{ t('profile.latestDocument') }}</span>
          <strong>{{
            latestDocument?.original_filename || t('profile.noUploadedDocument')
          }}</strong>
          <p>
            {{
              latestDocument
                ? `${formatDate(latestDocument.created_at) || t('profile.today')} · ${translateStatus(latestDocument.processing_status)}`
                : t('profile.latestDocFallback')
            }}
          </p>
        </div>

        <div class="activity-list">
          <div class="activity-row">
            <span>{{ t('profile.collectionSize') }}</span>
            <strong>{{ totalSize }}</strong>
          </div>
          <div class="activity-row">
            <span>{{ t('profile.docQuestions') }}</span>
            <strong>{{ questionsCount }}</strong>
          </div>
          <div class="activity-row">
            <span>{{ t('profile.processedDocs') }}</span>
            <strong>{{ processedPercent }}%</strong>
          </div>
        </div>
      </div>
    </div>
  </section>
</template>

<style scoped>
  .page {
    flex: 1;
    padding: 1.5rem 2rem;
  }

  .profile-hero {
    display: grid;
    grid-template-columns: minmax(0, 1.2fr) minmax(260px, 0.8fr);
    gap: 1rem;
    margin-bottom: 1.25rem;
  }

  .profile-card-wrap {
    display: flex;
    align-items: center;
    gap: 1rem;
    padding: 1.5rem;
    background: var(--panel-bg);
    border: 1px solid var(--panel-border);
    border-radius: 24px;
    box-shadow: var(--shadow-md);
    backdrop-filter: blur(12px);
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
    flex-shrink: 0;
  }

  .profile-headline {
    flex: 1;
  }

  .profile-kicker {
    display: inline-block;
    margin-bottom: 0.35rem;
    padding: 0.24rem 0.55rem;
    border-radius: 999px;
    background: var(--primary-light);
    color: var(--primary);
    font-size: 0.7rem;
    font-weight: 700;
    letter-spacing: 0.08em;
    text-transform: uppercase;
  }

  .profile-name {
    margin: 0;
    font-size: 1.35rem;
    font-weight: 700;
    color: var(--text);
  }

  .profile-subtitle {
    margin: 0.35rem 0 0;
    color: var(--text-muted);
    line-height: 1.55;
  }

  .profile-role-tag {
    display: inline-block;
    padding: 0.2rem 0.7rem;
    border-radius: 999px;
    font-size: 0.72rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.04em;
    flex-shrink: 0;
  }

  .role-tag-admin {
    background: #fef3c7;
    color: #92400e;
  }
  .role-tag-user {
    background: var(--primary-light);
    color: var(--primary);
  }

  .profile-summary-grid {
    display: grid;
    grid-template-columns: repeat(3, minmax(0, 1fr));
    gap: 0.75rem;
  }

  .summary-card {
    padding: 1rem;
    background: var(--panel-bg);
    border: 1px solid var(--panel-border);
    border-radius: 22px;
    box-shadow: var(--shadow-sm);
    text-align: center;
  }

  .summary-card strong {
    display: block;
    margin-bottom: 0.2rem;
    font-size: 1.35rem;
    color: var(--primary);
  }

  .summary-card span {
    font-size: 0.76rem;
    line-height: 1.45;
    color: var(--text-muted);
  }

  .profile-panels {
    display: grid;
    grid-template-columns: minmax(0, 1.35fr) minmax(280px, 0.85fr);
    gap: 1rem;
  }

  .profile-panel {
    padding: 1.2rem;
    background: var(--panel-bg);
    border: 1px solid var(--panel-border);
    border-radius: 24px;
    box-shadow: var(--shadow-md);
    backdrop-filter: blur(12px);
  }

  .panel-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 0.75rem;
    margin-bottom: 0.9rem;
  }

  .panel-header h3 {
    margin: 0;
    font-size: 1rem;
    color: var(--text);
  }

  .panel-chip {
    padding: 0.25rem 0.55rem;
    border-radius: 999px;
    background: var(--surface-alt);
    color: var(--text-muted);
    font-size: 0.7rem;
    font-weight: 700;
  }

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

  .capitalize {
    text-transform: capitalize;
  }

  .activity-card {
    padding: 1rem;
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 18px;
    margin-bottom: 0.9rem;
  }

  .activity-label {
    display: inline-block;
    margin-bottom: 0.45rem;
    font-size: 0.68rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    color: var(--primary);
  }

  .activity-card strong {
    display: block;
    margin-bottom: 0.3rem;
    color: var(--text);
  }

  .activity-card p {
    margin: 0;
    color: var(--text-muted);
    line-height: 1.55;
    font-size: 0.82rem;
  }

  .activity-list {
    display: grid;
    gap: 0.6rem;
  }

  .activity-row {
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 1rem;
    padding: 0.85rem 0.95rem;
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 16px;
    font-size: 0.84rem;
    color: var(--text-muted);
  }

  .activity-row strong {
    color: var(--text);
  }

  @media (max-width: 860px) {
    .page {
      padding: 1.25rem 1rem;
    }
    .profile-hero,
    .profile-panels,
    .profile-summary-grid {
      grid-template-columns: 1fr;
    }
    .profile-card-wrap {
      flex-direction: column;
      align-items: flex-start;
    }
  }

  @media (max-width: 540px) {
    .info-grid {
      grid-template-columns: 1fr;
    }
  }
</style>
