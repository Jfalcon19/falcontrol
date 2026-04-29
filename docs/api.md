# Falcontrol API Reference

Base URL: `http://localhost/api`  
Swagger UI interactivo: `http://localhost/api/docs`

## Autenticación

Todos los endpoints (excepto `/auth/login`) requieren cabecera:

```
Authorization: Bearer <access_token>
```

El access token expira en **15 minutos**. Usa `/auth/refresh` para renovarlo.

---

## Auth

### POST /auth/login

Obtiene un par de tokens.

```bash
curl -X POST http://localhost/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "admin@empresa.com", "password": "tu_password"}'
```

**Respuesta 200:**
```json
{
  "access_token": "eyJ...",
  "refresh_token": "eyJ...",
  "token_type": "bearer"
}
```

### POST /auth/refresh

Renueva el access token usando el refresh token (válido 7 días).

```bash
curl -X POST http://localhost/api/auth/refresh \
  -H "Content-Type: application/json" \
  -d '{"refresh_token": "eyJ..."}'
```

### GET /auth/me

Devuelve el usuario autenticado.

```bash
curl http://localhost/api/auth/me \
  -H "Authorization: Bearer $TOKEN"
```

**Respuesta 200:**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "email": "admin@empresa.com",
  "role": "admin",
  "is_active": true,
  "created_at": "2026-01-01T00:00:00Z"
}
```

---

## Usuarios

> Requiere rol **admin**.

### POST /users

Crea un nuevo usuario.

```bash
curl -X POST http://localhost/api/users \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"email": "operador@empresa.com", "password": "password123", "role": "operator"}'
```

Roles disponibles: `admin`, `operator`, `viewer`.

---

## Hosts

### GET /hosts

Lista todos los hosts. Soporta paginación y filtro por estado.

```bash
# Todos los hosts activos (por defecto)
curl http://localhost/api/hosts \
  -H "Authorization: Bearer $TOKEN"

# Con paginación
curl "http://localhost/api/hosts?skip=0&limit=50" \
  -H "Authorization: Bearer $TOKEN"

# Incluir hosts inactivos
curl "http://localhost/api/hosts?active_only=false" \
  -H "Authorization: Bearer $TOKEN"
```

**Respuesta 200:**
```json
[
  {
    "id": "...",
    "name": "servidor-web-01",
    "address": "192.168.1.10",
    "description": "Servidor web principal",
    "os_type": "linux",
    "connection_type": "ssh",
    "port": 22,
    "tags": ["web", "produccion"],
    "is_active": true,
    "created_at": "2026-01-01T00:00:00Z",
    "updated_at": null
  }
]
```

### POST /hosts

> Requiere rol **operator** o **admin**.

```bash
curl -X POST http://localhost/api/hosts \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "servidor-db-01",
    "address": "192.168.1.20",
    "os_type": "linux",
    "connection_type": "ssh",
    "port": 22,
    "tags": ["db", "produccion"],
    "description": "Base de datos principal"
  }'
```

`os_type`: `linux` | `windows`  
`connection_type`: `ssh` | `winrm`

### GET /hosts/{host_id}

```bash
curl http://localhost/api/hosts/550e8400-e29b-41d4-a716-446655440000 \
  -H "Authorization: Bearer $TOKEN"
```

### PATCH /hosts/{host_id}

> Requiere rol **operator** o **admin**. Solo se actualizan los campos enviados.

```bash
curl -X PATCH http://localhost/api/hosts/550e8400-e29b-41d4-a716-446655440000 \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"description": "Nueva descripción", "tags": ["web"]}'
```

### DELETE /hosts/{host_id}

> Requiere rol **admin**.

```bash
curl -X DELETE http://localhost/api/hosts/550e8400-e29b-41d4-a716-446655440000 \
  -H "Authorization: Bearer $TOKEN"
```

Responde `204 No Content`.

---

## Inventarios

Los inventarios agrupan hosts para ejecutar playbooks sobre ellos.

### GET /inventories

```bash
curl http://localhost/api/inventories \
  -H "Authorization: Bearer $TOKEN"
```

**Respuesta 200:**
```json
[
  {
    "id": "...",
    "name": "servidores-web",
    "description": "Todos los servidores web",
    "hosts": [ { "id": "...", "name": "servidor-web-01", ... } ],
    "created_at": "2026-01-01T00:00:00Z",
    "updated_at": null
  }
]
```

### POST /inventories

> Requiere rol **operator** o **admin**.

```bash
curl -X POST http://localhost/api/inventories \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "servidores-web",
    "description": "Todos los servidores web",
    "host_ids": ["uuid-host-1", "uuid-host-2"]
  }'
```

### GET /inventories/{inventory_id}

```bash
curl http://localhost/api/inventories/550e8400-e29b-41d4-a716-446655440000 \
  -H "Authorization: Bearer $TOKEN"
```

### PATCH /inventories/{inventory_id}

> Requiere rol **operator** o **admin**.

```bash
curl -X PATCH http://localhost/api/inventories/550e8400-e29b-41d4-a716-446655440000 \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"host_ids": ["uuid-host-1", "uuid-host-2", "uuid-host-3"]}'
```

### DELETE /inventories/{inventory_id}

> Requiere rol **admin**.

```bash
curl -X DELETE http://localhost/api/inventories/550e8400-e29b-41d4-a716-446655440000 \
  -H "Authorization: Bearer $TOKEN"
```

---

## Credenciales

Los secretos nunca se devuelven en las respuestas; se cifran con Fernet en base de datos.

### GET /credentials

```bash
curl http://localhost/api/credentials \
  -H "Authorization: Bearer $TOKEN"
```

**Respuesta 200:**
```json
[
  {
    "id": "...",
    "name": "clave-ssh-produccion",
    "description": "Clave SSH para servidores de producción",
    "credential_type": "ssh_key",
    "username": "deploy",
    "created_at": "2026-01-01T00:00:00Z",
    "updated_at": null
  }
]
```

### POST /credentials

> Requiere rol **operator** o **admin**.

```bash
# SSH key
curl -X POST http://localhost/api/credentials \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "clave-ssh-produccion",
    "credential_type": "ssh_key",
    "username": "deploy",
    "secret": "-----BEGIN OPENSSH PRIVATE KEY-----\n...",
    "passphrase": "opcional"
  }'

# Password SSH
curl -X POST http://localhost/api/credentials \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "password-ssh",
    "credential_type": "ssh_password",
    "username": "admin",
    "secret": "tu_password"
  }'

# WinRM
curl -X POST http://localhost/api/credentials \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "winrm-windows",
    "credential_type": "winrm",
    "username": "Administrator",
    "secret": "tu_password_windows"
  }'
```

`credential_type`: `ssh_key` | `ssh_password` | `winrm`

### GET /credentials/{credential_id}

```bash
curl http://localhost/api/credentials/550e8400-e29b-41d4-a716-446655440000 \
  -H "Authorization: Bearer $TOKEN"
```

### PATCH /credentials/{credential_id}

> Requiere rol **operator** o **admin**.

### DELETE /credentials/{credential_id}

> Requiere rol **admin**.

---

## Jobs

### GET /jobs

Lista los jobs más recientes (orden: más nuevo primero).

```bash
# Últimos 20 jobs
curl "http://localhost/api/jobs?skip=0&limit=20" \
  -H "Authorization: Bearer $TOKEN"
```

**Respuesta 200:**
```json
[
  {
    "id": "...",
    "inventory_id": "...",
    "playbook_path": "/opt/playbooks/deploy.yml",
    "status": "success",
    "return_code": 0,
    "started_at": "2026-01-01T10:00:00Z",
    "finished_at": "2026-01-01T10:02:30Z",
    "created_at": "2026-01-01T10:00:00Z"
  }
]
```

`status`: `pending` | `running` | `success` | `failed`

### POST /jobs

> Requiere rol **operator** o **admin**. Lanza el playbook de forma asíncrona via Celery.

```bash
curl -X POST http://localhost/api/jobs \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "inventory_id": "550e8400-e29b-41d4-a716-446655440000",
    "playbook_path": "/opt/playbooks/deploy.yml"
  }'
```

**Respuesta 201:**
```json
{
  "id": "...",
  "status": "pending",
  ...
}
```

### GET /jobs/{job_id}

Devuelve el detalle del job incluyendo el stdout completo.

```bash
curl http://localhost/api/jobs/550e8400-e29b-41d4-a716-446655440000 \
  -H "Authorization: Bearer $TOKEN"
```

### DELETE /jobs/{job_id}

> Requiere rol **admin**.

### WebSocket: logs en tiempo real

```
ws://localhost/ws/jobs/{job_id}/logs?token=<access_token>
```

El servidor emite las líneas de stdout a medida que se producen. Mensajes de control:
- `__PING__` — keepalive cada 25 s (ignorar)
- `__END__` — job finalizado, cerrar la conexión

Si el job ya terminó al conectar, se reenvía el stdout almacenado seguido de `__END__`.

---

## Schedules

### GET /schedules

```bash
curl "http://localhost/api/schedules?skip=0&limit=20" \
  -H "Authorization: Bearer $TOKEN"
```

**Respuesta 200:**
```json
[
  {
    "id": "...",
    "name": "backup-diario",
    "cron_expression": "0 2 * * *",
    "inventory_id": "...",
    "playbook_path": "/opt/playbooks/backup.yml",
    "enabled": true,
    "created_at": "2026-01-01T00:00:00Z",
    "updated_at": null
  }
]
```

### POST /schedules

> Requiere rol **operator** o **admin**.

```bash
curl -X POST http://localhost/api/schedules \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "backup-diario",
    "cron_expression": "0 2 * * *",
    "inventory_id": "550e8400-e29b-41d4-a716-446655440000",
    "playbook_path": "/opt/playbooks/backup.yml",
    "enabled": true
  }'
```

`cron_expression`: 5 campos — `minuto hora día mes día_semana`.  
Ejemplos: `0 2 * * *` (cada día a las 02:00), `*/15 * * * *` (cada 15 min), `0 8 * * 1` (lunes a las 08:00).

### GET /schedules/{schedule_id}

```bash
curl http://localhost/api/schedules/550e8400-e29b-41d4-a716-446655440000 \
  -H "Authorization: Bearer $TOKEN"
```

### PATCH /schedules/{schedule_id}

> Requiere rol **operator** o **admin**. Actualiza solo los campos enviados.

```bash
# Deshabilitar un schedule
curl -X PATCH http://localhost/api/schedules/550e8400-e29b-41d4-a716-446655440000 \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"enabled": false}'
```

### DELETE /schedules/{schedule_id}

> Requiere rol **admin**. El schedule se elimina de Celery Beat automáticamente.

---

## Dashboard

### GET /dashboard

Devuelve un resumen de métricas del sistema.

```bash
curl http://localhost/api/dashboard \
  -H "Authorization: Bearer $TOKEN"
```

**Respuesta 200:**
```json
{
  "total_hosts": 12,
  "total_inventories": 4,
  "total_schedules": 3,
  "total_jobs": 247,
  "running_jobs": 1,
  "failed_last_24h": 2,
  "recent_jobs": [ ... ]
}
```

`recent_jobs` contiene los últimos 10 jobs ordenados por fecha de creación (más reciente primero).

---

## Códigos de error comunes

| Código | Significado |
|--------|-------------|
| `400` | Validación fallida (body malformado) |
| `401` | Token ausente, inválido o expirado |
| `403` | Rol insuficiente para esta operación |
| `404` | Recurso no encontrado |
| `409` | Conflicto — nombre duplicado |
| `422` | Error de validación Pydantic (campos incorrectos) |
| `429` | Too Many Requests — rate limit superado |
| `500` | Error interno del servidor |
