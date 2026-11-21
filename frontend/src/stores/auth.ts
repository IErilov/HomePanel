import { defineStore } from 'pinia'
import { ref } from 'vue'
import { api } from '../api'
import type { CurrentUser } from '../types'

export const useAuthStore = defineStore('auth', () => {
  const user = ref<CurrentUser | null>(null)
  const loading = ref(false)
  const token = () => localStorage.getItem('hp_access_token')

  async function login(username: string, password: string) {
    loading.value = true
    try {
      const body = new URLSearchParams()
      body.set('username', username)
      body.set('password', password)
      const { data } = await api.post('/api/users/login', body, {
        headers: { 'Content-Type': 'application/x-www-form-urlencoded' }
      })
      localStorage.setItem('hp_access_token', data.access_token)
      await fetchMe()
    } finally {
      loading.value = false
    }
  }

  async function fetchMe() {
    if (!token()) {
      user.value = null
      return
    }
    const { data } = await api.get('/api/users/me')
    user.value = data
  }

  function logout() {
    localStorage.removeItem('hp_access_token')
    user.value = null
  }

  return { user, loading, login, fetchMe, logout, isAuthenticated: () => !!token() }
})