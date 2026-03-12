<script setup>
  import { useStore } from '../composables/useStore'
  import { useRouter } from 'vue-router'
  import DocumentCard from '../components/DocumentCard.vue'
  import UploadSection from '../components/UploadSection.vue'

  const router = useRouter()
  const {
    documents,
    dashboardBusy,
    searchQuery,
    sortField,
    filteredDocuments,
    activeSummaryId,
    activeQuestionId,
    latestAnswers,
    handleSummarize,
    handleAsk,
    handleDelete,
    handleDownload,
  } = useStore()
</script>

<template>
  <section class="page">
    <div class="toolbar">
      <div class="search-wrap">
        <svg
          viewBox="0 0 24 24"
          fill="none"
          stroke="currentColor"
          stroke-width="2"
          class="search-svg"
        >
          <circle cx="11" cy="11" r="8" />
          <line x1="21" y1="21" x2="16.65" y2="16.65" />
        </svg>
        <input
          v-model="searchQuery"
          type="text"
          placeholder="Išči po imenu datoteke..."
          class="search-input"
        />
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
      <svg
        viewBox="0 0 24 24"
        fill="none"
        stroke="currentColor"
        stroke-width="2"
        class="state-icon spin"
      >
        <path d="M21 12a9 9 0 1 1-6.219-8.56" />
      </svg>
      <span>Nalagam dokumente...</span>
    </div>

    <div v-else-if="!documents.length" class="state-box state-empty">
      <div class="empty-circle">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
          <path d="M13 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V9z" />
          <polyline points="13 2 13 9 20 9" />
        </svg>
      </div>
      <p class="empty-title">Ni dokumentov</p>
      <p class="empty-sub">Naloži prvi PDF za začetek</p>
      <button class="btn-primary-sm" @click="router.push('/upload')">
        <svg
          viewBox="0 0 24 24"
          fill="none"
          stroke="currentColor"
          stroke-width="2"
          class="btn-ico"
        >
          <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4" />
          <polyline points="17 8 12 3 7 8" />
          <line x1="12" y1="3" x2="12" y2="15" />
        </svg>
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
</template>

<style scoped>
  .page {
    flex: 1;
    padding: 1.5rem 2rem;
  }

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
    transition:
      border-color 0.2s,
      box-shadow 0.2s;
  }

  .search-wrap:focus-within {
    border-color: var(--primary);
    box-shadow: var(--shadow-glow);
  }

  .search-svg {
    width: 16px;
    height: 16px;
    color: var(--text-light);
    flex-shrink: 0;
  }

  .search-input {
    border: none;
    outline: none;
    background: transparent;
    font-size: 0.85rem;
    color: var(--text);
    width: 100%;
    font-family: inherit;
  }

  .search-input::placeholder {
    color: var(--text-light);
  }

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

  .sort-select:focus {
    border-color: var(--primary);
    box-shadow: var(--shadow-glow);
  }

  .result-count {
    font-size: 0.78rem;
    color: var(--text-light);
    white-space: nowrap;
  }

  .doc-grid {
    display: grid;
    gap: 1rem;
  }

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

  .state-icon {
    width: 24px;
    height: 24px;
  }

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

  .empty-circle svg {
    width: 28px;
    height: 28px;
    color: var(--text-light);
  }
  .empty-title {
    margin: 0;
    font-weight: 600;
    color: var(--text);
  }
  .empty-sub {
    margin: 0.15rem 0 1rem;
    font-size: 0.85rem;
    color: var(--text-light);
  }

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
    box-shadow: 0 2px 8px rgba(99, 102, 241, 0.25);
  }

  .btn-primary-sm:hover {
    box-shadow: 0 4px 14px rgba(99, 102, 241, 0.35);
  }
  .btn-ico {
    width: 15px;
    height: 15px;
  }

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

  @media (max-width: 860px) {
    .page {
      padding: 1.25rem 1rem;
    }
  }

  @media (max-width: 540px) {
    .toolbar {
      flex-wrap: wrap;
    }
  }
</style>
