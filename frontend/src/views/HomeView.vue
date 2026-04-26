<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { fetchHealth } from '@/api/health'
import { useAuthStore } from '@/stores/auth'

const router = useRouter()
const auth = useAuthStore()

const status = ref<string | null>(null)
const version = ref<string | null>(null)
const error = ref<string | null>(null)
const loading = ref(true)

onMounted(async () => {
  try {
    if (!auth.user) await auth.fetchMe()
    const data = await fetchHealth()
    status.value = data.status
    version.value = data.version
  } catch {
    error.value = 'No se puede conectar con la API. ¿Está el backend corriendo?'
  } finally {
    loading.value = false
  }
})

async function handleLogout() {
  auth.logout()
  await router.push('/login')
}
</script>

<template>
  <div class="min-h-screen bg-gray-950">
    <header class="border-b border-gray-800 px-6 py-4 flex items-center justify-between">
      <h1 class="text-lg font-bold text-white tracking-tight">
        Fal<span class="text-brand-500">control</span>
      </h1>
      <div class="flex items-center gap-4">
        <span class="text-sm text-gray-400">{{ auth.user?.email }}</span>
        <span
          class="text-xs px-2 py-0.5 rounded-full border"
          :class="{
            'border-yellow-700 text-yellow-400': auth.user?.role === 'admin',
            'border-blue-700 text-blue-400': auth.user?.role === 'operator',
            'border-gray-700 text-gray-400': auth.user?.role === 'viewer',
          }"
          >{{ auth.user?.role }}</span
        >
        <button
          class="text-sm text-gray-500 hover:text-white transition-colors"
          @click="handleLogout"
        >
          Salir
        </button>
      </div>
    </header>

    <main class="flex items-center justify-center min-h-[calc(100vh-65px)]">
      <div class="text-center space-y-6">
        <p class="text-gray-400 text-sm">Automation CMS para PYMES</p>

        <div class="p-6 bg-gray-900 rounded-xl border border-gray-800 min-w-[280px]">
          <p class="text-xs uppercase tracking-widest text-gray-500 mb-3">Estado del backend</p>

          <div v-if="loading" class="flex items-center justify-center gap-2 text-gray-400">
            <span class="animate-spin">⟳</span>
            <span>Comprobando…</span>
          </div>

          <div v-else-if="error" class="flex items-center justify-center gap-2 text-red-400">
            <span>✗</span>
            <span class="text-sm">{{ error }}</span>
          </div>

          <div v-else class="space-y-2">
            <div class="flex items-center justify-center gap-2 text-green-400 font-mono text-lg">
              <span>✓</span>
              <span>{{ status }}</span>
            </div>
            <p class="text-gray-500 text-xs">v{{ version }}</p>
          </div>
        </div>
      </div>
    </main>
  </div>
</template>
