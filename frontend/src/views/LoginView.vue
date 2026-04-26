<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import axios from 'axios'
import { useAuthStore } from '@/stores/auth'

const router = useRouter()
const auth = useAuthStore()

const email = ref('')
const password = ref('')
const error = ref<string | null>(null)
const loading = ref(false)

async function handleSubmit() {
  error.value = null
  loading.value = true
  try {
    await auth.login({ email: email.value, password: password.value })
    await router.push('/')
  } catch (e) {
    if (axios.isAxiosError(e)) {
      const status = e.response?.status
      if (status === 401) {
        error.value = 'Credenciales incorrectas'
      } else {
        const detail = (e.response?.data as { detail?: string })?.detail
        error.value = detail ?? 'Error al conectar con el servidor'
      }
    } else {
      error.value = 'Error inesperado'
    }
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <div class="min-h-screen bg-gray-950 flex items-center justify-center px-4">
    <div class="w-full max-w-sm space-y-8">
      <div class="text-center">
        <h1 class="text-3xl font-bold text-white tracking-tight">
          Falcon<span class="text-brand-500">trol</span>
        </h1>
        <p class="mt-2 text-sm text-gray-400">Automation CMS para PYMES</p>
      </div>

      <form
        class="bg-gray-900 rounded-xl border border-gray-800 p-8 space-y-5"
        @submit.prevent="handleSubmit"
      >
        <div class="space-y-1">
          <label for="email" class="block text-xs font-medium text-gray-400 uppercase tracking-wider"
            >Email</label
          >
          <input
            id="email"
            v-model="email"
            type="email"
            autocomplete="email"
            required
            class="w-full rounded-lg bg-gray-800 border border-gray-700 text-white placeholder-gray-500 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-brand-500 focus:border-transparent"
            placeholder="admin@example.com"
          />
        </div>

        <div class="space-y-1">
          <label
            for="password"
            class="block text-xs font-medium text-gray-400 uppercase tracking-wider"
            >Contraseña</label
          >
          <input
            id="password"
            v-model="password"
            type="password"
            autocomplete="current-password"
            required
            class="w-full rounded-lg bg-gray-800 border border-gray-700 text-white placeholder-gray-500 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-brand-500 focus:border-transparent"
            placeholder="••••••••"
          />
        </div>

        <div
          v-if="error"
          class="flex items-center gap-2 rounded-lg bg-red-950 border border-red-800 px-3 py-2 text-sm text-red-400"
        >
          <span>✗</span>
          <span>{{ error }}</span>
        </div>

        <button
          type="submit"
          :disabled="loading"
          class="w-full rounded-lg bg-brand-500 hover:bg-brand-600 disabled:opacity-50 disabled:cursor-not-allowed text-white font-medium py-2 text-sm transition-colors"
        >
          <span v-if="loading" class="inline-flex items-center gap-2">
            <span class="animate-spin">⟳</span>
            Entrando…
          </span>
          <span v-else>Entrar</span>
        </button>
      </form>
    </div>
  </div>
</template>
