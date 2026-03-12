<script setup>
  import { computed } from 'vue'
  import { useStore } from '../composables/useStore'

  const { currentUser, documents, summaryCount, questionsCount, formatDate, formatDateTime } =
    useStore()

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
</script>

<template>
  <section class="page">
    <div class="profile-card-wrap">
      <div class="profile-avatar-lg">
        {{ currentUser.full_name?.charAt(0)?.toUpperCase() }}
      </div>
      <h2 class="profile-name">{{ currentUser.full_name }}</h2>
      <span class="profile-role-tag" :class="'role-tag-' + currentUser.role">{{
        currentUser.role
      }}</span>
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
      <div class="info-item">
        <span class="info-label">Vprašanja</span>
        <span class="info-value">{{ questionsCount }}</span>
      </div>
      <div class="info-item">
        <span class="info-label">Skupna velikost</span>
        <span class="info-value">{{ totalSize }}</span>
      </div>
      <div class="info-item">
        <span class="info-label">Obdelanih</span>
        <span class="info-value">{{ processedPercent }}%</span>
      </div>
      <div class="info-item">
        <span class="info-label">Registriran</span>
        <span class="info-value">{{ formatDateTime(currentUser.created_at) || '—' }}</span>
      </div>
      <div class="info-item">
        <span class="info-label">Zadnja prijava</span>
        <span class="info-value">{{ formatDateTime(currentUser.last_login_at) || '—' }}</span>
      </div>
    </div>
  </section>
</template>

<style scoped>
  .page {
    flex: 1;
    padding: 1.5rem 2rem;
  }

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

  .role-tag-admin {
    background: #fef3c7;
    color: #92400e;
  }
  .role-tag-user {
    background: var(--primary-light);
    color: var(--primary);
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

  @media (max-width: 860px) {
    .page {
      padding: 1.25rem 1rem;
    }
  }

  @media (max-width: 540px) {
    .info-grid {
      grid-template-columns: 1fr;
    }
  }
</style>
