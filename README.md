# Falcontrol

> CMS de automatización de sistemas — alternativa ligera a Ansible Tower/AWX para PYMES e instituciones.

[![CI](https://github.com/Jfalcon19/falcontrol/actions/workflows/ci.yml/badge.svg)](https://github.com/Jfalcon19/falcontrol/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

## ¿Qué es Falcontrol?

Falcontrol te permite gestionar tus sistemas Linux y Windows con Ansible desde una interfaz web minimalista, sin la complejidad de AWX. Un solo comando para arrancarlo todo:

```bash
docker compose up -d
```

## Stack

| Capa | Tecnología |
|------|------------|
| Backend | FastAPI + SQLAlchemy async + PostgreSQL 16 |
| Tareas async | Celery + Redis |
| Frontend | Vue 3 + TypeScript + Tailwind CSS |
| Ejecución Ansible | ansible-runner |
| Infraestructura | Docker Compose + Nginx |

## Inicio rápido

```bash
# 1. Clonar el repositorio
git clone git@github.com:Jfalcon19/falcontrol.git
cd falcontrol

# 2. Copiar y editar variables de entorno
cp .env.example .env
# Edita .env con tus valores (mínimo: FALCONTROL_SECRET_KEY, POSTGRES_PASSWORD)

# 3. Levantar el stack completo
docker compose up -d

# 4. Abrir en el navegador
open http://localhost
```

## Desarrollo local

```bash
docker compose -f docker-compose.yml -f docker-compose.dev.yml up -d
```

El modo dev activa hot-reload en backend y frontend, y expone los puertos directamente al host.

## Documentación

- [Arquitectura](docs/architecture.md)
- [API](docs/api.md)
- [Guía de usuario](docs/user-guide.md)
- [Para colaboradores / Claude Code](CLAUDE.md)

## Estado del proyecto

> Sprint 0 — Setup inicial en curso.

## Licencia

MIT © 2026 [Jfalcon19](https://github.com/Jfalcon19)
