<script setup lang="ts">
import type { OsType } from '@/types'

defineProps<{ os: OsType }>()
</script>

<template>
  <span
    class="inline-flex items-center gap-1 text-xs px-2 py-0.5 rounded-full border font-medium"
    :class="
      os === 'linux'
        ? 'border-orange-700 text-orange-400 bg-orange-950/40'
        : 'border-sky-700 text-sky-400 bg-sky-950/40'
    "
  >
    {{ os === 'linux' ? 'Linux' : 'Windows' }}
  </span>
</template>
