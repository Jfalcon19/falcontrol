<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useJobsStore } from '@/stores/jobs'
import { useInventoriesStore } from '@/stores/inventories'
import { useAuthStore } from '@/stores/auth'
import JobStatusBadge from '@/components/JobStatusBadge.vue'
import ConfirmModal from '@/components/ConfirmModal.vue'

const router = useRouter()
const jobsStore = useJobsStore()
const inventoriesStore = useInventoriesStore()
const auth = useAuthStore()

const showLaunchForm = ref(false)
const launchInventoryId = ref('')
const launchPlaybook = ref('')
const launching = ref(false)

const jobToDelete = ref<string | null>(null)

onMounted(async () => {
  await Promise.all([jobsStore.fetchJobs(), inventoriesStore.fetchAll()])
})

async function handleLaunch() {
  if (!launchInventoryId.value || !launchPlaybook.value.trim()) return
  launching.value = true
  const job = await jobsStore.launchJob({
    inventory_id: launchInventoryId.value,
    playbook_path: launchPlaybook.value.trim(),
  })
  launching.value = false
  if (job) {
    showLaunchForm.value = false
    launchInventoryId.value = ''
    launchPlaybook.value = ''
    router.push({ name: 'job-detail', params: { id: job.id } })
  }
}

async function confirmDelete() {
  if (!jobToDelete.value) return
  await jobsStore.removeJob(jobToDelete.value)
  jobToDelete.value = null
}

function formatDuration(startedAt: string | null, finishedAt: string | null): string {
  if (!startedAt) return '—'
  const start = new Date(startedAt).getTime()
  const end = finishedAt ? new Date(finishedAt).getTime() : Date.now()
  const secs = Math.round((end - start) / 1000)
  if (secs < 60) return `${secs}s`
  return `${Math.floor(secs / 60)}m ${secs % 60}s`
}

function formatDate(iso: string): string {
  return new Date(iso).toLocaleString('es-ES', { dateStyle: 'short', timeStyle: 'short' })
}
</script>

<template>
  <div>
    <!-- Header -->
    <div class="flex items-center justify-between mb-6">
      <h2 class="text-xl font-semibold text-white">Jobs</h2>
      <button
        v-if="auth.user?.role !== 'viewer'"
        class="px-4 py-2 text-sm bg-brand-600 hover:bg-brand-500 text-white rounded-lg transition-colors"
        @click="showLaunchForm = true"
      >
        Lanzar job
      </button>
    </div>

    <!-- Launch form -->
    <div v-if="showLaunchForm" class="mb-6 bg-gray-900 border border-gray-800 rounded-xl p-5">
      <h3 class="text-sm font-medium text-white mb-4">Nuevo job</h3>
      <form class="grid grid-cols-1 gap-4 sm:grid-cols-2" @submit.prevent="handleLaunch">
        <div>
          <label class="block text-xs text-gray-400 mb-1">Inventario</label>
          <select
            v-model="launchInventoryId"
            required
            class="w-full bg-gray-800 border border-gray-700 text-white rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-brand-500"
          >
            <option value="" disabled>Selecciona un inventario…</option>
            <option v-for="inv in inventoriesStore.inventories" :key="inv.id" :value="inv.id">
              {{ inv.name }}
            </option>
          </select>
        </div>
        <div>
          <label class="block text-xs text-gray-400 mb-1">Ruta del playbook</label>
          <input
            v-model="launchPlaybook"
            type="text"
            placeholder="/opt/playbooks/ping.yml"
            required
            class="w-full bg-gray-800 border border-gray-700 text-white rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-brand-500"
          />
        </div>
        <div class="sm:col-span-2 flex justify-end gap-3">
          <button
            type="button"
            class="px-4 py-2 text-sm text-gray-400 hover:text-white transition-colors"
            @click="showLaunchForm = false"
          >
            Cancelar
          </button>
          <button
            type="submit"
            :disabled="launching"
            class="px-4 py-2 text-sm bg-brand-600 hover:bg-brand-500 disabled:opacity-50 text-white rounded-lg transition-colors"
          >
            {{ launching ? 'Lanzando…' : 'Lanzar' }}
          </button>
        </div>
      </form>
    </div>

    <!-- Error -->
    <p v-if="jobsStore.error" class="text-red-400 text-sm mb-4">{{ jobsStore.error }}</p>

    <!-- Loading -->
    <div v-if="jobsStore.loading" class="text-gray-500 text-sm">Cargando…</div>

    <!-- Empty -->
    <div
      v-else-if="!jobsStore.jobs.length"
      class="text-center py-16 text-gray-600 text-sm"
    >
      No hay jobs todavía.
    </div>

    <!-- Table -->
    <div v-else class="overflow-x-auto rounded-xl border border-gray-800">
      <table class="w-full text-sm">
        <thead class="bg-gray-900 text-gray-400 text-left">
          <tr>
            <th class="px-4 py-3 font-medium">Estado</th>
            <th class="px-4 py-3 font-medium">Playbook</th>
            <th class="px-4 py-3 font-medium">RC</th>
            <th class="px-4 py-3 font-medium">Duración</th>
            <th class="px-4 py-3 font-medium">Creado</th>
            <th class="px-4 py-3 font-medium w-16"></th>
          </tr>
        </thead>
        <tbody class="divide-y divide-gray-800">
          <tr
            v-for="job in jobsStore.jobs"
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
            <td class="px-4 py-3 text-gray-400">
              {{ job.return_code ?? '—' }}
            </td>
            <td class="px-4 py-3 text-gray-400">
              {{ formatDuration(job.started_at, job.finished_at) }}
            </td>
            <td class="px-4 py-3 text-gray-500">
              {{ formatDate(job.created_at) }}
            </td>
            <td class="px-4 py-3 text-right" @click.stop>
              <button
                v-if="auth.user?.role === 'admin'"
                class="text-gray-600 hover:text-red-400 transition-colors text-xs"
                @click="jobToDelete = job.id"
              >
                Eliminar
              </button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- Confirm delete modal -->
    <ConfirmModal
      :open="jobToDelete !== null"
      title="Eliminar job"
      message="¿Eliminar este job? Esta acción no se puede deshacer."
      confirm-label="Eliminar"
      @confirm="confirmDelete"
      @cancel="jobToDelete = null"
    />
  </div>
</template>
