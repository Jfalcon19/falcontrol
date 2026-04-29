# Falcontrol

> CMS de automatización de sistemas — alternativa ligera a Ansible Tower/AWX para PYMES e instituciones.

[![CI](https://github.com/Jfalcon19/falcontrol/actions/workflows/ci.yml/badge.svg)](https://github.com/Jfalcon19/falcontrol/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Version](https://img.shields.io/badge/version-0.4.0-blue.svg)](https://github.com/Jfalcon19/falcontrol/releases)

## ¿Qué es Falcontrol?

Falcontrol te permite gestionar tus sistemas Linux y Windows con Ansible desde una interfaz web minimalista, sin la complejidad de AWX. Un solo comando para arrancarlo todo:

```bash
docker compose up -d
```

## Funcionalidades

- **Gestión de hosts**: CRUD de hosts Linux/Windows con SSH y WinRM
- **Inventarios**: agrupación de hosts en inventarios reutilizables
- **Credenciales cifradas**: SSH key, password y WinRM almacenadas con Fernet
- **Ejecución de jobs**: lanzar playbooks Ansible contra inventarios con logs en tiempo real
- **Scheduler**: programar ejecuciones periódicas con expresiones cron
- **Dashboard**: métricas globales y últimos jobs de un vistazo
- **Roles de usuario**: admin, operator y viewer

## Stack

| Capa | Tecnología |
|------|------------|
| Backend | FastAPI + SQLAlchemy async + PostgreSQL 16 |
| Tareas async | Celery + Redis |
| Scheduler | Celery Beat + RedBeat |
| Frontend | Vue 3 + TypeScript + Tailwind CSS |
| Ejecución Ansible | ansible-runner |
| Infraestructura | Docker Compose + Nginx |

## Inicio rápido

### Requisitos previos

- Docker Engine 24+ y Docker Compose v2
- Ansible instalado en el host (o incluido en la imagen del backend)

### Instalación

```bash
# 1. Clonar el repositorio
git clone git@github.com:Jfalcon19/falcontrol.git
cd falcontrol

# 2. Copiar y editar variables de entorno
cp .env.example .env
$EDITOR .env
```

**Variables obligatorias en `.env`:**

| Variable | Descripción |
|----------|-------------|
| `FALCONTROL_SECRET_KEY` | Clave Fernet base64 — genera con el comando de abajo |
| `POSTGRES_PASSWORD` | Password de PostgreSQL |
| `FIRST_ADMIN_EMAIL` | Email del primer administrador |
| `FIRST_ADMIN_PASSWORD` | Password del primer admin (mín. 8 caracteres) |

```bash
# Generar FALCONTROL_SECRET_KEY
python3 -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"

# 3. Levantar el stack completo
docker compose up -d

# 4. Abrir en el navegador
open http://localhost
```

El primer arranque crea automáticamente el usuario administrador definido en `.env`.

## Desarrollo local

```bash
docker compose -f docker-compose.yml -f docker-compose.dev.yml up -d
```

El modo dev activa hot-reload en backend y frontend y expone los puertos directamente al host:

| Servicio | URL |
|----------|-----|
| Frontend | `http://localhost:5173` |
| Backend / Swagger | `http://localhost:8000/api/docs` |

### Ejecutar tests

```bash
# Backend
cd backend && uv run pytest

# Frontend
cd frontend && npm run test
```

## Documentación

- [API Reference](docs/api.md) — todos los endpoints con ejemplos curl
- [Guía de usuario](docs/user-guide.md) — guía para administradores
- [Arquitectura](docs/architecture.md)
- [Para colaboradores / Claude Code](CLAUDE.md)

## Estado del proyecto

**v0.4.0** — Sprint 4 completado. Funcionalidades implementadas: auth, hosts, inventarios, credenciales, jobs con logs WebSocket, scheduler con Celery Beat y dashboard de métricas.

## Licencia

MIT © 2026 [Jfalcon19](https://github.com/Jfalcon19)
