import { ref } from 'vue'
import { defineStore } from 'pinia'
import * as hostsApi from '@/api/hosts'
import type { Host, HostCreate, HostUpdate } from '@/types'

export const useHostsStore = defineStore('hosts', () => {
  const hosts = ref<Host[]>([])
  const loading = ref(false)
  const error = ref<string | null>(null)

  async function fetchAll(): Promise<void> {
    loading.value = true
    error.value = null
    try {
      hosts.value = await hostsApi.listHosts()
    } catch {
      error.value = 'Error al cargar los hosts'
    } finally {
      loading.value = false
    }
  }

  async function create(payload: HostCreate): Promise<Host> {
    const host = await hostsApi.createHost(payload)
    hosts.value.push(host)
    return host
  }

  async function update(id: string, payload: HostUpdate): Promise<Host> {
    const updated = await hostsApi.updateHost(id, payload)
    const idx = hosts.value.findIndex((h) => h.id === id)
    if (idx !== -1) hosts.value[idx] = updated
    return updated
  }

  async function remove(id: string): Promise<void> {
    await hostsApi.deleteHost(id)
    hosts.value = hosts.value.filter((h) => h.id !== id)
  }

  return { hosts, loading, error, fetchAll, create, update, remove }
})
