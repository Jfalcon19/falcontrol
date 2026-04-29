<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useHostsStore } from '@/stores/hosts'
import { useAuthStore } from '@/stores/auth'
import OsTypeBadge from '@/components/OsTypeBadge.vue'
import ConnectionTypeBadge from '@/components/ConnectionTypeBadge.vue'
import TagChips from '@/components/TagChips.vue'
import ConfirmModal from '@/components/ConfirmModal.vue'
import type { Host, HostCreate, HostUpdate, OsType, ConnectionType } from '@/types'

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
  address: string
  description: string
  os_type: OsType
  connection_type: ConnectionType
  port: string
  tags: string
  is_active: boolean
}>({
  name: '',
  address: '',
  description: '',
  os_type: 'linux',
  connection_type: 'ssh',
  port: '',
  tags: '',
  is_active: true,
})

function openCreate() {
  modalMode.value = 'create'
  editingId.value = null
  form.value = {
    name: '',
    address: '',
    description: '',
    os_type: 'linux',
    connection_type: 'ssh',
    port: '',
    tags: '',
    is_active: true,
  }
  formError.value = null
  showModal.value = true
}

function openEdit(host: Host) {
  modalMode.value = 'edit'
  editingId.value = host.id
  form.value = {
    name: host.name,
    address: host.address,
    description: host.description ?? '',
    os_type: host.os_type,
    connection_type: host.connection_type,
    port: host.port !== null ? String(host.port) : '',
    tags: host.tags.join(', '),
    is_active: host.is_active,
  }
  formError.value = null
  showModal.value = true
}

function closeModal() {
  showModal.value = false
}

function buildPayload(): HostCreate | HostUpdate {
  const tags = form.value.tags
    .split(',')
    .map((t) => t.trim())
    .filter(Boolean)
  const port = form.value.port !== '' ? Number(form.value.port) : null
  return {
    name: form.value.name,
    address: form.value.address,
    description: form.value.description || null,
    os_type: form.value.os_type,
    connection_type: form.value.connection_type,
    port,
    tags,
    is_active: form.value.is_active,
  }
}

async function saveHost() {
  formError.value = null
  saving.value = true
  try {
    if (modalMode.value === 'create') {
      await hostsStore.create(buildPayload() as HostCreate)
    } else {
      await hostsStore.update(editingId.value!, buildPayload() as HostUpdate)
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

const deletingHost = ref<Host | null>(null)
const deleting = ref(false)

function confirmDelete(host: Host) {
  deletingHost.value = host
}

async function doDelete() {
  if (!deletingHost.value) return
  deleting.value = true
  try {
    await hostsStore.remove(deletingHost.value.id)
    deletingHost.value = null
  } finally {
    deleting.value = false
  }
}

// ── Init ───────────────────────────────────────────────────────────────────

onMounted(() => hostsStore.fetchAll())
</script>

<template>
  <div class="space-y-4">
    <!-- Page header -->
    <div class="flex items-center justify-between">
      <h1 class="text-xl font-semibold text-white">Hosts</h1>
      <button
        v-if="canWrite"
        class="px-4 py-1.5 text-sm rounded-lg bg-brand-600 hover:bg-brand-500 text-white transition-colors"
        @click="openCreate"
      >
        + Nuevo host
      </button>
    </div>

    <!-- Loading -->
    <div v-if="hostsStore.loading" class="text-gray-400 text-sm">Cargando…</div>

    <!-- Error -->
    <div v-else-if="hostsStore.error" class="text-red-400 text-sm">{{ hostsStore.error }}</div>

    <!-- Empty -->
    <div
      v-else-if="hostsStore.hosts.length === 0"
      class="text-center py-16 text-gray-600 text-sm"
    >
      No hay hosts todavía.
    </div>

    <!-- Table -->
    <div v-else class="overflow-x-auto rounded-xl border border-gray-800">
      <table class="w-full text-sm text-left">
        <thead class="bg-gray-900 text-gray-400 uppercase text-xs tracking-wider">
          <tr>
            <th class="px-4 py-3">Nombre</th>
            <th class="px-4 py-3">Dirección</th>
            <th class="px-4 py-3">SO</th>
            <th class="px-4 py-3">Conexión</th>
            <th class="px-4 py-3">Puerto</th>
            <th class="px-4 py-3">Tags</th>
            <th class="px-4 py-3">Estado</th>
            <th class="px-4 py-3"></th>
          </tr>
        </thead>
        <tbody class="divide-y divide-gray-800">
          <tr
            v-for="host in hostsStore.hosts"
            :key="host.id"
            class="bg-gray-950 hover:bg-gray-900 transition-colors"
          >
            <td class="px-4 py-3 font-medium text-white">{{ host.name }}</td>
            <td class="px-4 py-3 text-gray-300 font-mono text-xs">{{ host.address }}</td>
            <td class="px-4 py-3"><OsTypeBadge :os="host.os_type" /></td>
            <td class="px-4 py-3"><ConnectionTypeBadge :conn="host.connection_type" /></td>
            <td class="px-4 py-3 text-gray-400">{{ host.port ?? '—' }}</td>
            <td class="px-4 py-3"><TagChips :tags="host.tags" /></td>
            <td class="px-4 py-3">
              <span
                class="text-xs px-2 py-0.5 rounded-full border"
                :class="
                  host.is_active
                    ? 'border-green-700 text-green-400'
                    : 'border-gray-700 text-gray-500'
                "
              >
                {{ host.is_active ? 'Activo' : 'Inactivo' }}
              </span>
            </td>
            <td class="px-4 py-3">
              <div class="flex items-center gap-3 justify-end">
                <button
                  v-if="canWrite"
                  class="text-gray-500 hover:text-white text-xs transition-colors"
                  @click="openEdit(host)"
                >
                  Editar
                </button>
                <button
                  v-if="canDelete"
                  class="text-gray-500 hover:text-red-400 text-xs transition-colors"
                  @click="confirmDelete(host)"
                >
                  Borrar
                </button>
              </div>
            </td>
          </tr>
        </tbody>
      </table>
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
          {{ modalMode === 'create' ? 'Nuevo host' : 'Editar host' }}
        </h2>

        <form class="space-y-3" @submit.prevent="saveHost">
          <div class="grid grid-cols-2 gap-3">
            <div class="space-y-1">
              <label class="text-xs text-gray-400">Nombre *</label>
              <input
                v-model="form.name"
                required
                class="w-full bg-gray-800 border border-gray-700 rounded-lg px-3 py-1.5 text-sm text-white focus:outline-none focus:border-brand-500"
              />
            </div>
            <div class="space-y-1">
              <label class="text-xs text-gray-400">Dirección *</label>
              <input
                v-model="form.address"
                required
                class="w-full bg-gray-800 border border-gray-700 rounded-lg px-3 py-1.5 text-sm text-white focus:outline-none focus:border-brand-500"
              />
            </div>
          </div>

          <div class="space-y-1">
            <label class="text-xs text-gray-400">Descripción</label>
            <input
              v-model="form.description"
              class="w-full bg-gray-800 border border-gray-700 rounded-lg px-3 py-1.5 text-sm text-white focus:outline-none focus:border-brand-500"
            />
          </div>

          <div class="grid grid-cols-3 gap-3">
            <div class="space-y-1">
              <label class="text-xs text-gray-400">SO *</label>
              <select
                v-model="form.os_type"
                class="w-full bg-gray-800 border border-gray-700 rounded-lg px-3 py-1.5 text-sm text-white focus:outline-none focus:border-brand-500"
              >
                <option value="linux">Linux</option>
                <option value="windows">Windows</option>
              </select>
            </div>
            <div class="space-y-1">
              <label class="text-xs text-gray-400">Conexión *</label>
              <select
                v-model="form.connection_type"
                class="w-full bg-gray-800 border border-gray-700 rounded-lg px-3 py-1.5 text-sm text-white focus:outline-none focus:border-brand-500"
              >
                <option value="ssh">SSH</option>
                <option value="winrm">WinRM</option>
              </select>
            </div>
            <div class="space-y-1">
              <label class="text-xs text-gray-400">Puerto</label>
              <input
                v-model="form.port"
                type="number"
                min="1"
                max="65535"
                placeholder="22"
                class="w-full bg-gray-800 border border-gray-700 rounded-lg px-3 py-1.5 text-sm text-white focus:outline-none focus:border-brand-500"
              />
            </div>
          </div>

          <div class="space-y-1">
            <label class="text-xs text-gray-400">Tags (separados por coma)</label>
            <input
              v-model="form.tags"
              placeholder="web, prod, db"
              class="w-full bg-gray-800 border border-gray-700 rounded-lg px-3 py-1.5 text-sm text-white focus:outline-none focus:border-brand-500"
            />
          </div>

          <label class="flex items-center gap-2 text-sm text-gray-300 cursor-pointer">
            <input v-model="form.is_active" type="checkbox" class="rounded" />
            Activo
          </label>

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
      v-if="deletingHost"
      title="Eliminar host"
      :message="`¿Eliminar el host «${deletingHost.name}»? Esta acción no se puede deshacer.`"
      :loading="deleting"
      @confirm="doDelete"
      @cancel="deletingHost = null"
    />
  </Teleport>
</template>
