# Guía de usuario — Falcontrol

Esta guía explica el flujo de trabajo habitual para un administrador: desde el primer acceso hasta lanzar un playbook programado.

## Índice

1. [Primer acceso](#1-primer-acceso)
2. [Gestión de hosts](#2-gestión-de-hosts)
3. [Inventarios](#3-inventarios)
4. [Credenciales](#4-credenciales)
5. [Lanzar un job](#5-lanzar-un-job)
6. [Ver logs en tiempo real](#6-ver-logs-en-tiempo-real)
7. [Programar ejecuciones](#7-programar-ejecuciones)
8. [Dashboard](#8-dashboard)
9. [Gestión de usuarios](#9-gestión-de-usuarios)
10. [Roles y permisos](#10-roles-y-permisos)

---

## 1. Primer acceso

Tras levantar el stack con `docker compose up -d`, abre `http://localhost` en tu navegador.

Inicia sesión con las credenciales definidas en `.env` (`FIRST_ADMIN_EMAIL` / `FIRST_ADMIN_PASSWORD`). Estas credenciales son las del primer usuario administrador, creado automáticamente al arrancar.

> **Cambia la contraseña del admin por defecto** antes de exponer la aplicación a la red.

---

## 2. Gestión de hosts

Los hosts son las máquinas que Ansible gestionará.

**Añadir un host:**

1. Ve a **Hosts** en el sidebar.
2. Pulsa **Nuevo host**.
3. Rellena los campos:
   - **Nombre**: identificador legible (ej. `servidor-web-01`)
   - **Dirección**: IP o FQDN (ej. `192.168.1.10`)
   - **Tipo de SO**: `linux` o `windows`
   - **Tipo de conexión**: `ssh` (Linux) o `winrm` (Windows)
   - **Puerto**: déjalo en blanco para usar el predeterminado (22 para SSH, 5985 para WinRM)
   - **Tags**: etiquetas libres para filtrar (ej. `web`, `produccion`)
4. Pulsa **Crear**.

**Editar o desactivar**: usa el botón de edición en la fila del host. Desactivar un host lo excluye de inventarios futuros pero no elimina los datos.

---

## 3. Inventarios

Un inventario agrupa hosts sobre los que ejecutar un playbook.

**Crear un inventario:**

1. Ve a **Inventarios** en el sidebar.
2. Pulsa **Nuevo inventario**.
3. Pon un nombre descriptivo (ej. `servidores-web`).
4. Selecciona los hosts que forman parte de este inventario.
5. Pulsa **Crear**.

Puedes editar el inventario en cualquier momento para añadir o quitar hosts.

---

## 4. Credenciales

Las credenciales se cifran con Fernet antes de guardarse. El secreto nunca se muestra tras la creación.

**Tipos de credencial:**

| Tipo | Uso | Campos necesarios |
|------|-----|-------------------|
| `ssh_key` | Clave privada SSH | usuario + clave privada + passphrase (opcional) |
| `ssh_password` | Contraseña SSH | usuario + password |
| `winrm` | Windows Remote Management | usuario + password |

**Añadir una credencial:**

1. Ve a **Credenciales** en el sidebar.
2. Pulsa **Nueva credencial**.
3. Selecciona el tipo y rellena los campos. El campo **Secreto** es la clave privada o password.
4. Pulsa **Crear**.

> Las credenciales no se asocian directamente a hosts en el MVP; se usan en el inventario generado para Ansible. En una versión futura se podrá asignar credencial por host.

---

## 5. Lanzar un job

Un job es una ejecución de un playbook Ansible contra un inventario.

**Desde la interfaz:**

1. Ve a **Jobs** en el sidebar.
2. Pulsa **Lanzar job**.
3. Selecciona el inventario de destino.
4. Escribe la ruta absoluta del playbook dentro del contenedor (ej. `/opt/playbooks/ping.yml`).
5. Pulsa **Lanzar**.

El job pasa por los estados: `pending` → `running` → `success` / `failed`.

**Desde la API:**

```bash
curl -X POST http://localhost/api/jobs \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"inventory_id": "<uuid>", "playbook_path": "/opt/playbooks/ping.yml"}'
```

---

## 6. Ver logs en tiempo real

Al hacer clic en un job con estado `running` o `pending`, se abre la vista de detalle con un terminal que muestra el stdout de Ansible línea a línea.

- La conexión es un WebSocket; no hace falta recargar la página.
- Si el job ya terminó, se muestra el stdout completo almacenado.
- El botón de volver lleva de nuevo a la lista de jobs.

---

## 7. Programar ejecuciones

Los schedules ejecutan playbooks automáticamente según una expresión cron.

**Crear un schedule:**

1. Ve a **Schedules** en el sidebar.
2. Pulsa **Nuevo schedule**.
3. Rellena:
   - **Nombre**: identificador único (ej. `backup-diario`)
   - **Expresión cron**: 5 campos — `minuto hora día mes día_semana`
   - **Inventario**: dónde ejecutar el playbook
   - **Ruta del playbook**: ruta absoluta dentro del contenedor
   - **Habilitado**: activa o desactiva al crear
4. Pulsa **Crear**.

**Ejemplos de expresiones cron:**

| Expresión | Significado |
|-----------|-------------|
| `0 2 * * *` | Todos los días a las 02:00 |
| `*/15 * * * *` | Cada 15 minutos |
| `0 8 * * 1` | Todos los lunes a las 08:00 |
| `0 0 1 * *` | El primer día de cada mes a las 00:00 |

**Activar / desactivar**: haz clic en el badge **Activo** / **Inactivo** de la fila para alternar el estado sin eliminar el schedule.

**Eliminar**: solo administradores. El schedule se desregistra de Celery Beat automáticamente.

---

## 8. Dashboard

El Dashboard muestra el estado global del sistema en tiempo real.

| Métrica | Descripción |
|---------|-------------|
| **Hosts** | Total de hosts registrados |
| **Inventarios** | Total de inventarios |
| **Schedules** | Total de schedules configurados |
| **Jobs totales** | Todos los jobs en historial |
| **Jobs activos** | Jobs con estado `running` en este momento |
| **Fallos (24h)** | Jobs fallidos en las últimas 24 horas |

La tabla inferior muestra los **10 jobs más recientes** con enlace al detalle de cada uno.

La vista se recarga automáticamente cada 30 segundos.

---

## 9. Gestión de usuarios

Solo los administradores pueden crear usuarios. Accede a la API directamente:

```bash
# Crear un operador
curl -X POST http://localhost/api/users \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"email": "operador@empresa.com", "password": "password123", "role": "operator"}'

# Crear un viewer (solo lectura)
curl -X POST http://localhost/api/users \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"email": "auditor@empresa.com", "password": "password123", "role": "viewer"}'
```

---

## 10. Roles y permisos

| Acción | viewer | operator | admin |
|--------|:------:|:--------:|:-----:|
| Ver hosts, inventarios, credenciales | ✓ | ✓ | ✓ |
| Ver jobs y schedules | ✓ | ✓ | ✓ |
| Ver dashboard | ✓ | ✓ | ✓ |
| Crear/editar hosts, inventarios, credenciales | — | ✓ | ✓ |
| Lanzar jobs | — | ✓ | ✓ |
| Crear/editar schedules | — | ✓ | ✓ |
| Eliminar cualquier recurso | — | — | ✓ |
| Crear usuarios | — | — | ✓ |
