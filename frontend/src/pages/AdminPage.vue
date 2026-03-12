<script setup>
  import { useStore } from '../composables/useStore'

  const { adminStats, adminUsers, currentUser, handleSetRole, formatDate } = useStore()
</script>

<template>
  <section class="page">
    <div class="stats-row" v-if="adminStats">
      <div class="stat-tile">
        <span class="stat-num">{{ adminStats.users }}</span
        ><span class="stat-lbl">Uporabnikov</span>
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
              <td class="td-date">{{ formatDate(u.created_at) }}</td>
              <td class="td-date">{{ formatDate(u.last_login_at) || '—' }}</td>
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
                    Admin
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
</template>

<style scoped>
  .page {
    flex: 1;
    padding: 1.5rem 2rem;
  }

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
    .stats-row {
      grid-template-columns: repeat(2, 1fr);
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
