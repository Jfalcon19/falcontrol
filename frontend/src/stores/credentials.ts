import { ref } from 'vue'
import { defineStore } from 'pinia'
import * as credentialsApi from '@/api/credentials'
import type { Credential, CredentialCreate, CredentialUpdate } from '@/types'

export const useCredentialsStore = defineStore('credentials', () => {
  const credentials = ref<Credential[]>([])
  const loading = ref(false)
  const error = ref<string | null>(null)

  async function fetchAll(): Promise<void> {
    loading.value = true
    error.value = null
    try {
      credentials.value = await credentialsApi.listCredentials()
    } catch {
      error.value = 'Error al cargar las credenciales'
    } finally {
      loading.value = false
    }
  }

  async function create(payload: CredentialCreate): Promise<Credential> {
    const cred = await credentialsApi.createCredential(payload)
    credentials.value.push(cred)
    return cred
  }

  async function update(id: string, payload: CredentialUpdate): Promise<Credential> {
    const updated = await credentialsApi.updateCredential(id, payload)
    const idx = credentials.value.findIndex((c) => c.id === id)
    if (idx !== -1) credentials.value[idx] = updated
    return updated
  }

  async function remove(id: string): Promise<void> {
    await credentialsApi.deleteCredential(id)
    credentials.value = credentials.value.filter((c) => c.id !== id)
  }

  return { credentials, loading, error, fetchAll, create, update, remove }
})
