import { createRouter, createWebHistory } from 'vue-router'
import FilesView from './views/FilesView.vue'
import LoginView from './views/LoginView.vue'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    // The workspace is the only application page. The root is a smart entry point.
    { path: '/', redirect: () => localStorage.getItem('hp_access_token') ? '/app' : '/login' },
    { path: '/app', name: 'files', component: FilesView },
    { path: '/login', name: 'login', component: LoginView },
    // Registration is intentionally not available in this version.
    { path: '/register', redirect: '/login' },
    { path: '/:pathMatch(.*)*', redirect: () => localStorage.getItem('hp_access_token') ? '/app' : '/login' }
  ],
  scrollBehavior() {
    return { top: 0 }
  }
})

router.beforeEach((to) => {
  const hasToken = !!localStorage.getItem('hp_access_token')
  if (to.name === 'login' && hasToken) return '/app'
  return true
})

export default router
