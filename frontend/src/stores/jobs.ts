import { defineStore } from 'pinia'
import { ref } from 'vue'
import { listJobs, getJob, createJob, deleteJob } from '@/api/jobs'
import type { Job, JobCreate, JobDetail } from '@/types'

export const useJobsStore = defineStore('jobs', () => {
  const jobs = ref<Job[]>([])
  const loading = ref(false)
  const error = ref<string | null>(null)

  async function fetchJobs() {
    loading.value = true
    error.value = null
    try {
      jobs.value = await listJobs()
    } catch {
      error.value = 'Error al cargar los jobs'
    } finally {
      loading.value = false
    }
  }

  async function fetchJob(id: string): Promise<JobDetail | null> {
    try {
      return await getJob(id)
    } catch {
      return null
    }
  }

  async function launchJob(payload: JobCreate): Promise<Job | null> {
    try {
      const job = await createJob(payload)
      jobs.value.unshift(job)
      return job
    } catch {
      error.value = 'Error al lanzar el job'
      return null
    }
  }

  async function removeJob(id: string) {
    await deleteJob(id)
    jobs.value = jobs.value.filter((j) => j.id !== id)
  }

  return { jobs, loading, error, fetchJobs, fetchJob, launchJob, removeJob }
})
