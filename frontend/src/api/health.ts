import axios from 'axios'

export interface HealthResponse {
  status: string
  version: string
}

export async function fetchHealth(): Promise<HealthResponse> {
  const { data } = await axios.get<HealthResponse>('/api/health')
  return data
}
