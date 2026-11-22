<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { RouterLink, useRoute, useRouter } from 'vue-router'
import { Files, LogIn, LogOut, Moon, Sun, UserRound } from 'lucide-vue-next'
import { useAuthStore } from '../stores/auth'

const auth = useAuthStore()
const route = useRoute()
const router = useRouter()
const dark = ref(localStorage.getItem('hp_theme') === 'dark')
const pageTitle = computed(() => route.name === 'files' ? 'Файловое пространство' : 'Home portal')

function toggleTheme() {
  dark.value = !dark.value
  localStorage.setItem('hp_theme', dark.value ? 'dark' : 'light')
  const root = document.documentElement
  root.classList.add('theme-changing')
  root.dataset.theme = dark.value ? 'dark' : 'light'
  root.style.colorScheme = dark.value ? 'dark' : 'light'
  window.setTimeout(() => root.classList.remove('theme-changing'), 280)
}

function logout() {
  auth.logout()
  router.push('/login')
}

onMounted(() => {
  document.documentElement.dataset.theme = dark.value ? 'dark' : 'light'
  document.documentElement.style.colorScheme = dark.value ? 'dark' : 'light'
})
</script>

<template>
  <div class="app-shell">
    <aside class="sidebar">
      <RouterLink to="/app" class="brand">
        <span class="brand-mark"><img src="/brand-mark.svg" alt="" /></span>
        <span class="brand-copy">
          <strong>Home portal</strong>
          <small>by Erilov Ilya</small>
        </span>
      </RouterLink>

      <p class="side-caption">РАБОЧЕЕ ПРОСТРАНСТВО</p>
      <nav class="side-nav">
        <RouterLink to="/app" class="side-link" :class="{ active: route.name === 'files' }">
          <Files :size="18" /> Файловое пространство
        </RouterLink>
      </nav>

      <div class="sidebar-bottom">
        <div v-if="auth.user" class="user-block">
          <span class="user-avatar"><UserRound :size="17" /></span>
          <span class="user-copy"><strong>{{ auth.user.name }}</strong><small>{{ auth.user.role }}</small></span>
        </div>
        <button v-if="auth.isAuthenticated()" class="side-link side-logout" @click="logout">
          <LogOut :size="17" /> Выйти
        </button>
        <RouterLink v-else to="/login" class="side-link"><LogIn :size="17" /> Войти</RouterLink>
      </div>
    </aside>

    <main class="main-area">
      <header class="topbar">
        <RouterLink to="/app" class="mobile-brand">
          <span class="brand-mark"><img src="/brand-mark.svg" alt="" /></span>
          <span><strong>Home portal</strong><small>by Erilov Ilya</small></span>
        </RouterLink>
        <div class="breadcrumbs"><span>Home portal</span><span>/</span><strong>{{ pageTitle }}</strong></div>
        <div class="top-actions">
          <button
            class="theme-toggle"
            :class="{ 'is-dark': dark }"
            type="button"
            @click="toggleTheme"
            :aria-label="dark ? 'Переключить на светлую тему' : 'Переключить на тёмную тему'"
            :aria-pressed="dark"
            title="Сменить тему"
          >
            <span class="theme-toggle-track" aria-hidden="true">
              <span class="theme-toggle-thumb">
                <Moon v-if="dark" :size="14" class="theme-icon moon-icon" />
                <Sun v-else :size="14" class="theme-icon sun-icon" />
              </span>
              <span class="theme-stars" aria-hidden="true">✦</span>
            </span>
          </button>
          <span v-if="auth.user" class="top-user"><UserRound :size="16" /> {{ auth.user.name }}</span>
          <RouterLink v-else to="/login" class="top-login">Войти</RouterLink>
        </div>
      </header>
      <div class="page-content"><slot /></div>
      <footer class="app-footer"><span>Home portal</span><span>by Erilov Ilya</span></footer>
    </main>
  </div>
</template>
