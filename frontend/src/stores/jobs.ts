import { defineStore } from 'pinia'
import { ref } from 'vue'
import { listJobs, getJob, createJob, deleteJob } from '@/api/jobs'
import type { Job, JobCreate, JobDetail } from '@/types'

const PAGE_SIZE = 20

export const useJobsStore = defineStore('jobs', () => {
  const jobs = ref<Job[]>([])
  const loading = ref(false)
  const error = ref<string | null>(null)
  const page = ref(0)
  const hasMore = ref(true)

  async function fetchJobs(resetPage = true) {
    if (resetPage) page.value = 0
    loading.value = true
    error.value = null
    try {
      const result = await listJobs(page.value * PAGE_SIZE, PAGE_SIZE)
      jobs.value = result
      hasMore.value = result.length === PAGE_SIZE
    } catch {
      error.value = 'Error al cargar los jobs'
    } finally {
      loading.value = false
    }
  }

  async function nextPage() {
    page.value++
    await fetchJobs(false)
  }

  async function prevPage() {
    if (page.value > 0) {
      page.value--
      await fetchJobs(false)
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

  return { jobs, loading, error, page, hasMore, fetchJobs, nextPage, prevPage, fetchJob, launchJob, removeJob }
})
