import axios from 'axios'

export const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000',
  timeout: 30000
})

api.interceptors.request.use((config) => {
  const token = localStorage.getItem('hp_access_token')
  if (token) config.headers.Authorization = `Bearer ${token}`
  return config
})

api.interceptors.response.use(
  (response) => response,
  (error) => {
    return Promise.reject(error)
  }
)

export function errorMessage(error: unknown): string {
  if (axios.isAxiosError(error)) {
    const detail = error.response?.data?.detail
    if (typeof detail === 'string') return detail
    if (!error.response) return 'Не удалось связаться с сервером. Проверь API и адрес подключения.'
    return `Ошибка запроса (${error.response.status})`
  }
  return 'Произошла непредвиденная ошибка'
}