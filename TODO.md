# TODO.md — Falcontrol

> Tareas activas. Marcar con `[x]` lo completado. Mover sprints cerrados al final.

## Sprint actual: **Sprint 0 — Setup inicial**

Objetivo del sprint: tener el repositorio creado en GitHub, la estructura de carpetas, el entorno de docker-compose corriendo en local con un "hello world" del backend y frontend, y las dos VMs Debian aprovisionadas y accesibles vía SSH.

### 0.1 Repositorio y meta-archivos
- [ ] Inicializar git en el directorio `~/falcontrol`.
- [ ] Crear `.gitignore` (Python + Node + libvirt + IDEs).
- [ ] Crear `LICENSE` (MIT, titular: Jfalcon19).
- [ ] Crear `README.md` inicial con badges, descripción y link a CLAUDE.md.
- [ ] Crear `.env.example` con todas las variables documentadas.
- [ ] Hacer commit inicial: `chore: bootstrap Falcontrol repository`.
- [ ] Crear repo en GitHub con `gh repo create Jfalcon19/falcontrol --public --source=. --remote=origin --push`.

### 0.2 Estructura de carpetas
- [ ] Crear árbol completo de carpetas según sección 3 de CLAUDE.md.
- [ ] Añadir `.gitkeep` en carpetas vacías relevantes.

### 0.3 Backend mínimo
- [ ] Configurar `backend/pyproject.toml` con `uv` o `poetry`.
- [ ] `backend/Dockerfile` (multi-stage, basado en `python:3.12-slim`).
- [ ] `app/main.py` con un endpoint `/health` que responda `{"status": "ok"}`.
- [ ] Configuración base con `pydantic-settings`.
- [ ] `ruff` y `mypy` configurados; `ruff check .` debe pasar.

### 0.4 Frontend mínimo
- [ ] `npm create vue@latest` con TypeScript + Pinia + Router + ESLint + Prettier + Vitest.
- [ ] Instalar Tailwind y Headless UI.
- [ ] Página de inicio que llame a `GET /api/health` y muestre el estado.
- [ ] `frontend/Dockerfile` (multi-stage, basado en `node:22-alpine`).

### 0.5 Docker Compose
- [ ] `docker-compose.yml` con servicios: `db` (postgres:16), `redis`, `backend`, `frontend`, `nginx`.
- [ ] `docker-compose.dev.yml` con override (volúmenes para hot-reload, puertos expuestos).
- [ ] Verificar que `docker compose -f docker-compose.yml -f docker-compose.dev.yml up` levanta todo y responde el `/health` a través de Nginx.

### 0.6 CI básico
- [ ] `.github/workflows/ci.yml` con jobs: `backend-lint`, `backend-test`, `frontend-lint`, `frontend-test`.
- [ ] Verificar que el workflow corre verde en GitHub.

### 0.7 VMs de desarrollo
- [ ] `vms/README.md` con instrucciones para el usuario.
- [ ] `vms/cloud-init/user-data.yaml` (plantilla para Debian 13).
- [ ] `vms/provision-controller.sh`: idempotente, comprueba existencia, descarga imagen Debian 13 cloud, crea VM con `virt-install`.
- [ ] `vms/provision-linux-target.sh`: igual para `falcontrol-linux`.
- [ ] Generar `~/.ssh/falcontrol_ed25519` si no existe; inyectarla vía cloud-init.
- [ ] Script `vms/check-windows.sh` que pruebe `ansible win11 -m win_ping` y reporte.
- [ ] `vms/inventory.ini` con las 3 VMs y variables de conexión.

### 0.8 Cierre del Sprint 0
- [ ] Tag `v0.0.1-setup` en git.
- [ ] Actualizar `README.md` con estado actual.
- [ ] Crear issues en GitHub para cada feature del Sprint 1.

---

## Próximos sprints (resumen)

### Sprint 1 — Auth + Usuarios
- Modelo `User` con roles (admin/operator/viewer).
- Endpoints `/auth/register`, `/auth/login`, `/auth/refresh`, `/auth/me`.
- JWT con access + refresh tokens.
- Hashing con bcrypt.
- Frontend: pantallas de login y registro, store Pinia para auth, interceptor Axios.
- Tests de integración para todos los endpoints de auth.

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

_(vacío)_
