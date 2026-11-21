
<script setup lang="ts">
import { ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import {
  Eye,
  EyeOff,
  LockKeyhole,
  UserRound,
  ArrowRight,
  ShieldCheck,
} from 'lucide-vue-next'
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

    const redirect =
      typeof route.query.redirect === 'string'
        ? route.query.redirect
        : '/app'

    await router.push(redirect)
  } catch (e) {
    error.value = errorMessage(e)
  }
}
</script>

<template>
  <main class="portal-login">
    <!-- Левая научная панель -->
    <aside class="dna-panel" aria-hidden="true">
      <div class="dna-grid"></div>
      <div class="dna-glow dna-glow-one"></div>
      <div class="dna-glow dna-glow-two"></div>

      <div class="dna-copy">
        <span class="dna-index">CLOUD SERVICE / BY ERILOV ILYA</span>
        <h2>
          Пространство<br />
          ваших данных.
        </h2>
        <p>
          Единая среда для хранения и управления цифровыми файлами у вас под рукой.
        </p>
      </div>

      <svg
        class="dna-art"
        viewBox="0 0 440 900"
        preserveAspectRatio="none"
        fill="none"
        xmlns="http://www.w3.org/2000/svg"
      >
        <defs>
          <linearGradient id="dnaBlue" x1="0" y1="0" x2="1" y2="1">
            <stop offset="0%" stop-color="#A6D9FA" />
            <stop offset="100%" stop-color="#3986C8" />
          </linearGradient>

          <linearGradient id="dnaMint" x1="0" y1="0" x2="1" y2="1">
            <stop offset="0%" stop-color="#C0F0E7" />
            <stop offset="100%" stop-color="#63B8AD" />
          </linearGradient>
        </defs>

        <path
          class="dna-strand dna-strand-blue"
          d="M75 0 C 400 150, 400 300, 220 450 C 40 600, 40 750, 365 900"
          stroke="url(#dnaBlue)"
          stroke-width="3"
          stroke-linecap="round"
        />

        <path
          class="dna-strand dna-strand-mint"
          d="M365 0 C 40 150, 40 300, 220 450 C 400 600, 400 750, 75 900"
          stroke="url(#dnaMint)"
          stroke-width="3"
          stroke-linecap="round"
        />

        <g class="dna-rungs">
          <path d="M120 42 L320 42" />
          <path d="M175 117 L265 117" />
          <path d="M245 192 L195 192" />
          <path d="M290 267 L150 267" />
          <path d="M290 342 L150 342" />
          <path d="M220 417 L220 417" />
          <path d="M150 492 L290 492" />
          <path d="M150 567 L290 567" />
          <path d="M195 642 L245 642" />
          <path d="M265 717 L175 717" />
          <path d="M320 792 L120 792" />
          <path d="M365 867 L75 867" />
        </g>

        <g class="dna-particles">
          <circle cx="120" cy="42" r="5" />
          <circle cx="265" cy="117" r="4" />
          <circle cx="245" cy="192" r="5" />
          <circle cx="150" cy="267" r="4" />
          <circle cx="290" cy="342" r="5" />
          <circle cx="220" cy="417" r="4" />
          <circle cx="150" cy="492" r="5" />
          <circle cx="290" cy="567" r="4" />
          <circle cx="195" cy="642" r="5" />
          <circle cx="175" cy="717" r="4" />
          <circle cx="320" cy="792" r="5" />
          <circle cx="75" cy="867" r="4" />
        </g>
      </svg>
    </aside>

    <!-- Правая панель авторизации -->
    <section class="login-panel">
      <header class="login-topbar">
        <div class="author-mark">
        </div>
      </header>

      <div class="login-content">
        <div class="login-heading">

          <h1>Добро пожаловать</h1>

          <p>
            Войдите в систему, чтобы получить доступ
            к своему файловому пространству.
          </p>
        </div>

        <form class="login-form" @submit.prevent="submit">
          <div class="login-field-group">
            <label for="portal-username">
              Имя пользователя
            </label>

            <div class="login-input-wrap">
              <UserRound :size="18" :stroke-width="1.7" />

              <input
                id="portal-username"
                v-model="username"
                type="text"
                autocomplete="username"
                placeholder="Ваше имя пользователя"
                required
              />
            </div>
          </div>

          <div class="login-field-group">
            <label for="portal-password">
              Пароль
            </label>

            <div class="login-input-wrap">
              <LockKeyhole :size="18" :stroke-width="1.7" />

              <input
                id="portal-password"
                v-model="password"
                :type="showPassword ? 'text' : 'password'"
                autocomplete="current-password"
                placeholder="Ваш пароль"
                required
              />

              <button
                class="login-password-toggle"
                type="button"
                :aria-label="showPassword ? 'Скрыть пароль' : 'Показать пароль'"
                @click="showPassword = !showPassword"
              >
                <EyeOff v-if="showPassword" :size="18" />
                <Eye v-else :size="18" />
              </button>
            </div>
          </div>

          <p v-if="error" class="login-error" role="alert">
            {{ error }}
          </p>

          <button
            class="login-submit"
            type="submit"
            :disabled="auth.loading"
          >
            <span>
              {{ auth.loading ? 'Выполняется вход...' : 'Войти в систему' }}
            </span>

            <ArrowRight v-if="!auth.loading" :size="19" />
          </button>
        </form>
      </div>

      <footer class="login-footer">
      </footer>
    </section>
  </main>
</template>


<style scoped>

.portal-login {
  --login-text: #202833;
  --login-muted: #84909d;
  --login-line: #e8edf1;
  --login-blue: #3986c8;

  width: 100%;
  min-height: 100vh;
  min-height: 100svh;
  display: grid;
  grid-template-columns: 55% 45%;
  overflow: hidden;
  background: #ffffff;
  color: var(--login-text);
}

/* LEFT PANEL */

.dna-panel {
  position: relative;
  min-width: 0;
  min-height: 100vh;
  min-height: 100svh;
  display: flex;
  align-items: flex-end;
  padding: 8.5%;
  overflow: hidden;
  isolation: isolate;
  color: #edf6fc;
  background:
    radial-gradient(ellipse at 75% 30%, rgba(57, 134, 200, .22), transparent 45%),
    linear-gradient(145deg, #101c28 0%, #142b3c 55%, #10202d 100%);
}

.dna-grid {
  position: absolute;
  z-index: -1;
  inset: 0;
  opacity: .15;
  background-image:
    linear-gradient(rgba(180, 220, 245, .14) 1px, transparent 1px),
    linear-gradient(90deg, rgba(180, 220, 245, .14) 1px, transparent 1px);
  background-size: 42px 42px;
  mask-image: linear-gradient(to bottom, black, transparent 90%);
}

.dna-glow {
  position: absolute;
  z-index: -1;
  width: 380px;
  height: 380px;
  border-radius: 50%;
  filter: blur(100px);
  pointer-events: none;
}

.dna-glow-one {
  top: 5%;
  right: 0;
  background: rgba(57, 134, 200, .2);
}

.dna-glow-two {
  bottom: 5%;
  left: 0;
  background: rgba(99, 184, 173, .12);
}

.dna-copy {
  position: relative;
  z-index: 2;
  width: 100%;
  max-width: 470px;
  padding-bottom: 10px;
}

.dna-index {
  display: block;
  margin-bottom: 27px;
  color: #91b8d3;
  font-size: 9px;
  font-weight: 700;
  letter-spacing: .2em;
}

.dna-copy h2 {
  margin: 0;
  color: #f0f7fc;
  font-size: clamp(42px, 5vw, 68px);
  font-weight: 650;
  line-height: 1.08;
  letter-spacing: -.065em;
}

.dna-copy p {
  max-width: 365px;
  margin: 23px 0 0;
  color: #a9bdcc;
  font-size: 13px;
  line-height: 1.85;
}

/* DNA ART */

.dna-art {
  position: absolute;
  z-index: 0;
  top: -3%;
  right: -8%;
  width: 72%;
  height: 108%;
  opacity: .78;
  pointer-events: none;
  overflow: visible;
}

.dna-strand {
  stroke-dasharray: 12 9;
  animation: dna-flow 18s linear infinite;
}

.dna-strand-mint {
  animation-direction: reverse;
}

.dna-rungs path {
  stroke: rgba(173, 218, 239, .32);
  stroke-width: 1.2;
  stroke-linecap: round;
}

.dna-particles circle {
  fill: #b9e5f4;
  filter: drop-shadow(0 0 7px rgba(166, 217, 250, .8));
  animation: dna-pulse 3s ease-in-out infinite alternate;
}

.dna-particles circle:nth-child(2n) {
  animation-delay: .7s;
}

.dna-particles circle:nth-child(3n) {
  animation-delay: 1.4s;
}

@keyframes dna-flow {
  to {
    stroke-dashoffset: -210;
  }
}

@keyframes dna-pulse {
  from {
    opacity: .35;
    transform: scale(.8);
    transform-box: fill-box;
    transform-origin: center;
  }

  to {
    opacity: 1;
    transform: scale(1.35);
    transform-box: fill-box;
    transform-origin: center;
  }
}

/* RIGHT PANEL */

.login-panel {
  position: relative;
  z-index: 1;
  min-width: 0;
  min-height: 100vh;
  min-height: 100svh;
  display: flex;
  flex-direction: column;
  padding: 34px clamp(38px, 6vw, 90px) 27px;
  color: #202833;
  background: #ffffff;
}

.login-topbar {
  min-height: 28px;
  display: flex;
  align-items: center;
  justify-content: flex-end;
}

.author-mark {
  color: #84909d;
  font-size: 9px;
  font-weight: 750;
  letter-spacing: .17em;
}

.login-content {
  width: 100%;
  max-width: 370px;
  margin: auto;
  padding: 45px 0;
}

.login-heading {
  margin-bottom: 34px;
}

.login-heading h1 {
  margin: 0 0 12px;
  color: #202833;
  font-size: clamp(30px, 3vw, 37px);
  font-weight: 700;
  line-height: 1.15;
  letter-spacing: -.055em;
}

.login-heading p {
  max-width: 330px;
  margin: 0;
  color: #84909d;
  font-size: 12px;
  line-height: 1.8;
}

/* FORM */

.login-form {
  display: grid;
  gap: 21px;
}

.login-field-group {
  display: grid;
  gap: 9px;
}

.login-field-group label {
  color: #303b46;
  font-size: 10px;
  font-weight: 700;
}

.login-input-wrap {
  min-height: 49px;
  display: flex;
  align-items: center;
  gap: 11px;
  padding: 0 14px;
  border: 1px solid #e8edf1;
  border-radius: 8px;
  color: #84909d;
  background: #f8fafc;
  transition: border-color .18s, background .18s, box-shadow .18s;
}

.login-input-wrap:focus-within {
  border-color: #3986c8;
  background: #ffffff;
  box-shadow: 0 0 0 3px rgba(57, 134, 200, .09);
}

.login-input-wrap input {
  width: 100%;
  min-width: 0;
  height: 47px;
  padding: 0;
  border: 0;
  outline: 0;
  color: #202833;
  background: transparent;
  font-size: 11px;
  box-shadow: none;
}

.login-input-wrap input::placeholder {
  color: #9aa5af;
  opacity: 1;
}

.login-input-wrap input:focus {
  outline: none;
  box-shadow: none;
}

.login-password-toggle {
  flex: none;
  display: grid;
  place-items: center;
  padding: 5px;
  border: 0;
  border-radius: 5px;
  color: #84909d;
  background: transparent;
}

.login-password-toggle:hover {
  color: #3986c8;
}

.login-password-toggle:focus-visible {
  outline: 2px solid #3986c8;
  outline-offset: 2px;
}

.login-error {
  margin: -7px 0 0;
  padding: 10px 12px;
  border: 1px solid rgba(200, 91, 99, .25);
  border-radius: 7px;
  color: #c85b63;
  background: #fff5f5;
  font-size: 10px;
  line-height: 1.5;
}

.login-submit {
  width: 100%;
  min-height: 49px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  margin-top: 5px;
  padding: 0 16px;
  border: 1px solid #3986c8;
  border-radius: 8px;
  color: #ffffff;
  background: #3986c8;
  font-size: 11px;
  font-weight: 700;
  transition: background .18s, transform .18s;
}

.login-submit:hover:not(:disabled) {
  border-color: #2d75b3;
  background: #2d75b3;
  transform: translateY(-1px);
}

.login-submit:disabled {
  cursor: not-allowed;
  opacity: .65;
}

.login-footer {
  min-height: 22px;
  display: flex;
  align-items: center;
  justify-content: flex-end;
  color: #84909d;
  font-size: 9px;
}

/* TABLET */

@media (max-width: 900px) {
  .portal-login {
    grid-template-columns: 48% 52%;
  }

  .dna-panel {
    padding: 7%;
  }

  .dna-art {
    width: 95%;
    right: -24%;
  }

  .dna-copy h2 {
    font-size: clamp(37px, 5vw, 52px);
  }

  .login-panel {
    padding-right: 38px;
    padding-left: 38px;
  }
}

/* MOBILE */

@media (max-width: 650px) {
  .portal-login {
    display: flex;
    flex-direction: column;
    overflow: auto;
  }

  .dna-panel {
    width: 100%;
    min-height: 220px;
    height: 220px;
    flex: none;
    align-items: flex-end;
    padding: 25px 25px;
  }

  .dna-copy {
    padding: 0;
  }

  .dna-index {
    margin-bottom: 11px;
    font-size: 8px;
  }

  .dna-copy h2 {
    font-size: 30px;
  }

  .dna-copy p {
    display: none;
  }

  .dna-art {
    top: -70%;
    right: -8%;
    width: 55%;
    height: 240%;
    opacity: .55;
  }

  .login-panel {
    width: 100%;
    min-height: calc(100svh - 220px);
    padding: 20px 25px 17px;
  }

  .login-content {
    max-width: 420px;
    padding: 42px 0;
  }

  .login-heading {
    margin-bottom: 27px;
  }

  .login-heading h1 {
    font-size: 29px;
  }
}

@media (max-width: 380px) {
  .dna-panel {
    min-height: 190px;
    height: 190px;
  }

  .login-panel {
    min-height: calc(100svh - 190px);
    padding-right: 19px;
    padding-left: 19px;
  }

  .login-content {
    padding: 34px 0;
  }
}

@media (prefers-reduced-motion: reduce) {
  .dna-strand,
  .dna-particles circle {
    animation: none;
  }

  .login-submit,
  .login-input-wrap {
    transition: none;
  }
}
</style>