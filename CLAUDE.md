# CLAUDE.md — Falcontrol

> Archivo de instrucciones para Claude Code. Lee esto al inicio de cada sesión.

## 1. Contexto del proyecto

**Falcontrol** es un CMS de automatización de sistemas tipo Ansible Tower/AWX, diseñado para ser **sencillo, local y autoalojable**. Objetivo: ofrecer a instituciones y PYMES una herramienta para gestionar sus sistemas Linux y Windows mediante Ansible, sin la complejidad de AWX.

**Autor:** Falcón (usuario único propietario del repo).
**Licencia:** MIT (pendiente de añadir).
**Repositorio:** `github.com/Jfalcon19/falcontrol` (público).

### Propuesta de valor frente a AWX
- Instalación con un solo `docker compose up`
- Interfaz minimalista y responsive (Vue 3 + Tailwind)
- Bajo consumo de recursos
- Foco en casos de uso de PYMES: inventarios pequeños/medianos (< 500 hosts)

---

## 2. Stack tecnológico (decisión firme, no cambiar sin consultar)

### Backend
- **Python 3.12+**
- **FastAPI** como framework HTTP
- **ansible-runner** para ejecutar playbooks (NO llamar a `ansible-playbook` por subprocess)
- **SQLAlchemy 2.x** (modo async) + **Alembic** para migraciones
- **PostgreSQL 16** en producción, **SQLite** permitido para tests
- **Celery + Redis** para tareas async (ejecución de playbooks, scheduler)
- **Pydantic v2** para validación
- **python-jose** para JWT, **passlib[bcrypt]** para passwords
- **cryptography** (Fernet) para cifrar credenciales de hosts gestionados

### Frontend
- **Vue 3** con Composition API + `<script setup>`
- **TypeScript** obligatorio (no JS puro)
- **Vite** como bundler
- **Pinia** para estado
- **Vue Router 4**
- **Tailwind CSS** para estilos (NO frameworks de componentes pesados tipo Vuetify)
- **Headless UI** + **Heroicons** para componentes accesibles
- **Axios** con interceptores para auth
- WebSockets nativos para logs en vivo

### Infraestructura
- **Docker + Docker Compose** para dev y producción
- **Nginx** como reverse proxy (sirve frontend + proxy a API + WS)
- Imágenes basadas en `python:3.12-slim` y `node:22-alpine`

---

## 3. Estructura del repositorio

```
falcontrol/
├── CLAUDE.md                       # este archivo
├── TODO.md                         # tareas del sprint actual
├── README.md                       # orientado a usuarios finales
├── LICENSE                         # MIT
├── .gitignore
├── .env.example                    # variables de entorno documentadas
├── .claude/
│   └── settings.json               # permisos de Claude Code para este proyecto
├── docker-compose.yml              # stack de producción
├── docker-compose.dev.yml          # override con hot-reload
├── backend/
│   ├── pyproject.toml              # usar uv o poetry
│   ├── Dockerfile
│   ├── alembic.ini
│   ├── alembic/
│   ├── app/
│   │   ├── main.py                 # entrada FastAPI
│   │   ├── core/                   # config, security, db
│   │   ├── models/                 # SQLAlchemy
│   │   ├── schemas/                # Pydantic
│   │   ├── api/                    # routers por recurso
│   │   │   ├── auth.py
│   │   │   ├── hosts.py
│   │   │   ├── inventories.py
│   │   │   ├── credentials.py
│   │   │   ├── projects.py         # repos de playbooks (git)
│   │   │   ├── jobs.py             # ejecuciones
│   │   │   ├── schedules.py
│   │   │   └── users.py
│   │   ├── services/               # lógica de negocio
│   │   │   ├── ansible_runner.py   # wrapper de ansible-runner
│   │   │   ├── vault.py            # cifrado Fernet
│   │   │   └── scheduler.py
│   │   ├── tasks/                  # tareas Celery
│   │   └── websockets/             # logs en vivo
│   └── tests/
├── frontend/
│   ├── package.json
│   ├── Dockerfile
│   ├── vite.config.ts
│   ├── tsconfig.json
│   ├── tailwind.config.ts
│   ├── src/
│   │   ├── main.ts
│   │   ├── App.vue
│   │   ├── router/
│   │   ├── stores/                 # Pinia
│   │   ├── api/                    # cliente axios tipado
│   │   ├── components/             # reutilizables
│   │   ├── views/                  # páginas
│   │   └── types/                  # interfaces TS
│   └── tests/
├── deploy/
│   ├── nginx/
│   └── postgres/
├── docs/
│   ├── architecture.md
│   ├── api.md
│   └── user-guide.md
├── playbooks-examples/             # playbooks de demostración
└── vms/                            # scripts para aprovisionar VMs de desarrollo
    ├── provision-controller.sh
    ├── provision-linux-target.sh
    ├── cloud-init/
    └── README.md
```

---

## 4. Alcance funcional — MVP (prioridad alta → baja)

1. **Autenticación y usuarios** con roles: `admin`, `operator`, `viewer`.
2. **Gestión de hosts**: CRUD, agrupación en inventarios, tags.
3. **Credenciales cifradas**: SSH key, password, WinRM (usuario/pass).
4. **Proyectos**: clonar/sincronizar repos git con playbooks.
5. **Ejecución de jobs**: lanzar playbook contra inventario, ver estado, logs.
6. **Logs en tiempo real** vía WebSocket durante la ejecución.
7. **Historial de jobs** con stdout completo, código de retorno, duración.
8. **Scheduler**: ejecuciones programadas tipo cron.
9. **Dashboard**: estado global, últimos jobs, hosts con fallos.

**Fuera del MVP** (para iteraciones posteriores): surveys/encuestas, workflows multi-step, notificaciones, LDAP/OAuth, multi-tenant.

---

## 5. Principios de diseño y reglas duras

### Seguridad (inquebrantable)
- **NUNCA** loguear secretos, passwords, tokens o contenido de credenciales.
- Credenciales siempre cifradas en BD con Fernet; la clave maestra vive solo en `FALCONTROL_SECRET_KEY` (env var).
- JWT con expiración corta (15 min access + 7 días refresh).
- Rate limiting en endpoints de auth.
- CORS restrictivo en producción.
- Dependencias auditadas: `pip-audit` y `npm audit` deben pasar antes de merge.

### Código
- **Backend**: `ruff` (lint + format) + `mypy --strict` en `app/`. No se mergea código con errores.
- **Frontend**: `eslint` + `prettier` + `vue-tsc` sin errores.
- Type hints obligatorios en Python (funciones públicas).
- Docstrings estilo Google en clases y funciones no triviales.
- Commits siguiendo **Conventional Commits** (`feat:`, `fix:`, `docs:`, `chore:`, `refactor:`, `test:`).
- Ramas: `main` protegida, trabajo en `feat/<slug>`, `fix/<slug>`.

### Testing
- Cobertura mínima del backend: **70%** en `services/` y `api/`.
- Todo endpoint nuevo requiere al menos un test de integración.
- Tests de Ansible: usar las VMs reales (ver sección 7), no mockear `ansible-runner` excepto en tests unitarios.

### Arquitectura
- Capas estrictas: `api → services → models`. Un router NUNCA accede directo a `session.execute`, siempre pasa por un service.
- Schemas Pydantic separados para entrada y salida (`HostCreate`, `HostRead`, `HostUpdate`).
- No meter lógica de negocio en el frontend.

---

## 6. Entorno de desarrollo local del autor

**Hardware del anfitrión:**
- Ryzen 5 5600X (6c/12t) • 32 GB RAM • SSD 500 GB
- Debian 13 • QEMU/KVM + libvirt instalados • Virtualización habilitada en BIOS
- GPU AMD sin drivers propietarios (irrelevante para el proyecto)

**Herramientas instaladas del lado del usuario:**
- `gh` CLI autenticado como `Jfalcon19` (protocolo SSH)
- Clave SSH `~/.ssh/id_ed25519` registrada en GitHub

**Comandos de verificación del entorno (ejecutar si hay dudas):**
```bash
egrep -c '(vmx|svm)' /proc/cpuinfo   # > 0
lsmod | grep kvm                      # debe listar kvm_amd
sudo kvm-ok                           # "KVM acceleration can be used"
virsh list --all                      # sin sudo, tras añadir al grupo libvirt
gh auth status                        # debe mostrar Jfalcon19 logueado
```

---

## 7. Máquinas virtuales del entorno de pruebas

Falcontrol se prueba contra **3 VMs reales** gestionadas con libvirt:

| VM | Rol | SO | RAM | Disco | Red |
|----|-----|-----|-----|-------|-----|
| `falcontrol-controller` | Donde corre el stack | Debian 13 minimal | 4 GB | 30 GB | `default` (NAT) |
| `falcontrol-linux` | Target Linux gestionado | Debian 13 minimal | 2 GB | 15 GB | `default` (NAT) |
| `win11` | Target Windows (ya existe) | TinyWin11 + WinRM | 6 GB | — | `default` (NAT) |

### Aprovisionamiento (Claude Code debe crear scripts idempotentes en `vms/`)

- Usar `virt-install` con `cloud-init` para las dos VMs Debian.
- Nunca sobreescribir una VM existente sin confirmación explícita del usuario.
- Scripts deben comprobar con `virsh dominfo <vm>` antes de crear.
- Generar par de claves SSH dedicado `~/.ssh/falcontrol_ed25519` y propagarlo vía cloud-init.
- Publicar IPs de las VMs en `vms/inventory.ini` para uso en desarrollo.

### Sobre la VM Windows
- El usuario ya tiene `win11` con TinyWin y WinRM (presumiblemente) activado.
- **Antes de usarla**, Claude Code debe verificar conectividad:
  ```bash
  ansible -i vms/inventory.ini win11 -m win_ping
  ```
- Si falla, documentar en `vms/README.md` los pasos para habilitar WinRM con HTTP básico o NTLM (no pedir al usuario ejecutar nada sin antes mostrarle los comandos).

---

## 8. Modos de permisos de Claude Code en este proyecto

El proyecto incluye `.claude/settings.json` con una lista de comandos **auto-permitidos** (lectura, linters, tests, git no destructivo) y otra de comandos que **siempre piden confirmación** o están **denegados** (operaciones destructivas sobre VMs, `git push --force`, `rm -rf /`, etc.).

### Recomendación al usuario sobre qué modo usar

| Situación | Modo | Cómo activarlo |
|-----------|------|----------------|
| Trabajo normal de código | **Accept Edits** | `Shift+Tab` una vez dentro de Claude Code |
| Sprint grande o tarea compleja | **Plan Mode** primero, luego Accept Edits | `Shift+Tab` dos veces |
| Operaciones sobre VMs (`virt-install`, `virsh destroy`) | **Default** (confirmación manual) | Modo inicial |
| Migraciones de BD o `git push` | **Default** (confirmación manual) | Modo inicial |
| Entorno totalmente desechable (no aplica aquí) | Bypass | `claude --dangerously-skip-permissions` — **NO usar en esta máquina** |

### Reglas para Claude Code sobre permisos
- Respetar siempre la lista `deny` de `.claude/settings.json`, aunque el usuario diga "hazlo".
- Si una acción está en la zona ambigua (no en `allow` ni `deny`), preguntar antes.
- Si el usuario está en bypass y una acción es destructiva e irreversible, Claude Code debe **pausar y confirmar verbalmente** aunque técnicamente tenga permiso.

---

## 9. Flujo de trabajo con Claude Code

### Al iniciar una sesión
1. Leer este `CLAUDE.md` completo.
2. Leer `TODO.md` para saber el estado del sprint.
3. Revisar `git status` y la rama actual.
4. **Preguntar al usuario qué objetivo tiene esta sesión** antes de tocar código.

### Antes de escribir código
- Si la tarea implica un cambio arquitectónico, proponer primero un plan y esperar aprobación.
- Si la tarea afecta a más de 5 archivos, dividirla en commits atómicos.
- Si se instala una dependencia nueva, justificarla en el mensaje de commit.

### Antes de `git push`
1. `ruff check .` y `ruff format --check .` — sin errores.
2. `mypy app/` — sin errores.
3. `pytest` — todo verde.
4. En frontend: `npm run lint && npm run type-check && npm run test`.
5. Si se añade migración: verificar `alembic upgrade head` en BD limpia.
6. Actualizar `TODO.md` marcando lo completado.

### GitHub
- Repositorio público: `github.com/Jfalcon19/falcontrol`.
- Usar `gh` CLI (ya autenticado como Jfalcon19 con SSH). No pedir tokens al usuario.
- Añadir `.github/workflows/ci.yml` con lint + tests en el segundo commit.
- Issues para cada feature del MVP antes de empezar a desarrollarla.
- Tras el commit inicial a `main`, todo cambio va por PR (aunque sea dev único).

---

## 10. Comunicación con el usuario

- **Idioma**: español en commits, issues, documentación de usuario y conversación. **Inglés** en código, comentarios técnicos, nombres de variables, y logs.
- Cuando haya varias alternativas válidas, presentar pros/contras en lugar de decidir en silencio.
- Ante errores del usuario (ej. comando mal tecleado), sugerir la corrección sin condescendencia.
- El usuario prefiere **comandos ejecutables completos** antes que explicaciones largas de teoría.

---

## 11. Cosas que Claude Code NUNCA debe hacer

- Subir secretos al repositorio (revisar cada commit con `git diff`).
- Ejecutar `virsh destroy` o `virsh undefine` sin confirmación explícita.
- Ejecutar playbooks de Ansible contra hosts fuera de las 3 VMs de desarrollo sin confirmación.
- Hacer `git push --force` a `main`.
- Instalar dependencias globales del sistema (`sudo pip install`, `sudo npm install -g`).
- Modificar la configuración de libvirt/QEMU del anfitrión sin explicarlo primero.
- Usar `ansible-playbook` por subprocess; usar siempre `ansible-runner` como librería.
- Asumir credenciales por defecto; siempre preguntar o leer de variables de entorno.

---

## 12. Roadmap inicial sugerido (primeros sprints)

1. **Sprint 0 — Setup** (1-2 sesiones)
   - Estructura de carpetas, `docker-compose.dev.yml`, CI básico, scripts de VMs.
2. **Sprint 1 — Auth + Usuarios**
   - Modelos, endpoints, JWT, frontend de login.
3. **Sprint 2 — Hosts, inventarios, credenciales**
   - CRUD completo + cifrado Fernet.
4. **Sprint 3 — Ejecución de playbooks**
   - Integración `ansible-runner`, Celery, WebSocket de logs.
5. **Sprint 4 — Scheduler + Dashboard**
6. **Sprint 5 — Pulido, docs, release v0.1.0**

---

## 13. Referencias útiles

- FastAPI: https://fastapi.tiangolo.com/
- ansible-runner: https://ansible.readthedocs.io/projects/runner/
- Ansible Windows: https://docs.ansible.com/ansible/latest/os_guide/windows_winrm.html
- Vue 3: https://vuejs.org/guide/
- AWX (referencia de UX, no de código): https://github.com/ansible/awx
