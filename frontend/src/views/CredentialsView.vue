<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useCredentialsStore } from '@/stores/credentials'
import { useAuthStore } from '@/stores/auth'
import CredentialTypeBadge from '@/components/CredentialTypeBadge.vue'
import ConfirmModal from '@/components/ConfirmModal.vue'
import type { Credential, CredentialCreate, CredentialUpdate, CredentialType } from '@/types'

const credStore = useCredentialsStore()
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
  credential_type: CredentialType
  username: string
  secret: string
  passphrase: string
}>({
  name: '',
  description: '',
  credential_type: 'ssh_key',
  username: '',
  secret: '',
  passphrase: '',
})

const needsUsername = computed(
  () => form.value.credential_type === 'ssh_password' || form.value.credential_type === 'winrm',
)
const showPassphrase = computed(() => form.value.credential_type === 'ssh_key')

function openCreate() {
  modalMode.value = 'create'
  editingId.value = null
  form.value = {
    name: '',
    description: '',
    credential_type: 'ssh_key',
    username: '',
    secret: '',
    passphrase: '',
  }
  formError.value = null
  showModal.value = true
}

function openEdit(cred: Credential) {
  modalMode.value = 'edit'
  editingId.value = cred.id
  form.value = {
    name: cred.name,
    description: cred.description ?? '',
    credential_type: cred.credential_type,
    username: cred.username ?? '',
    secret: '',
    passphrase: '',
  }
  formError.value = null
  showModal.value = true
}

function closeModal() {
  showModal.value = false
}

async function saveCredential() {
  formError.value = null
  saving.value = true
  try {
    if (modalMode.value === 'create') {
      const payload: CredentialCreate = {
        name: form.value.name,
        description: form.value.description || null,
        credential_type: form.value.credential_type,
        username: form.value.username || null,
        secret: form.value.secret,
        passphrase: form.value.passphrase || null,
      }
      await credStore.create(payload)
    } else {
      const payload: CredentialUpdate = {
        name: form.value.name,
        description: form.value.description || null,
        username: form.value.username || null,
      }
      if (form.value.secret) payload.secret = form.value.secret
      if (form.value.passphrase) payload.passphrase = form.value.passphrase
      await credStore.update(editingId.value!, payload)
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

const deletingCred = ref<Credential | null>(null)
const deleting = ref(false)

function confirmDelete(cred: Credential) {
  deletingCred.value = cred
}

async function doDelete() {
  if (!deletingCred.value) return
  deleting.value = true
  try {
    await credStore.remove(deletingCred.value.id)
    deletingCred.value = null
  } finally {
    deleting.value = false
  }
}

// ── Init ───────────────────────────────────────────────────────────────────

onMounted(() => credStore.fetchAll())
</script>

<template>
  <div class="space-y-4">
    <!-- Page header -->
    <div class="flex items-center justify-between">
      <h1 class="text-xl font-semibold text-white">Credenciales</h1>
      <button
        v-if="canWrite"
        class="px-4 py-1.5 text-sm rounded-lg bg-brand-600 hover:bg-brand-500 text-white transition-colors"
        @click="openCreate"
      >
        + Nueva credencial
      </button>
    </div>

    <!-- Loading -->
    <div v-if="credStore.loading" class="text-gray-400 text-sm">Cargando…</div>

    <!-- Error -->
    <div v-else-if="credStore.error" class="text-red-400 text-sm">{{ credStore.error }}</div>

    <!-- Empty -->
    <div
      v-else-if="credStore.credentials.length === 0"
      class="text-center py-16 text-gray-600 text-sm"
    >
      No hay credenciales todavía.
    </div>

    <!-- Table -->
    <div v-else class="overflow-x-auto rounded-xl border border-gray-800">
      <table class="w-full text-sm text-left">
        <thead class="bg-gray-900 text-gray-400 uppercase text-xs tracking-wider">
          <tr>
            <th class="px-4 py-3">Nombre</th>
            <th class="px-4 py-3">Tipo</th>
            <th class="px-4 py-3">Usuario</th>
            <th class="px-4 py-3">Descripción</th>
            <th class="px-4 py-3">Actualizado</th>
            <th class="px-4 py-3"></th>
          </tr>
        </thead>
        <tbody class="divide-y divide-gray-800">
          <tr
            v-for="cred in credStore.credentials"
            :key="cred.id"
            class="bg-gray-950 hover:bg-gray-900 transition-colors"
          >
            <td class="px-4 py-3 font-medium text-white">{{ cred.name }}</td>
            <td class="px-4 py-3"><CredentialTypeBadge :type="cred.credential_type" /></td>
            <td class="px-4 py-3 text-gray-300 font-mono text-xs">{{ cred.username ?? '—' }}</td>
            <td class="px-4 py-3 text-gray-400 text-xs max-w-xs truncate">
              {{ cred.description ?? '—' }}
            </td>
            <td class="px-4 py-3 text-gray-500 text-xs">
              {{ cred.updated_at ? new Date(cred.updated_at).toLocaleDateString() : '—' }}
            </td>
            <td class="px-4 py-3">
              <div class="flex items-center gap-3 justify-end">
                <button
                  v-if="canWrite"
                  class="text-gray-500 hover:text-white text-xs transition-colors"
                  @click="openEdit(cred)"
                >
                  Editar
                </button>
                <button
                  v-if="canDelete"
                  class="text-gray-500 hover:text-red-400 text-xs transition-colors"
                  @click="confirmDelete(cred)"
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
          {{ modalMode === 'create' ? 'Nueva credencial' : 'Editar credencial' }}
        </h2>

        <form class="space-y-3" @submit.prevent="saveCredential">
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
              <label class="text-xs text-gray-400">Tipo *</label>
              <select
                v-model="form.credential_type"
                :disabled="modalMode === 'edit'"
                class="w-full bg-gray-800 border border-gray-700 rounded-lg px-3 py-1.5 text-sm text-white focus:outline-none focus:border-brand-500 disabled:opacity-50"
              >
                <option value="ssh_key">SSH Key</option>
                <option value="ssh_password">SSH Password</option>
                <option value="winrm">WinRM</option>
              </select>
            </div>
          </div>

          <div class="space-y-1">
            <label class="text-xs text-gray-400">Descripción</label>
            <input
              v-model="form.description"
              class="w-full bg-gray-800 border border-gray-700 rounded-lg px-3 py-1.5 text-sm text-white focus:outline-none focus:border-brand-500"
            />
          </div>

          <div v-if="needsUsername" class="space-y-1">
            <label class="text-xs text-gray-400">Usuario *</label>
            <input
              v-model="form.username"
              :required="needsUsername"
              class="w-full bg-gray-800 border border-gray-700 rounded-lg px-3 py-1.5 text-sm text-white focus:outline-none focus:border-brand-500"
            />
          </div>

          <div class="space-y-1">
            <label class="text-xs text-gray-400">
              {{ modalMode === 'create' ? 'Secret *' : 'Secret (dejar vacío para no cambiar)' }}
            </label>
            <textarea
              v-model="form.secret"
              :required="modalMode === 'create'"
              rows="3"
              :placeholder="
                form.credential_type === 'ssh_key'
                  ? '-----BEGIN OPENSSH PRIVATE KEY-----'
                  : 'Contraseña'
              "
              class="w-full bg-gray-800 border border-gray-700 rounded-lg px-3 py-1.5 text-sm text-white font-mono focus:outline-none focus:border-brand-500 resize-none"
            />
          </div>

          <div v-if="showPassphrase" class="space-y-1">
            <label class="text-xs text-gray-400">Passphrase de la clave (opcional)</label>
            <input
              v-model="form.passphrase"
              type="password"
              class="w-full bg-gray-800 border border-gray-700 rounded-lg px-3 py-1.5 text-sm text-white focus:outline-none focus:border-brand-500"
            />
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
      v-if="deletingCred"
      title="Eliminar credencial"
      :message="`¿Eliminar la credencial «${deletingCred.name}»? Esta acción no se puede deshacer.`"
      :loading="deleting"
      @confirm="doDelete"
      @cancel="deletingCred = null"
    />
  </Teleport>
</template>
