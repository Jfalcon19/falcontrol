import { apiClient } from '@/api/client'
import type { Host, HostCreate, HostUpdate } from '@/types'

export async function listHosts(): Promise<Host[]> {
  const { data } = await apiClient.get<Host[]>('/hosts')
  return data
}

export async function getHost(id: string): Promise<Host> {
  const { data } = await apiClient.get<Host>(`/hosts/${id}`)
  return data
}

export async function createHost(payload: HostCreate): Promise<Host> {
  const { data } = await apiClient.post<Host>('/hosts', payload)
  return data
}

export async function updateHost(id: string, payload: HostUpdate): Promise<Host> {
  const { data } = await apiClient.patch<Host>(`/hosts/${id}`, payload)
  return data
}

export async function deleteHost(id: string): Promise<void> {
  await apiClient.delete(`/hosts/${id}`)
}
