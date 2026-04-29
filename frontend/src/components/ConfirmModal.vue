<script setup lang="ts">
defineProps<{
  title: string
  message: string
  confirmLabel?: string
  loading?: boolean
}>()

const emit = defineEmits<{
  confirm: []
  cancel: []
}>()
</script>

<template>
  <div class="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm">
    <div class="bg-gray-900 border border-gray-700 rounded-xl p-6 w-full max-w-sm shadow-xl space-y-4">
      <h2 class="text-white font-semibold text-base">{{ title }}</h2>
      <p class="text-gray-400 text-sm">{{ message }}</p>
      <div class="flex justify-end gap-3 pt-2">
        <button
          class="px-4 py-1.5 text-sm rounded-lg border border-gray-700 text-gray-300 hover:border-gray-500 transition-colors"
          :disabled="loading"
          @click="emit('cancel')"
        >
          Cancelar
        </button>
        <button
          class="px-4 py-1.5 text-sm rounded-lg bg-red-700 hover:bg-red-600 text-white transition-colors disabled:opacity-50"
          :disabled="loading"
          @click="emit('confirm')"
        >
          {{ confirmLabel ?? 'Eliminar' }}
        </button>
      </div>
    </div>
  </div>
</template>
