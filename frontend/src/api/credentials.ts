import { apiClient } from '@/api/client'
import type { Credential, CredentialCreate, CredentialUpdate } from '@/types'

export async function listCredentials(): Promise<Credential[]> {
  const { data } = await apiClient.get<Credential[]>('/credentials')
  return data
}

export async function getCredential(id: string): Promise<Credential> {
  const { data } = await apiClient.get<Credential>(`/credentials/${id}`)
  return data
}

export async function createCredential(payload: CredentialCreate): Promise<Credential> {
  const { data } = await apiClient.post<Credential>('/credentials', payload)
  return data
}

export async function updateCredential(
  id: string,
  payload: CredentialUpdate,
): Promise<Credential> {
  const { data } = await apiClient.patch<Credential>(`/credentials/${id}`, payload)
  return data
}

export async function deleteCredential(id: string): Promise<void> {
  await apiClient.delete(`/credentials/${id}`)
}
