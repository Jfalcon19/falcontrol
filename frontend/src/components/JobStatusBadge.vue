<script setup lang="ts">
import type { JobStatus } from '@/types'

defineProps<{ status: JobStatus }>()

const classes: Record<JobStatus, string> = {
  pending: 'bg-gray-700 text-gray-300',
  running: 'bg-blue-900 text-blue-300 animate-pulse',
  success: 'bg-green-900 text-green-300',
  failed: 'bg-red-900 text-red-300',
}

const labels: Record<JobStatus, string> = {
  pending: 'Pendiente',
  running: 'Ejecutando',
  success: 'Éxito',
  failed: 'Fallido',
}
</script>

<template>
  <span class="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium" :class="classes[status]">
    {{ labels[status] }}
  </span>
</template>
