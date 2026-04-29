import axios from 'axios'
import type { Job, JobCreate, JobDetail } from '@/types'

const base = '/api/jobs'

export async function listJobs(): Promise<Job[]> {
  const { data } = await axios.get<Job[]>(base)
  return data
}

export async function getJob(id: string): Promise<JobDetail> {
  const { data } = await axios.get<JobDetail>(`${base}/${id}`)
  return data
}

export async function createJob(payload: JobCreate): Promise<Job> {
  const { data } = await axios.post<Job>(base, payload)
  return data
}

export async function deleteJob(id: string): Promise<void> {
  await axios.delete(`${base}/${id}`)
}
