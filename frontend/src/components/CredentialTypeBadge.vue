<script setup lang="ts">
import type { CredentialType } from '@/types'

defineProps<{ type: CredentialType }>()

const labels: Record<CredentialType, string> = {
  ssh_key: 'SSH Key',
  ssh_password: 'SSH Pass',
  winrm: 'WinRM',
}

const styles: Record<CredentialType, string> = {
  ssh_key: 'border-teal-700 text-teal-400 bg-teal-950/40',
  ssh_password: 'border-blue-700 text-blue-400 bg-blue-950/40',
  winrm: 'border-purple-700 text-purple-400 bg-purple-950/40',
}
</script>

<template>
  <span
    class="inline-flex items-center text-xs px-2 py-0.5 rounded-full border font-medium"
    :class="styles[type]"
  >
    {{ labels[type] }}
  </span>
</template>
