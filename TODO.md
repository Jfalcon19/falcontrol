# TODO.md — Falcontrol

> Tareas activas. Marcar con `[x]` lo completado. Mover sprints cerrados al final.

## Sprint actual: **Sprint 3 — Ejecución de Jobs**

Objetivo del sprint: integrar `ansible-runner` con Celery para lanzar playbooks, WebSocket de logs en vivo y persistencia del historial de ejecuciones.

### 3.1 Modelo y migración
- [ ] Modelo `Job`: id, inventory_id, playbook_path, status (pending/running/success/failed), stdout, return_code, started_at, finished_at.
- [ ] Migración Alembic `0005_create_jobs`.

### 3.2 Tarea Celery
- [ ] `tasks/run_playbook.py`: envuelve `ansible-runner.run_async`, actualiza estado del job en BD.
- [ ] Configurar Celery con Redis broker (ya disponible en `docker-compose.yml`).

### 3.3 Endpoints
- [ ] `POST /api/jobs` — lanza job (operator+).
- [ ] `GET /api/jobs` — lista jobs con paginación.
- [ ] `GET /api/jobs/{id}` — detalle con stdout completo.
- [ ] `DELETE /api/jobs/{id}` — solo admin.

### 3.4 WebSocket de logs
- [ ] `websockets/job_logs.py`: emite líneas de stdout en tiempo real mientras el job corre.
- [ ] Endpoint `WS /api/jobs/{id}/logs`.

### 3.5 Tests
- [ ] Tests de integración para endpoints de jobs (mocking de ansible-runner en unit tests).
- [ ] Test de WebSocket básico.

### 3.6 Frontend
- [ ] `JobsView.vue`: lista de jobs con estado, botón lanzar, link a detalle.
- [ ] `JobDetailView.vue`: terminal con stdout en vivo vía WebSocket.

### 3.7 Cierre Sprint 3
- [ ] `ruff check . && mypy app/ && pytest` — todo verde.
- [ ] `npm run lint && npm run type-check && npm run test` — todo verde.
- [ ] Verificar `alembic upgrade head` con migración 0005 en PostgreSQL.
- [ ] PR a `main` y tag `v0.3.0-jobs`.

---

## Próximos sprints (resumen)

### Sprint 4 — Scheduler + Dashboard
- Scheduler con expresiones cron usando Celery Beat.
- Dashboard con métricas, últimos jobs, hosts con fallos.

### Sprint 5 — Pulido + Release
- Documentación completa.
- Helm chart o instalador alternativo opcional.
- Tag `v1.0.0` y release en GitHub.

---

## Sprints cerrados

### Sprint 2 — Hosts, Inventarios, Credenciales ✓

#### 2.1 Backend: CRUD de hosts (issue #3 — PR #10)
- [x] Modelo `Host`: id, name, address, description, os_type, connection_type, port, tags (JSON), is_active, timestamps.
- [x] Schemas Pydantic: `HostCreate`, `HostRead`, `HostUpdate`.
- [x] Servicio `services/hosts.py`: CRUD completo con PATCH semántico (`exclude_unset=True`).
- [x] Router `api/hosts.py`: GET list, GET by id, POST, PATCH, DELETE con control de roles.
- [x] Migración Alembic `0002_create_hosts`.
- [x] 23 tests de integración — cobertura ≥ 70%.

#### 2.2 Backend: CRUD de inventarios M:N (issue #4 — PR #11)
- [x] Modelo `Inventory` con relación M:N a `Host` vía tabla `inventory_hosts`.
- [x] Schemas: `InventoryCreate`, `InventoryRead`, `InventoryUpdate` con `host_ids`.
- [x] Servicio `services/inventories.py`: resolución de hosts por IDs en cada operación.
- [x] Router `api/inventories.py`: CRUD completo con permisos por rol.
- [x] Migración Alembic `0003_create_inventories`.
- [x] 22 tests de integración.

#### 2.3 Backend: credenciales cifradas con Fernet (issue #5 — PR #12)
- [x] Modelo `Credential`: encrypted_secret y encrypted_passphrase nunca expuestos en API.
- [x] `services/vault.py`: cifrado simétrico Fernet derivado de `FALCONTROL_SECRET_KEY`.
- [x] Schemas: `CredentialCreate` (con validador username requerido para ssh_password/winrm), `CredentialRead` (sin secretos), `CredentialUpdate`.
- [x] Migración Alembic `0004_create_credentials`.
- [x] 26 tests de integración incluyendo verificación directa de cifrado en BD.

#### 2.4 Frontend: hosts e inventarios (issue #6 — PR #13)
- [x] Tipos TS `Host`, `Inventory` y variantes Create/Update.
- [x] Clientes Axios `api/hosts.ts` y `api/inventories.ts`.
- [x] Stores Pinia `useHostsStore` y `useInventoriesStore`.
- [x] `AppLayout.vue` con sidebar de navegación; router anidado bajo layout.
- [x] Componentes: `OsTypeBadge`, `ConnectionTypeBadge`, `TagChips`, `ConfirmModal`.
- [x] `HostsView.vue`: tabla con CRUD completo y permisos por rol.
- [x] `InventoriesView.vue`: cards con modal y multiselect de hosts.

#### 2.5 Frontend: credenciales (issue #7 — PR #14)
- [x] Tipos TS `Credential`, `CredentialType` y variantes Create/Update.
- [x] Cliente Axios `api/credentials.ts` y store `useCredentialsStore`.
- [x] `CredentialTypeBadge.vue`: badge coloreado por tipo.
- [x] `CredentialsView.vue`: tabla sin exponer secretos, modal con campos condicionales por tipo.

#### 2.6 Cierre Sprint 2 (issue #8)
- [x] `alembic upgrade head` + `alembic downgrade base` verificados en PostgreSQL 16 limpio.
- [x] `ruff check . && mypy app/ && pytest` — todo verde (71 tests).
- [x] `npm run lint && npm run type-check && npm run test` — todo verde.
- [x] PR a `main` y tag `v0.2.0-sprint2`.

---

### Sprint 1 — Auth + Usuarios ✓

#### 1.1 Modelo y esquemas
- [x] Modelo `User` (SQLAlchemy async): id (UUID), email, hashed_password, role (admin/operator/viewer), is_active, created_at.
- [x] Schemas Pydantic: `UserCreate`, `UserRead`, `UserUpdate`, `Token`, `TokenPair`.

#### 1.2 Servicio de auth
- [x] `services/auth.py`: hash de password (bcrypt), verificación, creación de JWT access + refresh.
- [x] `services/users.py`: CRUD de usuarios + comprobación de primer admin.

#### 1.3 Endpoints
- [x] `POST /api/auth/login` — devuelve access + refresh tokens.
- [x] `POST /api/auth/refresh` — renueva access token.
- [x] `GET /api/auth/me` — devuelve usuario autenticado.
- [x] `POST /api/users` — creación de usuarios (solo admin).

#### 1.4 Migración Alembic
- [x] Migración `0001_create_users` con tabla `users`.

#### 1.5 Tests de integración
- [x] Test: registro + login + /me.
- [x] Test: refresh de token.
- [x] Test: acceso denegado sin token.

#### 1.6 Frontend: auth
- [x] Store Pinia `useAuthStore`: login, logout, fetchMe; persiste tokens en localStorage.
- [x] Interceptor Axios: inyecta Bearer, reintenta tras refresh, emite fc:logout si falla.
- [x] Vista `LoginView.vue`: formulario email/password, feedback de error en español.
- [x] Guardia de ruta: redirige a /login si no autenticado.

#### 1.7 Cierre Sprint 1
- [x] PR #2 a `main`, tag `v0.1.0-auth`.

---

### Sprint 0 — Setup inicial ✓

#### 0.1–0.7 Infraestructura base
- [x] Repositorio git, `.gitignore`, `LICENSE` MIT, `README.md`, `.env.example`.
- [x] Árbol de carpetas completo según CLAUDE.md sección 3.
- [x] Backend: `pyproject.toml` con uv, Dockerfile, `/api/health`, ruff + mypy.
- [x] Frontend: Vue 3 + TS + Pinia + Router + Tailwind + Vitest + Dockerfile.
- [x] `docker-compose.yml` (producción) y `docker-compose.dev.yml` (dev con hot-reload).
- [x] CI: `.github/workflows/ci.yml` con lint + tests para backend y frontend.
- [x] Scripts de VMs: `vms/provision-*.sh`, `vms/cloud-init/`, `vms/inventory.ini`.
