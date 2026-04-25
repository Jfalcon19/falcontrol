# TODO.md — Falcontrol

> Tareas activas. Marcar con `[x]` lo completado. Mover sprints cerrados al final.

## Sprint actual: **Sprint 1 — Auth + Usuarios**

Objetivo del sprint: modelo User con roles, endpoints JWT completos, frontend de login/registro con Pinia store e interceptor Axios.

### 1.1 Modelo y esquemas
- [ ] Modelo `User` (SQLAlchemy async): id (UUID), email, hashed_password, role (admin/operator/viewer), is_active, created_at.
- [ ] Schemas Pydantic: `UserCreate`, `UserRead`, `UserUpdate`, `Token`, `TokenPair`.

### 1.2 Servicio de auth
- [ ] `services/auth.py`: hash de password (bcrypt), verificación, creación de JWT access + refresh.
- [ ] `services/users.py`: CRUD de usuarios + comprobación de primer admin.

### 1.3 Endpoints
- [ ] `POST /api/auth/register` — solo admin puede crear usuarios.
- [ ] `POST /api/auth/login` — devuelve access + refresh tokens.
- [ ] `POST /api/auth/refresh` — renueva access token.
- [ ] `GET /api/auth/me` — devuelve usuario autenticado.
- [ ] Rate limiting en `/auth/login` (slowapi o similar).

### 1.4 Migración Alembic
- [ ] Migración inicial con tabla `users`.
- [ ] Verificar `alembic upgrade head` en BD limpia.

### 1.5 Tests de integración
- [ ] Test: registro + login + /me.
- [ ] Test: refresh de token.
- [ ] Test: acceso denegado sin token.
- [ ] Test: rate limiting (básico).

### 1.6 Frontend: auth
- [ ] Store Pinia `useAuthStore`: login, logout, refreshToken, usuario actual.
- [ ] Interceptor Axios: inyectar Bearer, manejar 401 con refresh automático.
- [ ] Vista `LoginView.vue`: formulario email/password, feedback de error.
- [ ] Guardia de ruta: redirigir a /login si no autenticado.

### 1.7 Cierre Sprint 1
- [ ] `npm run lint && npm run type-check` — sin errores.
- [ ] `ruff check . && mypy app/` — sin errores.
- [ ] `pytest` — todo verde, cobertura ≥ 70% en services/ y api/.
- [ ] Tag `v0.1.0-auth` en git.
- [ ] PR de `feat/sprint-1-auth` a `main`.
- [ ] Crear issues GitHub para Sprint 2.

---

## Próximos sprints (resumen)

### Sprint 2 — Hosts, Inventarios, Credenciales
- CRUD de hosts, inventarios (con relación M:N), credenciales.
- Cifrado Fernet de credenciales en BD.
- Frontend con tablas, filtros, formularios.

### Sprint 3 — Ejecución de Jobs
- Integración con `ansible-runner` envuelto en Celery.
- Endpoint para lanzar job, WebSocket para logs en vivo.
- Persistencia de output completo y artefactos.

### Sprint 4 — Scheduler + Dashboard
- Scheduler con expresiones cron usando Celery Beat.
- Dashboard con métricas, últimos jobs, hosts con fallos.

### Sprint 5 — Pulido + Release
- Documentación completa.
- Helm chart o instalador alternativo opcional.
- Tag `v0.1.0` y release en GitHub.

---

## Sprints cerrados

### Sprint 0 — Setup inicial ✓

#### 0.1 Repositorio y meta-archivos
- [x] Inicializar git en el directorio `~/falcontrol`.
- [x] Crear `.gitignore` (Python + Node + libvirt + IDEs).
- [x] Crear `LICENSE` (MIT, titular: Jfalcon19).
- [x] Crear `README.md` inicial con badges, descripción y link a CLAUDE.md.
- [x] Crear `.env.example` con todas las variables documentadas.
- [x] Hacer commit inicial: `chore: bootstrap Falcontrol repository`.
- [ ] Crear repo en GitHub con `gh repo create` — **pendiente: hacer `git push` al repo remoto**.

#### 0.2 Estructura de carpetas
- [x] Crear árbol completo de carpetas según sección 3 de CLAUDE.md.
- [x] Añadir `.gitkeep` en carpetas vacías relevantes.

#### 0.3 Backend mínimo
- [x] Configurar `backend/pyproject.toml` con `uv`.
- [x] `backend/Dockerfile` (multi-stage, basado en `python:3.12-slim`).
- [x] `app/main.py` con endpoint `/api/health` que responde `{"status": "ok"}`.
- [x] Configuración base con `pydantic-settings`.
- [x] `ruff` y `mypy` configurados.

#### 0.4 Frontend mínimo
- [x] Vue 3 con TypeScript + Pinia + Router + ESLint + Prettier + Vitest.
- [x] Tailwind CSS instalado y configurado.
- [x] Página de inicio que llama a `GET /api/health` y muestra el estado.
- [x] `frontend/Dockerfile` (multi-stage, basado en `node:22-alpine`).

#### 0.5 Docker Compose
- [x] `docker-compose.yml` con servicios: `db`, `redis`, `backend`, `celery-worker`, `frontend`, `nginx`.
- [x] `docker-compose.dev.yml` con override (volúmenes hot-reload, puertos expuestos).

#### 0.6 CI básico
- [x] `.github/workflows/ci.yml` con jobs: `backend-lint`, `backend-test`, `frontend-lint`, `frontend-test`.
- [ ] Verificar que el workflow corre verde en GitHub — **pendiente: requiere git push**.

#### 0.7 VMs de desarrollo
- [x] `vms/README.md` con instrucciones para el usuario.
- [x] `vms/cloud-init/user-data.yaml` (plantilla para Debian 13).
- [x] `vms/provision-controller.sh`: idempotente, comprueba existencia.
- [x] `vms/provision-linux-target.sh`: igual para `falcontrol-linux`.
- [x] Script `vms/check-windows.sh` que prueba `ansible win11 -m win_ping`.
- [x] `vms/inventory.ini` con las 3 VMs y variables de conexión.
- [ ] Ejecutar scripts y verificar VMs arrancadas — **pendiente: requiere descarga imagen Debian 13 y tu OK**.

#### 0.8 Cierre del Sprint 0
- [x] Actualizar `TODO.md` con estado actual.
- [ ] Tag `v0.0.1-setup` — **pendiente: hacer después del git push**.
- [ ] Crear issues en GitHub para cada feature del Sprint 1 — **pendiente: requiere repo remoto**.
