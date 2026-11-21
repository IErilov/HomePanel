<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { RouterLink, useRoute, useRouter } from 'vue-router'
import { Files, LogIn, LogOut, Moon, PanelsTopLeft, Sun, UserRound } from 'lucide-vue-next'
import { useAuthStore } from '../stores/auth'

const auth = useAuthStore()
const route = useRoute()
const router = useRouter()
const dark = ref(localStorage.getItem('hp_theme') === 'dark')
const pageTitle = computed(() => route.name === 'files' ? 'Файловое пространство' : 'Home portal')

function toggleTheme() {
  dark.value = !dark.value
  localStorage.setItem('hp_theme', dark.value ? 'dark' : 'light')
  document.documentElement.dataset.theme = dark.value ? 'dark' : 'light'
}

function logout() {
  auth.logout()
  router.push('/login')
}

onMounted(() => {
  document.documentElement.dataset.theme = dark.value ? 'dark' : 'light'
  if (auth.isAuthenticated() && !auth.user) {
    auth.fetchMe().catch(() => {
      auth.logout()
      router.push('/login')
    })
  }
})
</script>

<template>
  <div class="app-shell">
    <aside class="sidebar">
      <RouterLink to="/app" class="brand">
        <span class="brand-copy">
          <strong>Home portal</strong>
          <small>by Erilov Ilya</small>
        </span>
      </RouterLink>

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
          <span class="brand-mark"><PanelsTopLeft :size="17" /></span>
          <span><strong>Home portal</strong><small>by Erilov Ilya</small></span>
        </RouterLink>
        <div class="breadcrumbs"></div>
        <div class="top-actions">
          <button class="icon-button" @click="toggleTheme" :aria-label="dark ? 'Светлая тема' : 'Тёмная тема'">
            <Sun v-if="dark" :size="17" /><Moon v-else :size="17" />
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
