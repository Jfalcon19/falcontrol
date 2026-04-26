import { ref, computed } from 'vue'
import { defineStore } from 'pinia'
import { ACCESS_TOKEN_KEY, REFRESH_TOKEN_KEY } from '@/api/client'
import * as authApi from '@/api/auth'
import type { LoginCredentials, User } from '@/types'

export const useAuthStore = defineStore('auth', () => {
  const user = ref<User | null>(null)
  const accessToken = ref<string | null>(localStorage.getItem(ACCESS_TOKEN_KEY))

  const isAuthenticated = computed(() => !!accessToken.value)

  function _persist(access: string, refresh: string): void {
    accessToken.value = access
    localStorage.setItem(ACCESS_TOKEN_KEY, access)
    localStorage.setItem(REFRESH_TOKEN_KEY, refresh)
  }

  function clear(): void {
    accessToken.value = null
    user.value = null
    localStorage.removeItem(ACCESS_TOKEN_KEY)
    localStorage.removeItem(REFRESH_TOKEN_KEY)
  }

  async function login(credentials: LoginCredentials): Promise<void> {
    const pair = await authApi.login(credentials)
    _persist(pair.access_token, pair.refresh_token)
    await fetchMe()
  }

  function logout(): void {
    clear()
  }

  async function fetchMe(): Promise<void> {
    user.value = await authApi.me()
  }

  // Forced logout triggered by the axios interceptor on unrecoverable 401
  window.addEventListener('fc:logout', () => clear())

  return { user, isAuthenticated, login, logout, fetchMe, clear }
})
