import { apiClient } from './client'

export interface HealthResponse {
  status: string
  version: string
}

export async function fetchHealth(): Promise<HealthResponse> {
  const { data } = await apiClient.get<HealthResponse>('/health')
  return data
}
