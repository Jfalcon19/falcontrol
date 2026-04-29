<script setup lang="ts">
import type { ConnectionType } from '@/types'

defineProps<{ conn: ConnectionType }>()
</script>

<template>
  <span
    class="inline-flex items-center text-xs px-2 py-0.5 rounded-full border font-medium"
    :class="
      conn === 'ssh'
        ? 'border-green-700 text-green-400 bg-green-950/40'
        : 'border-purple-700 text-purple-400 bg-purple-950/40'
    "
  >
    {{ conn === 'ssh' ? 'SSH' : 'WinRM' }}
  </span>
</template>
