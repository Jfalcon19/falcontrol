import { ref } from 'vue'
import { defineStore } from 'pinia'
import * as inventoriesApi from '@/api/inventories'
import type { Inventory, InventoryCreate, InventoryUpdate } from '@/types'

export const useInventoriesStore = defineStore('inventories', () => {
  const inventories = ref<Inventory[]>([])
  const loading = ref(false)
  const error = ref<string | null>(null)

  async function fetchAll(): Promise<void> {
    loading.value = true
    error.value = null
    try {
      inventories.value = await inventoriesApi.listInventories()
    } catch {
      error.value = 'Error al cargar los inventarios'
    } finally {
      loading.value = false
    }
  }

  async function create(payload: InventoryCreate): Promise<Inventory> {
    const inv = await inventoriesApi.createInventory(payload)
    inventories.value.push(inv)
    return inv
  }

  async function update(id: string, payload: InventoryUpdate): Promise<Inventory> {
    const updated = await inventoriesApi.updateInventory(id, payload)
    const idx = inventories.value.findIndex((i) => i.id === id)
    if (idx !== -1) inventories.value[idx] = updated
    return updated
  }

  async function remove(id: string): Promise<void> {
    await inventoriesApi.deleteInventory(id)
    inventories.value = inventories.value.filter((i) => i.id !== id)
  }

  return { inventories, loading, error, fetchAll, create, update, remove }
})
