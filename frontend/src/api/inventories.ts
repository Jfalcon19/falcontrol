import { apiClient } from '@/api/client'
import type { Inventory, InventoryCreate, InventoryUpdate } from '@/types'

export async function listInventories(): Promise<Inventory[]> {
  const { data } = await apiClient.get<Inventory[]>('/inventories')
  return data
}

export async function getInventory(id: string): Promise<Inventory> {
  const { data } = await apiClient.get<Inventory>(`/inventories/${id}`)
  return data
}

export async function createInventory(payload: InventoryCreate): Promise<Inventory> {
  const { data } = await apiClient.post<Inventory>('/inventories', payload)
  return data
}

export async function updateInventory(id: string, payload: InventoryUpdate): Promise<Inventory> {
  const { data } = await apiClient.patch<Inventory>(`/inventories/${id}`, payload)
  return data
}

export async function deleteInventory(id: string): Promise<void> {
  await apiClient.delete(`/inventories/${id}`)
}
