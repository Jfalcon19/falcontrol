export interface ApiError {
  detail: string
}

export interface User {
  id: string
  email: string
  role: 'admin' | 'operator' | 'viewer'
  is_active: boolean
  created_at: string
}

export interface TokenPair {
  access_token: string
  refresh_token: string
  token_type: string
}

export interface LoginCredentials {
  email: string
  password: string
}
