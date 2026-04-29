import axios from 'axios'
import type { Schedule, ScheduleCreate, ScheduleUpdate } from '@/types'

const base = '/api/schedules'

export async function listSchedules(skip = 0, limit = 20): Promise<Schedule[]> {
  const { data } = await axios.get<Schedule[]>(base, { params: { skip, limit } })
  return data
}

export async function getSchedule(id: string): Promise<Schedule> {
  const { data } = await axios.get<Schedule>(`${base}/${id}`)
  return data
}

export async function createSchedule(payload: ScheduleCreate): Promise<Schedule> {
  const { data } = await axios.post<Schedule>(base, payload)
  return data
}

export async function updateSchedule(id: string, payload: ScheduleUpdate): Promise<Schedule> {
  const { data } = await axios.patch<Schedule>(`${base}/${id}`, payload)
  return data
}

export async function deleteSchedule(id: string): Promise<void> {
  await axios.delete(`${base}/${id}`)
}
