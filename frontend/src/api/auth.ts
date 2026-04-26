import { apiClient } from './client'
import type { LoginCredentials, TokenPair, User } from '@/types'

export async function login(credentials: LoginCredentials): Promise<TokenPair> {
  const { data } = await apiClient.post<TokenPair>('/auth/login', credentials)
  return data
}

export async function refresh(refreshToken: string): Promise<TokenPair> {
  const { data } = await apiClient.post<TokenPair>('/auth/refresh', { refresh_token: refreshToken })
  return data
}

export async function me(): Promise<User> {
  const { data } = await apiClient.get<User>('/auth/me')
  return data
}
