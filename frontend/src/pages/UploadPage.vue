<script setup>
  import { computed } from 'vue'
  import { useStore } from '../composables/useStore'
  import { useRouter } from 'vue-router'
  import UploadSection from '../components/UploadSection.vue'

  const router = useRouter()
  const { uploadBusy, documents, summaryCount, handleUpload: storeUpload, refreshDocuments } =
    useStore()

  const readyCount = computed(() =>
    documents.value.filter((document) => document.processing_status === 'ready').length,
  )

  async function onUpload(file, done) {
    try {
      const ok = await storeUpload(file)
      if (done) done(ok)
      if (ok) await refreshDocuments()
    } catch {
      if (done) done(false)
    }
  }
</script>

<template>
  <section class="page">
    <div class="upload-shell">
      <div class="upload-intro">
        <span class="upload-kicker">Nalaganje dokumentov</span>
        <h2 class="upload-title">Pripravi dokumente za analizo in nadaljnjo obdelavo.</h2>
        <p class="upload-text">
          Tukaj naložiš eno ali več PDF datotek, spremljaš pripravljenost sistema in nato nadaljuješ v pregled dokumentov ali povzetkov.
        </p>

        <div class="upload-highlights">
          <div class="highlight-card">
            <strong>{{ documents.length }}</strong>
            <span>Skupaj dokumentov</span>
          </div>
          <div class="highlight-card">
            <strong>{{ summaryCount }}</strong>
            <span>Pripravljenih povzetkov</span>
          </div>
          <div class="highlight-card">
            <strong>{{ readyCount }}</strong>
            <span>Dokumentov pripravljenih za vprašanja</span>
          </div>
        </div>

        <div class="upload-actions">
          <button class="btn-primary" @click="router.push('/documents')">Odpri dokumente</button>
        </div>
      </div>

      <div class="upload-side-notes">
        <div class="note-card">
          <span class="note-label">Priporočilo</span>
          <p>Najboljše rezultate dobiš pri PDF datotekah z berljivim besedilom in urejeno strukturo strani.</p>
        </div>
        <div class="note-card">
          <span class="note-label">Nadaljevanje</span>
          <p>Po nalaganju odpri predogled, sproži povzetek in nato uporabi vprašanja za podrobnejšo analizo vsebine.</p>
        </div>
      </div>
    </div>

    <div class="upload-wrap">
      <UploadSection :busy="uploadBusy" @upload="onUpload" />
    </div>
  </section>
</template>

<style scoped>
  .page {
    flex: 1;
    padding: 1.5rem 2rem;
  }

  .upload-shell {
    display: grid;
    grid-template-columns: minmax(0, 1.4fr) minmax(280px, 0.8fr);
    gap: 1rem;
    margin-bottom: 1.25rem;
  }

  .upload-intro,
  .upload-side-notes {
    background: rgba(255, 255, 255, 0.72);
    border: 1px solid rgba(255, 255, 255, 0.62);
    border-radius: 24px;
    box-shadow: var(--shadow-md);
    backdrop-filter: blur(12px);
  }

  .upload-intro {
    padding: 1.4rem 1.5rem;
  }

  .upload-kicker {
    display: inline-block;
    margin-bottom: 0.55rem;
    padding: 0.28rem 0.58rem;
    border-radius: 999px;
    background: var(--primary-light);
    color: var(--primary);
    font-size: 0.7rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.08em;
  }

  .upload-title {
    margin: 0;
    max-width: 16ch;
    font-size: clamp(1.8rem, 3vw, 2.4rem);
    line-height: 1.05;
    color: var(--text);
  }

  .upload-text {
    margin: 0.9rem 0 1.15rem;
    max-width: 62ch;
    line-height: 1.7;
    color: var(--text-muted);
  }

  .upload-highlights {
    display: grid;
    grid-template-columns: repeat(3, minmax(0, 1fr));
    gap: 0.75rem;
  }

  .highlight-card {
    padding: 1rem;
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 18px;
  }

  .highlight-card strong {
    display: block;
    margin-bottom: 0.2rem;
    font-size: 1.2rem;
    color: var(--primary);
  }

  .highlight-card span {
    font-size: 0.77rem;
    line-height: 1.45;
    color: var(--text-muted);
  }

  .upload-actions {
    margin-top: 1rem;
  }

  .btn-primary {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    padding: 0.75rem 1.15rem;
    border: none;
    border-radius: 12px;
    background: linear-gradient(135deg, var(--primary), #818cf8);
    color: white;
    font-weight: 600;
    box-shadow: 0 6px 18px rgba(99, 102, 241, 0.22);
    cursor: pointer;
  }

  .upload-side-notes {
    display: grid;
    gap: 0.8rem;
    padding: 1rem;
  }

  .note-card {
    padding: 1rem;
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 18px;
  }

  .note-label {
    display: inline-block;
    margin-bottom: 0.5rem;
    font-size: 0.68rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    color: var(--primary);
  }

  .note-card p {
    margin: 0;
    line-height: 1.65;
    color: var(--text-muted);
    font-size: 0.84rem;
  }

  .upload-wrap {
    max-width: 100%;
  }

  @media (max-width: 860px) {
    .page {
      padding: 1.25rem 1rem;
    }
    .upload-shell,
    .upload-highlights {
      grid-template-columns: 1fr;
    }
  }
</style>
