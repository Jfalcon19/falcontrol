import './assets/main.css'

import { createApp } from 'vue'
import { createPinia } from 'pinia'

import App from './App.vue'
import router from './router'

const app = createApp(App)

app.use(createPinia())
app.use(router)

// Redirect to /login when the axios interceptor detects an unrecoverable 401
window.addEventListener('fc:logout', () => {
  router.push('/login')
})

app.mount('#app')
