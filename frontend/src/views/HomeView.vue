<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { fetchHealth } from '@/api/health'

const status = ref<string | null>(null)
const version = ref<string | null>(null)
const error = ref<string | null>(null)
const loading = ref(true)

onMounted(async () => {
  try {
    const data = await fetchHealth()
    status.value = data.status
    version.value = data.version
  } catch {
    error.value = 'No se puede conectar con la API. ¿Está el backend corriendo?'
  } finally {
    loading.value = false
  }
})
</script>

<template>
  <div class="min-h-screen bg-gray-950 flex items-center justify-center">
    <div class="text-center space-y-6">
      <h1 class="text-4xl font-bold text-white tracking-tight">
        Falcon<span class="text-brand-500">trol</span>
      </h1>
      <p class="text-gray-400 text-sm">Automation CMS para PYMES</p>

      <div class="mt-8 p-6 bg-gray-900 rounded-xl border border-gray-800 min-w-[280px]">
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
  </div>
</template>
