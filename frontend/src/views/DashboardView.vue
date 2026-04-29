<script setup lang="ts">
import { onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { useDashboardStore } from '@/stores/dashboard'
import JobStatusBadge from '@/components/JobStatusBadge.vue'

const router = useRouter()
const dashboardStore = useDashboardStore()

let reloadTimer: ReturnType<typeof setInterval> | null = null

onMounted(() => {
  dashboardStore.fetchStats()
  reloadTimer = setInterval(() => dashboardStore.fetchStats(), 30_000)
})

onUnmounted(() => {
  if (reloadTimer !== null) clearInterval(reloadTimer)
})

function formatDate(iso: string): string {
  return new Date(iso).toLocaleString('es-ES', { dateStyle: 'short', timeStyle: 'short' })
}

interface StatCard {
  label: string
  key: keyof Pick<
    NonNullable<typeof dashboardStore.stats>,
    'total_hosts' | 'total_inventories' | 'total_schedules' | 'total_jobs' | 'running_jobs' | 'failed_last_24h'
  >
  accent: string
}

const statCards: StatCard[] = [
  { label: 'Hosts', key: 'total_hosts', accent: 'text-brand-400' },
  { label: 'Inventarios', key: 'total_inventories', accent: 'text-blue-400' },
  { label: 'Schedules', key: 'total_schedules', accent: 'text-purple-400' },
  { label: 'Jobs totales', key: 'total_jobs', accent: 'text-gray-300' },
  { label: 'Jobs activos', key: 'running_jobs', accent: 'text-green-400' },
  { label: 'Fallos (24h)', key: 'failed_last_24h', accent: 'text-red-400' },
]
</script>

<template>
  <div>
    <h2 class="text-xl font-semibold text-white mb-6">Dashboard</h2>

    <!-- Error -->
    <p v-if="dashboardStore.error" class="text-red-400 text-sm mb-4">{{ dashboardStore.error }}</p>

    <!-- Loading -->
    <div v-if="dashboardStore.loading" class="text-gray-500 text-sm">Cargando…</div>

    <template v-else-if="dashboardStore.stats">
      <!-- Stat cards -->
      <div class="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-4 mb-8">
        <div
          v-for="card in statCards"
          :key="card.key"
          class="bg-gray-900 border border-gray-800 rounded-xl px-5 py-4 flex flex-col gap-1"
        >
          <span class="text-xs text-gray-500">{{ card.label }}</span>
          <span class="text-3xl font-bold" :class="card.accent">
            {{ dashboardStore.stats[card.key] }}
          </span>
        </div>
      </div>

      <!-- Recent jobs -->
      <div>
        <h3 class="text-sm font-medium text-gray-400 mb-3">Jobs recientes</h3>

        <div
          v-if="!dashboardStore.stats.recent_jobs.length"
          class="text-center py-10 text-gray-600 text-sm"
        >
          No hay jobs todavía.
        </div>

        <div v-else class="overflow-x-auto rounded-xl border border-gray-800">
          <table class="w-full text-sm">
            <thead class="bg-gray-900 text-gray-400 text-left">
              <tr>
                <th class="px-4 py-3 font-medium">Estado</th>
                <th class="px-4 py-3 font-medium">Playbook</th>
                <th class="px-4 py-3 font-medium">RC</th>
                <th class="px-4 py-3 font-medium">Creado</th>
              </tr>
            </thead>
            <tbody class="divide-y divide-gray-800">
              <tr
                v-for="job in dashboardStore.stats.recent_jobs"
                :key="job.id"
                class="bg-gray-950 hover:bg-gray-900 transition-colors cursor-pointer"
                @click="router.push({ name: 'job-detail', params: { id: job.id } })"
              >
                <td class="px-4 py-3">
                  <JobStatusBadge :status="job.status" />
                </td>
                <td class="px-4 py-3 text-gray-300 font-mono text-xs truncate max-w-xs">
                  {{ job.playbook_path }}
                </td>
                <td class="px-4 py-3 text-gray-400">{{ job.return_code ?? '—' }}</td>
                <td class="px-4 py-3 text-gray-500">{{ formatDate(job.created_at) }}</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </template>
  </div>
</template>
