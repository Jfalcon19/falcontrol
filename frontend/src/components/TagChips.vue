<script setup lang="ts">
defineProps<{ tags: string[] }>()
</script>

<template>
  <div class="flex flex-wrap gap-1">
    <span
      v-for="tag in tags"
      :key="tag"
      class="text-xs px-2 py-0.5 rounded-md bg-gray-800 text-gray-300 border border-gray-700"
    >
      {{ tag }}
    </span>
    <span v-if="tags.length === 0" class="text-xs text-gray-600">—</span>
  </div>
</template>
