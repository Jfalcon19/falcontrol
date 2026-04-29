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

// ── Jobs ───────────────────────────────────────────────────────────────────

export type JobStatus = 'pending' | 'running' | 'success' | 'failed'

export interface Job {
  id: string
  inventory_id: string
  playbook_path: string
  status: JobStatus
  return_code: number | null
  started_at: string | null
  finished_at: string | null
  created_at: string
}

export interface JobDetail extends Job {
  stdout: string | null
}

export interface JobCreate {
  inventory_id: string
  playbook_path: string
}

// ── Schedules ──────────────────────────────────────────────────────────────

export interface Schedule {
  id: string
  name: string
  cron_expression: string
  inventory_id: string
  playbook_path: string
  enabled: boolean
  created_at: string
  updated_at: string | null
}

export interface ScheduleCreate {
  name: string
  cron_expression: string
  inventory_id: string
  playbook_path: string
  enabled?: boolean
}

export interface ScheduleUpdate {
  name?: string
  cron_expression?: string
  inventory_id?: string
  playbook_path?: string
  enabled?: boolean
}

// ── Dashboard ──────────────────────────────────────────────────────────────

export interface DashboardStats {
  total_hosts: number
  total_inventories: number
  total_schedules: number
  total_jobs: number
  running_jobs: number
  failed_last_24h: number
  recent_jobs: Job[]
}

// ── Credentials ────────────────────────────────────────────────────────────

export type CredentialType = 'ssh_key' | 'ssh_password' | 'winrm'

export interface Credential {
  id: string
  name: string
  description: string | null
  credential_type: CredentialType
  username: string | null
  created_at: string
  updated_at: string | null
}

export interface CredentialCreate {
  name: string
  description?: string | null
  credential_type: CredentialType
  username?: string | null
  secret: string
  passphrase?: string | null
}

export interface CredentialUpdate {
  name?: string
  description?: string | null
  username?: string | null
  secret?: string
  passphrase?: string | null
}
