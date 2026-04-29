<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useSchedulesStore } from '@/stores/schedules'
import { useInventoriesStore } from '@/stores/inventories'
import { useAuthStore } from '@/stores/auth'
import ConfirmModal from '@/components/ConfirmModal.vue'

const schedulesStore = useSchedulesStore()
const inventoriesStore = useInventoriesStore()
const auth = useAuthStore()

const showForm = ref(false)
const saving = ref(false)
const form = ref({
  name: '',
  cron_expression: '',
  inventory_id: '',
  playbook_path: '',
  enabled: true,
})

const scheduleToDelete = ref<string | null>(null)

onMounted(async () => {
  await Promise.all([schedulesStore.fetchAll(), inventoriesStore.fetchAll()])
})

async function handleCreate() {
  if (
    !form.value.name.trim() ||
    !form.value.cron_expression.trim() ||
    !form.value.inventory_id ||
    !form.value.playbook_path.trim()
  )
    return
  saving.value = true
  const s = await schedulesStore.addSchedule({
    name: form.value.name.trim(),
    cron_expression: form.value.cron_expression.trim(),
    inventory_id: form.value.inventory_id,
    playbook_path: form.value.playbook_path.trim(),
    enabled: form.value.enabled,
  })
  saving.value = false
  if (s) {
    showForm.value = false
    form.value = { name: '', cron_expression: '', inventory_id: '', playbook_path: '', enabled: true }
  }
}

async function handleToggle(schedule: (typeof schedulesStore.schedules)[number]) {
  await schedulesStore.toggleEnabled(schedule)
}

async function confirmDelete() {
  if (!scheduleToDelete.value) return
  await schedulesStore.removeSchedule(scheduleToDelete.value)
  scheduleToDelete.value = null
}

function inventoryName(id: string): string {
  return inventoriesStore.inventories.find((i) => i.id === id)?.name ?? id.slice(0, 8) + '…'
}

function formatDate(iso: string): string {
  return new Date(iso).toLocaleString('es-ES', { dateStyle: 'short', timeStyle: 'short' })
}

const canManage = auth.user?.role === 'admin' || auth.user?.role === 'operator'
const isAdmin = auth.user?.role === 'admin'
</script>

<template>
  <div>
    <!-- Header -->
    <div class="flex items-center justify-between mb-6">
      <h2 class="text-xl font-semibold text-white">Schedules</h2>
      <button
        v-if="canManage"
        class="px-4 py-2 text-sm bg-brand-600 hover:bg-brand-500 text-white rounded-lg transition-colors"
        @click="showForm = true"
      >
        Nuevo schedule
      </button>
    </div>

    <!-- Create form -->
    <div v-if="showForm" class="mb-6 bg-gray-900 border border-gray-800 rounded-xl p-5">
      <h3 class="text-sm font-medium text-white mb-4">Nuevo schedule</h3>
      <form class="grid grid-cols-1 gap-4 sm:grid-cols-2" @submit.prevent="handleCreate">
        <div>
          <label class="block text-xs text-gray-400 mb-1">Nombre</label>
          <input
            v-model="form.name"
            type="text"
            placeholder="backup-diario"
            required
            class="w-full bg-gray-800 border border-gray-700 text-white rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-brand-500"
          />
        </div>
        <div>
          <label class="block text-xs text-gray-400 mb-1">Expresión cron <span class="text-gray-600">(min hora día mes weekday)</span></label>
          <input
            v-model="form.cron_expression"
            type="text"
            placeholder="0 2 * * *"
            required
            class="w-full bg-gray-800 border border-gray-700 text-white font-mono rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-brand-500"
          />
        </div>
        <div>
          <label class="block text-xs text-gray-400 mb-1">Inventario</label>
          <select
            v-model="form.inventory_id"
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
            v-model="form.playbook_path"
            type="text"
            placeholder="/opt/playbooks/backup.yml"
            required
            class="w-full bg-gray-800 border border-gray-700 text-white rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-brand-500"
          />
        </div>
        <div class="flex items-center gap-2 sm:col-span-2">
          <input
            id="enabled"
            v-model="form.enabled"
            type="checkbox"
            class="h-4 w-4 rounded border-gray-700 bg-gray-800 accent-brand-500"
          />
          <label for="enabled" class="text-sm text-gray-400">Habilitado</label>
        </div>
        <div class="sm:col-span-2 flex justify-end gap-3">
          <button
            type="button"
            class="px-4 py-2 text-sm text-gray-400 hover:text-white transition-colors"
            @click="showForm = false"
          >
            Cancelar
          </button>
          <button
            type="submit"
            :disabled="saving"
            class="px-4 py-2 text-sm bg-brand-600 hover:bg-brand-500 disabled:opacity-50 text-white rounded-lg transition-colors"
          >
            {{ saving ? 'Guardando…' : 'Crear' }}
          </button>
        </div>
      </form>
    </div>

    <!-- Error -->
    <p v-if="schedulesStore.error" class="text-red-400 text-sm mb-4">{{ schedulesStore.error }}</p>

    <!-- Loading -->
    <div v-if="schedulesStore.loading" class="text-gray-500 text-sm">Cargando…</div>

    <!-- Empty -->
    <div
      v-else-if="!schedulesStore.schedules.length"
      class="text-center py-16 text-gray-600 text-sm"
    >
      No hay schedules todavía.
    </div>

    <!-- Table -->
    <div v-else class="overflow-x-auto rounded-xl border border-gray-800">
      <table class="w-full text-sm">
        <thead class="bg-gray-900 text-gray-400 text-left">
          <tr>
            <th class="px-4 py-3 font-medium">Nombre</th>
            <th class="px-4 py-3 font-medium">Cron</th>
            <th class="px-4 py-3 font-medium">Inventario</th>
            <th class="px-4 py-3 font-medium">Playbook</th>
            <th class="px-4 py-3 font-medium">Estado</th>
            <th class="px-4 py-3 font-medium">Creado</th>
            <th class="px-4 py-3 font-medium w-24"></th>
          </tr>
        </thead>
        <tbody class="divide-y divide-gray-800">
          <tr
            v-for="s in schedulesStore.schedules"
            :key="s.id"
            class="bg-gray-950 hover:bg-gray-900 transition-colors"
          >
            <td class="px-4 py-3 text-white font-medium">{{ s.name }}</td>
            <td class="px-4 py-3 text-gray-300 font-mono text-xs">{{ s.cron_expression }}</td>
            <td class="px-4 py-3 text-gray-400">{{ inventoryName(s.inventory_id) }}</td>
            <td class="px-4 py-3 text-gray-300 font-mono text-xs truncate max-w-xs">
              {{ s.playbook_path }}
            </td>
            <td class="px-4 py-3">
              <button
                v-if="canManage"
                class="text-xs px-2 py-0.5 rounded-full border transition-colors"
                :class="
                  s.enabled
                    ? 'border-green-700 text-green-400 hover:border-green-500'
                    : 'border-gray-700 text-gray-500 hover:border-gray-500'
                "
                @click="handleToggle(s)"
              >
                {{ s.enabled ? 'Activo' : 'Inactivo' }}
              </button>
              <span
                v-else
                class="text-xs px-2 py-0.5 rounded-full border"
                :class="
                  s.enabled
                    ? 'border-green-700 text-green-400'
                    : 'border-gray-700 text-gray-500'
                "
              >
                {{ s.enabled ? 'Activo' : 'Inactivo' }}
              </span>
            </td>
            <td class="px-4 py-3 text-gray-500">{{ formatDate(s.created_at) }}</td>
            <td class="px-4 py-3 text-right">
              <button
                v-if="isAdmin"
                class="text-gray-600 hover:text-red-400 transition-colors text-xs"
                @click="scheduleToDelete = s.id"
              >
                Eliminar
              </button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- Pagination -->
    <div v-if="!schedulesStore.loading && schedulesStore.schedules.length" class="flex items-center justify-between mt-4 text-sm text-gray-500">
      <span>Página {{ schedulesStore.page + 1 }}</span>
      <div class="flex gap-2">
        <button
          :disabled="schedulesStore.page === 0"
          class="px-3 py-1 rounded border border-gray-800 hover:border-gray-600 disabled:opacity-30 disabled:cursor-not-allowed transition-colors"
          @click="schedulesStore.prevPage()"
        >
          ← Anterior
        </button>
        <button
          :disabled="!schedulesStore.hasMore"
          class="px-3 py-1 rounded border border-gray-800 hover:border-gray-600 disabled:opacity-30 disabled:cursor-not-allowed transition-colors"
          @click="schedulesStore.nextPage()"
        >
          Siguiente →
        </button>
      </div>
    </div>

    <!-- Confirm delete -->
    <ConfirmModal
      :open="scheduleToDelete !== null"
      title="Eliminar schedule"
      message="¿Eliminar este schedule? Se desregistrará de Celery Beat y no se ejecutará más."
      confirm-label="Eliminar"
      @confirm="confirmDelete"
      @cancel="scheduleToDelete = null"
    />
  </div>
</template>
