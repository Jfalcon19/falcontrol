<script setup lang="ts">
import { useRouter, useRoute } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const router = useRouter()
const route = useRoute()
const auth = useAuthStore()

async function handleLogout() {
  auth.logout()
  await router.push('/login')
}

const navLinks = [
  { name: 'Dashboard', to: '/', icon: 'home' },
  { name: 'Hosts', to: '/hosts', icon: 'server' },
  { name: 'Inventarios', to: '/inventories', icon: 'collection' },
  { name: 'Credenciales', to: '/credentials', icon: 'key' },
]

function isActive(path: string): boolean {
  if (path === '/') return route.path === '/'
  return route.path.startsWith(path)
}
</script>

<template>
  <div class="min-h-screen bg-gray-950 flex flex-col">
    <!-- Header -->
    <header class="border-b border-gray-800 px-6 py-4 flex items-center justify-between shrink-0">
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
        >{{ auth.user?.role }}</span>
        <button
          class="text-sm text-gray-500 hover:text-white transition-colors"
          @click="handleLogout"
        >
          Salir
        </button>
      </div>
    </header>

    <div class="flex flex-1 overflow-hidden">
      <!-- Sidebar -->
      <nav class="w-52 shrink-0 border-r border-gray-800 py-4 flex flex-col gap-1 overflow-y-auto">
        <RouterLink
          v-for="link in navLinks"
          :key="link.to"
          :to="link.to"
          class="mx-2 px-3 py-2 rounded-lg text-sm transition-colors"
          :class="
            isActive(link.to)
              ? 'bg-gray-800 text-white font-medium'
              : 'text-gray-400 hover:bg-gray-900 hover:text-white'
          "
        >
          {{ link.name }}
        </RouterLink>
      </nav>

      <!-- Main content -->
      <main class="flex-1 overflow-y-auto p-6">
        <RouterView />
      </main>
    </div>
  </div>
</template>
