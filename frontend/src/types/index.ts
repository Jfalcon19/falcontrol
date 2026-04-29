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

// ── Hosts ──────────────────────────────────────────────────────────────────

export type OsType = 'linux' | 'windows'
export type ConnectionType = 'ssh' | 'winrm'

export interface Host {
  id: string
  name: string
  address: string
  description: string | null
  os_type: OsType
  connection_type: ConnectionType
  port: number | null
  tags: string[]
  is_active: boolean
  created_at: string
  updated_at: string | null
}

export interface HostCreate {
  name: string
  address: string
  description?: string | null
  os_type: OsType
  connection_type: ConnectionType
  port?: number | null
  tags?: string[]
  is_active?: boolean
}

export interface HostUpdate {
  name?: string
  address?: string
  description?: string | null
  os_type?: OsType
  connection_type?: ConnectionType
  port?: number | null
  tags?: string[]
  is_active?: boolean
}

// ── Inventories ────────────────────────────────────────────────────────────

export interface Inventory {
  id: string
  name: string
  description: string | null
  hosts: Host[]
  created_at: string
  updated_at: string | null
}

export interface InventoryCreate {
  name: string
  description?: string | null
  host_ids?: string[]
}

export interface InventoryUpdate {
  name?: string
  description?: string | null
  host_ids?: string[]
}
