<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { RouterLink } from 'vue-router'
import { ArrowRight, Cloud, FolderOpen, Globe2, HardDrive, LockKeyhole } from 'lucide-vue-next'
import { api, errorMessage } from '../api'
import type { Bucket } from '../types'

const buckets = ref<Bucket[]>([])
const normalizeBucketType = (value: string | null | undefined) => (value || '').trim().toUpperCase()
const loading = ref(true)
const error = ref('')
const openBuckets = computed(() => buckets.value.filter(bucket => normalizeBucketType(bucket.bucket_type) === 'OPEN'))

onMounted(async () => {
  try {
    const { data } = await api.get<{ buckets: Bucket[] }>('/api/buckets/')
    buckets.value = data.buckets || []
  } catch (e) {
    error.value = errorMessage(e)
  } finally {
    loading.value = false
  }
})
</script>

<template>
  <div class="landing">
    <header class="landing-nav">
      <RouterLink to="/" class="brand">
        <span class="brand-mark"><Cloud :size="20" /></span>
        <span><strong>HOME PANEL</strong><small>PERSONAL CLOUD</small></span>
      </RouterLink>
      <RouterLink to="/login" class="primary-button nav-login">Войти <ArrowRight :size="15" /></RouterLink>
    </header>

    <main class="landing-main">
      <section class="hero">
        <div class="hero-copy">
          <p class="eyebrow"><span class="online-dot"></span> ВАШЕ ФАЙЛОВОЕ ПРОСТРАНСТВО</p>
          <h1>Файлы.<br><span>Всё на своих местах.</span></h1>
          <p class="hero-description">Home Panel — простое пространство для хранения и управления файлами. Общие материалы доступны для просмотра, личные — после входа в аккаунт.</p>
          <div class="hero-actions">
            <RouterLink to="/login" class="primary-button hero-button">Открыть хранилище <ArrowRight :size="16" /></RouterLink>
            <a href="#public" class="text-link">Публичные файлы</a>
          </div>
        </div>
        <div class="hero-visual" aria-hidden="true">
          <div class="visual-card">
            <div class="visual-card-head"><span class="visual-cloud"><Cloud :size="22" /></span><span class="live-label"><i></i> ВАШЕ ОБЛАКО</span></div>
            <div class="visual-title">Всё под рукой</div>
            <div class="visual-row"><span class="visual-icon"><FolderOpen :size="17" /></span><span>Документы</span><small>PDF · DOCX</small></div>
            <div class="visual-row"><span class="visual-icon"><HardDrive :size="17" /></span><span>Хранилище</span><small>Файлы</small></div>
            <div class="visual-row"><span class="visual-icon"><LockKeyhole :size="17" /></span><span>Личное</span><small>Приватно</small></div>
          </div>
        </div>
      </section>

      <section class="feature-row">
        <div><Globe2 :size="19" /><span><strong>Общий доступ</strong><small>Публичные материалы</small></span></div>
        <div><LockKeyhole :size="19" /><span><strong>Личное хранилище</strong><small>Только после входа</small></span></div>
        <div><HardDrive :size="19" /><span><strong>Простое управление</strong><small>Загрузка и работа с файлами</small></span></div>
      </section>

      <section id="public" class="public-section">
        <div class="section-heading">
          <div><p class="eyebrow">ОТКРЫТЫЙ ДОСТУП</p><h2>Публичные хранилища</h2></div>
          <span class="section-caption">Доступны без авторизации</span>
        </div>
        <div v-if="loading" class="state-message">Загружаем хранилища…</div>
        <div v-else-if="error" class="state-message state-error">{{ error }}</div>
        <div v-else-if="!openBuckets.length" class="state-message">Публичных хранилищ пока нет.</div>
        <div v-else class="bucket-grid">
          <RouterLink v-for="bucket in openBuckets" :key="bucket.id" :to="{ path: '/app', query: { bucket: bucket.id } }" class="bucket-card">
            <span class="bucket-icon"><HardDrive :size="20" /></span>
            <span class="bucket-copy"><strong>{{ bucket.name }}</strong><small>Общее хранилище</small></span>
            <ArrowRight :size="17" class="bucket-arrow" />
          </RouterLink>
        </div>
      </section>
    </main>

    <footer class="landing-footer">
      <span class="footer-brand"><img src="/brand-mark.svg" alt="" /> HOME PORTAL</span>
      <span>Простое пространство для ваших файлов</span>
      <span>© {{ new Date().getFullYear() }}</span>
    </footer>
  </div>
</template>
