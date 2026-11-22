<script setup lang="ts">
import { ref } from 'vue'
import { useRoute, useRouter, RouterLink } from 'vue-router'
import { ArrowLeft, Eye, EyeOff, LockKeyhole, UserRound } from 'lucide-vue-next'
import { useAuthStore } from '../stores/auth'
import { errorMessage } from '../api'

const auth = useAuthStore()
const router = useRouter()
const route = useRoute()
const username = ref('')
const password = ref('')
const showPassword = ref(false)
const error = ref('')

async function submit() {
  error.value = ''
  try {
    await auth.login(username.value.trim(), password.value)
    const redirect = typeof route.query.redirect === 'string' ? route.query.redirect : '/app'
    await router.push(redirect)
  } catch (e) {
    error.value = errorMessage(e)
  }
}
</script>

<template>
  <div class="auth-page">
    <header class="auth-nav">
      <RouterLink to="/" class="brand brand-light">
        <span class="brand-mark"><img src="/brand-mark.svg" alt="" /></span>
        <span class="brand-copy"><strong>Home portal</strong><small>by Erilov Ilya</small></span>
      </RouterLink>
      <RouterLink to="/app" class="back-link"><ArrowLeft :size="16" /> К файлам</RouterLink>
    </header>

    <main class="auth-main">
      <section class="auth-card">
        <div class="auth-mark"><img src="/brand-mark.svg" alt="Home Portal" /></div>
        <p class="eyebrow">ЛИЧНОЕ ПРОСТРАНСТВО</p>
        <h1>Вход в аккаунт</h1>
        <p class="auth-description">Введите свои данные, чтобы продолжить работу с файлами.</p>

        <form class="auth-form" @submit.prevent="submit">
          <label for="username">Имя пользователя</label>
          <div class="input-group auth-field">
            <UserRound :size="17" />
            <input id="username" v-model="username" autocomplete="username" placeholder="Имя пользователя" required />
          </div>

          <label for="password">Пароль</label>
          <div class="input-group auth-field">
            <LockKeyhole :size="17" />
            <input id="password" v-model="password" :type="showPassword ? 'text' : 'password'" autocomplete="current-password" placeholder="Пароль" required />
            <button type="button" class="field-toggle" @click="showPassword = !showPassword" :aria-label="showPassword ? 'Скрыть пароль' : 'Показать пароль'">
              <EyeOff v-if="showPassword" :size="17" />
              <Eye v-else :size="17" />
            </button>
          </div>

          <p v-if="error" class="auth-error">{{ error }}</p>
          <button class="btn btn-primary primary-button auth-submit" type="submit" :disabled="auth.loading">
            {{ auth.loading ? 'Входим…' : 'Войти' }}
          </button>
        </form>
        <p class="auth-note">Доступ к личным файлам есть только после авторизации.</p>
      </section>
    </main>
    <footer class="auth-footer">© {{ new Date().getFullYear() }} Home portal · by Erilov Ilya</footer>
  </div>
</template>
