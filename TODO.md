# TODO.md — Falcontrol

> Tareas activas. Marcar con `[x]` lo completado. Mover sprints cerrados al final.

## Sprint actual: **Sprint 5 — Pulido + Release**

Objetivo del sprint: documentación, ajustes UX, tag `v1.0.0` y release en GitHub.

### 5.1 Documentación
- [ ] `docs/api.md`: documentar todos los endpoints con ejemplos curl.
- [ ] `docs/user-guide.md`: guía de uso para administradores.
- [ ] `README.md`: sección de instalación rápida con `docker compose up`.

### 5.2 Pulido UX
- [ ] Paginación en JobsView y SchedulesView.
- [ ] Indicador de recarga automática en DashboardView (cada 30 s).
- [ ] Mensajes de error más descriptivos en el frontend.

### 5.3 Seguridad y calidad
- [ ] `pip-audit` y `npm audit` sin vulnerabilidades críticas.
- [ ] Rate limiting en endpoints de auth.
- [ ] `alembic upgrade head` verificado en PostgreSQL 16 limpio desde cero.

### 5.4 Cierre Sprint 5
- [ ] PR a `main` y tag `v1.0.0`.
- [ ] Release en GitHub con changelog.

---

## Sprints cerrados

### Sprint 4 — Scheduler + Dashboard ✓ (tag v0.4.0-scheduler)

#### 4.1 Scheduler (issues #20, #21 — PRs #24, #25)
- [x] Modelo `Schedule`: cron expression, inventory_id, playbook_path, enabled.
- [x] Migración Alembic `0006_create_schedules`.
- [x] Endpoints CRUD `POST/GET/PATCH/DELETE /api/schedules` (operator+), 17 tests de integración.
- [x] Integración con Celery Beat (RedBeat) — `register_schedule`, `unregister_schedule`, `sync_all_schedules` en `beat_init`.
- [x] Tarea `run_scheduled_job(schedule_id)`: crea Job + llama `run_playbook` inline.
- [x] 9 tests unitarios del scheduler con mocks de RedBeat.

#### 4.2 Dashboard (issues #22, #23 — PRs #26, #27)
- [x] Endpoint `GET /api/dashboard`: 7 queries async (totales, running, failed 24h, recent_jobs), 4 tests de integración.
- [x] `SchedulesView.vue`: tabla con toggle enabled/disabled, formulario de creación, eliminación con confirmación.
- [x] `DashboardView.vue`: 6 tarjetas de métricas + tabla de últimos 10 jobs enlazados al detalle.
- [x] Tipos TS `Schedule`, `DashboardStats`; stores Pinia `useSchedulesStore`, `useDashboardStore`.

#### 4.3 Cierre Sprint 4 (issue #24)
- [x] `ruff check . && mypy app/ && pytest` — 134 tests, 78% cobertura.
- [x] `npm run lint && npm run type-check && npm run test` — todo verde.
- [x] TODO.md actualizado y tag `v0.4.0-scheduler`.

---

### Sprint 3 — Ejecución de Jobs ✓ (tag v0.3.0-jobs)

#### 3.1 Modelo y migración (issue #16 — PR #20)
- [x] Modelo `Job`: id, inventory_id, playbook_path, status, stdout, return_code, started_at, finished_at.
- [x] Schemas Pydantic: `JobCreate`, `JobRead` (sin stdout), `JobReadDetail` (con stdout).
- [x] Servicio `services/jobs.py`: CRUD + `mark_running` / `mark_finished`.
- [x] Router `api/jobs.py`: GET list, GET detail, POST (operator+), DELETE (admin).
- [x] Migración Alembic `0005_create_jobs` con enum `jobstatus`.

#### 3.2 Tarea Celery + WebSocket (issue #17 — PR #21)
- [x] `services/inventory_writer.py`: genera `inventory.ini` desde ORM (SSH/WinRM).
- [x] `tasks/jobs.py`: tarea `run_playbook` con `ansible-runner`, pub/sub Redis línea a línea.
- [x] `websockets/job_logs.py`: WS `/ws/jobs/{id}/logs` con auth JWT por query param, keepalive `__PING__` cada 25 s, reenvío de stdout almacenado si job ya terminó.
- [x] 5 tests unitarios con mocks completos (sin red, Redis ni Ansible real).

#### 3.3 Frontend (issue #18 — PR #22)
- [x] Tipos TS `Job`, `JobDetail`, `JobCreate`, `JobStatus`.
- [x] Cliente Axios `api/jobs.ts` y store Pinia `useJobsStore`.
- [x] `JobStatusBadge.vue`: badge con `animate-pulse` para estado running.
- [x] `JobsView.vue`: tabla con duración calculada, formulario de lanzamiento, eliminación con confirmación.
- [x] `JobDetailView.vue`: terminal con logs en vivo vía WebSocket nativo; maneja `__END__`, `__PING__`, jobs ya finalizados.

#### 3.4 Cierre Sprint 3 (issue #19 — PR #23)
- [x] `ruff check . && mypy app/ && pytest` — todo verde.
- [x] `npm run lint && npm run type-check && npm run test` — todo verde.
- [x] TODO.md actualizado y tag `v0.3.0-jobs`.

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
