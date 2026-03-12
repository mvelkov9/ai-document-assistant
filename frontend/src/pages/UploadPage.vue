<script setup>
  import { useStore } from '../composables/useStore'
  import { useRouter } from 'vue-router'
  import UploadSection from '../components/UploadSection.vue'

  const router = useRouter()
  const { uploadBusy, handleUpload: storeUpload } = useStore()

  async function onUpload(file) {
    const ok = await storeUpload(file)
    if (ok) router.push('/documents')
  }
</script>

<template>
  <section class="page">
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

  .upload-wrap {
    max-width: 640px;
  }

  @media (max-width: 860px) {
    .page {
      padding: 1.25rem 1rem;
    }
  }
</style>
