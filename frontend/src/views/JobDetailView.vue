<script setup lang="ts">
import { ref, onMounted, onUnmounted, nextTick } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useJobsStore } from '@/stores/jobs'
import { ACCESS_TOKEN_KEY } from '@/api/client'
import JobStatusBadge from '@/components/JobStatusBadge.vue'
import type { JobDetail } from '@/types'

const route = useRoute()
const router = useRouter()
const jobsStore = useJobsStore()

const jobId = route.params.id as string
const job = ref<JobDetail | null>(null)
const logLines = ref<string[]>([])
const logEl = ref<HTMLElement | null>(null)
const wsConnected = ref(false)
const finished = ref(false)

let ws: WebSocket | null = null

function scrollToBottom() {
  nextTick(() => {
    if (logEl.value) logEl.value.scrollTop = logEl.value.scrollHeight
  })
}

function connectWs() {
  const token = localStorage.getItem(ACCESS_TOKEN_KEY)
  if (!token) return

  const protocol = location.protocol === 'https:' ? 'wss' : 'ws'
  const url = `${protocol}://${location.host}/ws/jobs/${jobId}/logs?token=${token}`
  ws = new WebSocket(url)

  ws.onopen = () => {
    wsConnected.value = true
  }

  ws.onmessage = (ev: MessageEvent) => {
    const line: string = ev.data
    if (line === '__END__') {
      finished.value = true
      ws?.close()
      jobsStore.fetchJob(jobId).then((j) => {
        if (j) job.value = j
      })
      return
    }
    if (line === '__PING__') return
    if (line.startsWith('__ERROR__')) {
      logLines.value.push(line)
      scrollToBottom()
      return
    }
    logLines.value.push(line)
    scrollToBottom()
  }

  ws.onclose = () => {
    wsConnected.value = false
  }
}

onMounted(async () => {
  job.value = await jobsStore.fetchJob(jobId)
  if (!job.value) {
    router.replace({ name: 'jobs' })
    return
  }

  if (job.value.status === 'success' || job.value.status === 'failed') {
    // Job already done — WebSocket will stream stored stdout then __END__
    finished.value = false
  }

  connectWs()
})

onUnmounted(() => {
  ws?.close()
})

function formatDate(iso: string | null): string {
  if (!iso) return '—'
  return new Date(iso).toLocaleString('es-ES', { dateStyle: 'short', timeStyle: 'medium' })
}

function duration(): string {
  if (!job.value?.started_at) return '—'
  const start = new Date(job.value.started_at).getTime()
  const end = job.value.finished_at ? new Date(job.value.finished_at).getTime() : Date.now()
  const secs = Math.round((end - start) / 1000)
  if (secs < 60) return `${secs}s`
  return `${Math.floor(secs / 60)}m ${secs % 60}s`
}
</script>

<template>
  <div>
    <!-- Back link -->
    <button
      class="mb-4 text-sm text-gray-500 hover:text-white transition-colors flex items-center gap-1"
      @click="router.push({ name: 'jobs' })"
    >
      ← Volver a Jobs
    </button>

    <div v-if="!job" class="text-gray-500 text-sm">Cargando…</div>

    <template v-else>
      <!-- Job metadata -->
      <div class="bg-gray-900 border border-gray-800 rounded-xl p-5 mb-5">
        <div class="flex items-center justify-between mb-4">
          <h2 class="text-lg font-semibold text-white truncate">{{ job.playbook_path }}</h2>
          <JobStatusBadge :status="job.status" />
        </div>
        <dl class="grid grid-cols-2 sm:grid-cols-4 gap-4 text-sm">
          <div>
            <dt class="text-gray-500 text-xs mb-1">RC</dt>
            <dd class="text-white">{{ job.return_code ?? '—' }}</dd>
          </div>
          <div>
            <dt class="text-gray-500 text-xs mb-1">Duración</dt>
            <dd class="text-white">{{ duration() }}</dd>
          </div>
          <div>
            <dt class="text-gray-500 text-xs mb-1">Inicio</dt>
            <dd class="text-white">{{ formatDate(job.started_at) }}</dd>
          </div>
          <div>
            <dt class="text-gray-500 text-xs mb-1">Fin</dt>
            <dd class="text-white">{{ formatDate(job.finished_at) }}</dd>
          </div>
        </dl>
      </div>

      <!-- Log output -->
      <div class="bg-gray-950 border border-gray-800 rounded-xl overflow-hidden">
        <div class="flex items-center justify-between px-4 py-2 border-b border-gray-800">
          <span class="text-xs text-gray-400 font-mono">stdout</span>
          <span v-if="!finished && wsConnected" class="text-xs text-blue-400 animate-pulse">
            ● en vivo
          </span>
          <span v-else-if="finished" class="text-xs text-gray-600">finalizado</span>
        </div>
        <div
          ref="logEl"
          class="h-96 overflow-y-auto p-4 font-mono text-xs text-green-300 leading-relaxed"
        >
          <div v-if="!logLines.length" class="text-gray-700">Sin salida todavía…</div>
          <div v-for="(line, i) in logLines" :key="i" class="whitespace-pre-wrap">{{ line }}</div>
        </div>
      </div>
    </template>
  </div>
</template>
