import { createApp } from 'vue'
import { createPinia } from 'pinia'
import router from './router.ts'
import App from './App.vue'
import './styles.css'

createApp(App).use(createPinia()).use(router).mount('#app')