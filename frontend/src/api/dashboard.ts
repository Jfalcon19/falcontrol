import axios from 'axios'
import type { DashboardStats } from '@/types'

export async function getDashboardStats(): Promise<DashboardStats> {
  const { data } = await axios.get<DashboardStats>('/api/dashboard')
  return data
}
