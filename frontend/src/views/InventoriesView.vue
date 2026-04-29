<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useInventoriesStore } from '@/stores/inventories'
import { useHostsStore } from '@/stores/hosts'
import { useAuthStore } from '@/stores/auth'
import ConfirmModal from '@/components/ConfirmModal.vue'
import type { Inventory, InventoryCreate, InventoryUpdate } from '@/types'

const inventoriesStore = useInventoriesStore()
const hostsStore = useHostsStore()
const auth = useAuthStore()

const canWrite = ['admin', 'operator'].includes(auth.user?.role ?? '')
const canDelete = auth.user?.role === 'admin'

// ── Modal state ────────────────────────────────────────────────────────────

type ModalMode = 'create' | 'edit'
const showModal = ref(false)
const modalMode = ref<ModalMode>('create')
const editingId = ref<string | null>(null)
const saving = ref(false)
const formError = ref<string | null>(null)

const form = ref<{
  name: string
  description: string
  selectedHostIds: Set<string>
}>({
  name: '',
  description: '',
  selectedHostIds: new Set(),
})

function openCreate() {
  modalMode.value = 'create'
  editingId.value = null
  form.value = { name: '', description: '', selectedHostIds: new Set() }
  formError.value = null
  showModal.value = true
}

function openEdit(inv: Inventory) {
  modalMode.value = 'edit'
  editingId.value = inv.id
  form.value = {
    name: inv.name,
    description: inv.description ?? '',
    selectedHostIds: new Set(inv.hosts.map((h) => h.id)),
  }
  formError.value = null
  showModal.value = true
}

function closeModal() {
  showModal.value = false
}

function toggleHost(id: string) {
  if (form.value.selectedHostIds.has(id)) {
    form.value.selectedHostIds.delete(id)
  } else {
    form.value.selectedHostIds.add(id)
  }
  // trigger reactivity
  form.value.selectedHostIds = new Set(form.value.selectedHostIds)
}

async function saveInventory() {
  formError.value = null
  saving.value = true
  try {
    const payload: InventoryCreate | InventoryUpdate = {
      name: form.value.name,
      description: form.value.description || null,
      host_ids: Array.from(form.value.selectedHostIds),
    }
    if (modalMode.value === 'create') {
      await inventoriesStore.create(payload as InventoryCreate)
    } else {
      await inventoriesStore.update(editingId.value!, payload as InventoryUpdate)
    }
    closeModal()
  } catch (e: unknown) {
    const err = e as { response?: { data?: { detail?: string } } }
    formError.value = err.response?.data?.detail ?? 'Error al guardar'
  } finally {
    saving.value = false
  }
}

// ── Delete state ───────────────────────────────────────────────────────────

const deletingInv = ref<Inventory | null>(null)
const deleting = ref(false)

function confirmDelete(inv: Inventory) {
  deletingInv.value = inv
}

async function doDelete() {
  if (!deletingInv.value) return
  deleting.value = true
  try {
    await inventoriesStore.remove(deletingInv.value.id)
    deletingInv.value = null
  } finally {
    deleting.value = false
  }
}

// ── Init ───────────────────────────────────────────────────────────────────

onMounted(async () => {
  await Promise.all([inventoriesStore.fetchAll(), hostsStore.fetchAll()])
})
</script>

<template>
  <div class="space-y-4">
    <!-- Page header -->
    <div class="flex items-center justify-between">
      <h1 class="text-xl font-semibold text-white">Inventarios</h1>
      <button
        v-if="canWrite"
        class="px-4 py-1.5 text-sm rounded-lg bg-brand-600 hover:bg-brand-500 text-white transition-colors"
        @click="openCreate"
      >
        + Nuevo inventario
      </button>
    </div>

    <!-- Loading -->
    <div v-if="inventoriesStore.loading" class="text-gray-400 text-sm">Cargando…</div>

    <!-- Error -->
    <div v-else-if="inventoriesStore.error" class="text-red-400 text-sm">
      {{ inventoriesStore.error }}
    </div>

    <!-- Empty -->
    <div
      v-else-if="inventoriesStore.inventories.length === 0"
      class="text-center py-16 text-gray-600 text-sm"
    >
      No hay inventarios todavía.
    </div>

    <!-- Cards -->
    <div v-else class="grid grid-cols-1 gap-4 sm:grid-cols-2 xl:grid-cols-3">
      <div
        v-for="inv in inventoriesStore.inventories"
        :key="inv.id"
        class="bg-gray-900 border border-gray-800 rounded-xl p-4 space-y-3"
      >
        <div class="flex items-start justify-between gap-2">
          <div>
            <p class="text-white font-medium text-sm">{{ inv.name }}</p>
            <p v-if="inv.description" class="text-gray-500 text-xs mt-0.5">
              {{ inv.description }}
            </p>
          </div>
          <div class="flex gap-2 shrink-0">
            <button
              v-if="canWrite"
              class="text-gray-500 hover:text-white text-xs transition-colors"
              @click="openEdit(inv)"
            >
              Editar
            </button>
            <button
              v-if="canDelete"
              class="text-gray-500 hover:text-red-400 text-xs transition-colors"
              @click="confirmDelete(inv)"
            >
              Borrar
            </button>
          </div>
        </div>

        <div>
          <p class="text-xs text-gray-500 mb-1">
            {{ inv.hosts.length }} host{{ inv.hosts.length !== 1 ? 's' : '' }}
          </p>
          <div class="flex flex-wrap gap-1">
            <span
              v-for="host in inv.hosts"
              :key="host.id"
              class="text-xs px-2 py-0.5 rounded-md bg-gray-800 text-gray-300 border border-gray-700"
            >
              {{ host.name }}
            </span>
            <span v-if="inv.hosts.length === 0" class="text-xs text-gray-600">Sin hosts</span>
          </div>
        </div>
      </div>
    </div>
  </div>

  <!-- Create / Edit modal -->
  <Teleport to="body">
    <div
      v-if="showModal"
      class="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm"
    >
      <div class="bg-gray-900 border border-gray-700 rounded-xl p-6 w-full max-w-lg shadow-xl">
        <h2 class="text-white font-semibold text-base mb-4">
          {{ modalMode === 'create' ? 'Nuevo inventario' : 'Editar inventario' }}
        </h2>

        <form class="space-y-3" @submit.prevent="saveInventory">
          <div class="space-y-1">
            <label class="text-xs text-gray-400">Nombre *</label>
            <input
              v-model="form.name"
              required
              class="w-full bg-gray-800 border border-gray-700 rounded-lg px-3 py-1.5 text-sm text-white focus:outline-none focus:border-brand-500"
            />
          </div>

          <div class="space-y-1">
            <label class="text-xs text-gray-400">Descripción</label>
            <input
              v-model="form.description"
              class="w-full bg-gray-800 border border-gray-700 rounded-lg px-3 py-1.5 text-sm text-white focus:outline-none focus:border-brand-500"
            />
          </div>

          <div class="space-y-1">
            <label class="text-xs text-gray-400">Hosts</label>
            <div
              class="bg-gray-800 border border-gray-700 rounded-lg p-2 max-h-48 overflow-y-auto space-y-1"
            >
              <div v-if="hostsStore.hosts.length === 0" class="text-xs text-gray-600 px-2 py-1">
                No hay hosts disponibles
              </div>
              <label
                v-for="host in hostsStore.hosts"
                :key="host.id"
                class="flex items-center gap-2 px-2 py-1.5 rounded-lg cursor-pointer hover:bg-gray-700 transition-colors"
              >
                <input
                  type="checkbox"
                  :checked="form.selectedHostIds.has(host.id)"
                  class="rounded"
                  @change="toggleHost(host.id)"
                />
                <span class="text-sm text-gray-200">{{ host.name }}</span>
                <span class="text-xs text-gray-500 font-mono">{{ host.address }}</span>
              </label>
            </div>
          </div>

          <div v-if="formError" class="text-red-400 text-xs">{{ formError }}</div>

          <div class="flex justify-end gap-3 pt-2">
            <button
              type="button"
              class="px-4 py-1.5 text-sm rounded-lg border border-gray-700 text-gray-300 hover:border-gray-500 transition-colors"
              :disabled="saving"
              @click="closeModal"
            >
              Cancelar
            </button>
            <button
              type="submit"
              class="px-4 py-1.5 text-sm rounded-lg bg-brand-600 hover:bg-brand-500 text-white transition-colors disabled:opacity-50"
              :disabled="saving"
            >
              {{ saving ? 'Guardando…' : 'Guardar' }}
            </button>
          </div>
        </form>
      </div>
    </div>
  </Teleport>

  <!-- Delete confirmation -->
  <Teleport to="body">
    <ConfirmModal
      v-if="deletingInv"
      title="Eliminar inventario"
      :message="`¿Eliminar el inventario «${deletingInv.name}»? Esta acción no se puede deshacer.`"
      :loading="deleting"
      @confirm="doDelete"
      @cancel="deletingInv = null"
    />
  </Teleport>
</template>
