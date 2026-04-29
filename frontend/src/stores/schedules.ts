import { defineStore } from 'pinia'
import { ref } from 'vue'
import {
  listSchedules,
  createSchedule,
  updateSchedule,
  deleteSchedule,
} from '@/api/schedules'
import type { Schedule, ScheduleCreate } from '@/types'

const PAGE_SIZE = 20

export const useSchedulesStore = defineStore('schedules', () => {
  const schedules = ref<Schedule[]>([])
  const loading = ref(false)
  const error = ref<string | null>(null)
  const page = ref(0)
  const hasMore = ref(true)

  async function fetchAll(resetPage = true) {
    if (resetPage) page.value = 0
    loading.value = true
    error.value = null
    try {
      const result = await listSchedules(page.value * PAGE_SIZE, PAGE_SIZE)
      schedules.value = result
      hasMore.value = result.length === PAGE_SIZE
    } catch {
      error.value = 'Error al cargar los schedules'
    } finally {
      loading.value = false
    }
  }

  async function nextPage() {
    page.value++
    await fetchAll(false)
  }

  async function prevPage() {
    if (page.value > 0) {
      page.value--
      await fetchAll(false)
    }
  }

  async function addSchedule(payload: ScheduleCreate): Promise<Schedule | null> {
    error.value = null
    try {
      const s = await createSchedule(payload)
      schedules.value.push(s)
      return s
    } catch (err: unknown) {
      if (err && typeof err === 'object' && 'response' in err) {
        const resp = (err as { response?: { status?: number } }).response
        if (resp?.status === 409) {
          error.value = 'Ya existe un schedule con ese nombre'
        } else {
          error.value = 'Error al crear el schedule'
        }
      } else {
        error.value = 'Error al crear el schedule'
      }
      return null
    }
  }

  async function toggleEnabled(schedule: Schedule): Promise<void> {
    const updated = await updateSchedule(schedule.id, { enabled: !schedule.enabled })
    const idx = schedules.value.findIndex((s) => s.id === schedule.id)
    if (idx !== -1) schedules.value[idx] = updated
  }

  async function removeSchedule(id: string): Promise<void> {
    await deleteSchedule(id)
    schedules.value = schedules.value.filter((s) => s.id !== id)
  }

  return { schedules, loading, error, page, hasMore, fetchAll, nextPage, prevPage, addSchedule, toggleEnabled, removeSchedule }
})
