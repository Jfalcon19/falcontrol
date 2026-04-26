import axios from 'axios'

export const ACCESS_TOKEN_KEY = 'fc_access'
export const REFRESH_TOKEN_KEY = 'fc_refresh'

export const apiClient = axios.create({
  baseURL: '/api',
  headers: { 'Content-Type': 'application/json' },
})

apiClient.interceptors.request.use((config) => {
  const token = localStorage.getItem(ACCESS_TOKEN_KEY)
  if (token) config.headers.Authorization = `Bearer ${token}`
  return config
})

let refreshing: Promise<string> | null = null

apiClient.interceptors.response.use(
  (response) => response,
  async (error: unknown) => {
    if (!axios.isAxiosError(error)) return Promise.reject(error)

    const original = error.config as typeof error.config & { _retry?: boolean }
    if (error.response?.status !== 401 || original?._retry) {
      return Promise.reject(error)
    }
    original._retry = true

    if (!refreshing) {
      refreshing = (async () => {
        const rt = localStorage.getItem(REFRESH_TOKEN_KEY)
        if (!rt) throw new Error('no refresh token')
        const { data } = await axios.post<{ access_token: string; refresh_token: string }>(
          '/api/auth/refresh',
          { refresh_token: rt },
        )
        localStorage.setItem(ACCESS_TOKEN_KEY, data.access_token)
        localStorage.setItem(REFRESH_TOKEN_KEY, data.refresh_token)
        return data.access_token
      })().finally(() => {
        refreshing = null
      })
    }

    try {
      const token = await refreshing
      if (original?.headers) original.headers.Authorization = `Bearer ${token}`
      return apiClient(original!)
    } catch {
      localStorage.removeItem(ACCESS_TOKEN_KEY)
      localStorage.removeItem(REFRESH_TOKEN_KEY)
      window.dispatchEvent(new Event('fc:logout'))
      return Promise.reject(error)
    }
  },
)
