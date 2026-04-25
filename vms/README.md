# VMs de desarrollo — Falcontrol

Este directorio contiene scripts idempotentes para crear y gestionar las VMs del entorno de pruebas.

## VMs del entorno

| VM | Rol | SO | RAM | Disco |
|----|-----|-----|-----|-------|
| `falcontrol-controller` | Stack Falcontrol | Debian 13 | 4 GB | 30 GB |
| `falcontrol-linux` | Target Linux | Debian 13 | 2 GB | 15 GB |
| `win11` | Target Windows | TinyWin11 + WinRM | 6 GB | — |

## Prerequisitos

```bash
sudo apt install libvirt-clients virt-manager cloud-image-utils virtinst
sudo usermod -aG libvirt,kvm $(whoami)
# Cierra sesión y vuelve a entrar para que el grupo surta efecto
```

## Paso 1: Descargar imagen base Debian 13

Los scripts comprueban si la imagen ya existe en `/var/lib/libvirt/images/`. Si no está, muestran el comando para descargarla. Ejecuta manualmente:

```bash
sudo wget -O /var/lib/libvirt/images/debian-13-genericcloud-amd64.qcow2 \
  https://cloud.debian.org/images/cloud/trixie/latest/debian-13-genericcloud-amd64.qcow2
```

O con curl:

```bash
sudo curl -L -o /var/lib/libvirt/images/debian-13-genericcloud-amd64.qcow2 \
  https://cloud.debian.org/images/cloud/trixie/latest/debian-13-genericcloud-amd64.qcow2
```

Verifica la integridad con el SHA256 publicado en https://cloud.debian.org/images/cloud/trixie/latest/SHA256SUMS.

## Paso 2: Crear las VMs

```bash
# VM del stack (falcontrol-controller)
bash vms/provision-controller.sh

# VM target Linux (falcontrol-linux)
bash vms/provision-linux-target.sh
```

Ambos scripts:
- Comprueban si la VM ya existe (idempotentes).
- Generan `~/.ssh/falcontrol_ed25519` si no existe.
- Inyectan la clave pública vía cloud-init.
- Detectan la IP automáticamente al arrancar.

## Paso 3: Actualizar inventory.ini

Una vez creadas las VMs, obtén sus IPs:

```bash
virsh net-dhcp-leases default
```

Edita `vms/inventory.ini` y sustituye `CONTROLLER_IP`, `LINUX_TARGET_IP` y `WIN11_IP`.

## Paso 4: Verificar conectividad

```bash
# Linux targets
ansible -i vms/inventory.ini linux_targets -m ping

# Windows
bash vms/check-windows.sh
```

## Sobre la VM win11

La VM `win11` ya existe. **No la toques** (no la destruyas ni redefinas). Solo se usa con `win_ping` para verificar WinRM.

Si `check-windows.sh` falla, habilita WinRM desde PowerShell (admin) en la VM:

```powershell
Enable-PSRemoting -Force
winrm quickconfig -quiet
winrm set winrm/config/service/auth '@{Basic="true"}'
winrm set winrm/config/service '@{AllowUnencrypted="true"}'
netsh advfirewall firewall add rule name="WinRM HTTP" protocol=TCP dir=in localport=5985 action=allow
```

## Gestión básica de VMs

```bash
virsh list --all                    # listar todas las VMs
virsh start falcontrol-controller   # arrancar
virsh shutdown falcontrol-linux     # apagar limpiamente
virsh domifaddr falcontrol-linux --source agent  # obtener IP
ssh -i ~/.ssh/falcontrol_ed25519 admin@<IP>      # conectar
```
