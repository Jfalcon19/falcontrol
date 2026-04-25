#!/usr/bin/env bash
# check-windows.sh — Verifica conectividad Ansible con la VM win11.
# No modifica nada. Solo comprueba y reporta.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
INVENTORY="${SCRIPT_DIR}/inventory.ini"

GREEN='\033[0;32m'; RED='\033[0;31m'; YELLOW='\033[1;33m'; NC='\033[0m'
info()  { echo -e "${GREEN}[INFO]${NC}  $*"; }
warn()  { echo -e "${YELLOW}[WARN]${NC}  $*"; }
error() { echo -e "${RED}[ERROR]${NC} $*" >&2; }

if [[ ! -f "${INVENTORY}" ]]; then
    error "No se encuentra ${INVENTORY}. ¿Has creado las VMs primero?"
    exit 1
fi

info "Comprobando conectividad Ansible con win11…"
if ansible -i "${INVENTORY}" win11 -m win_ping 2>&1; then
    info "✓ win11 responde correctamente a win_ping."
else
    error "✗ win11 no responde. Posibles causas:"
    echo ""
    echo "  1. WinRM no está habilitado. En PowerShell (admin) en la VM:"
    echo "     Enable-PSRemoting -Force"
    echo "     winrm quickconfig -quiet"
    echo "     winrm set winrm/config/service/auth '@{Basic=\"true\"}'"
    echo "     winrm set winrm/config/service '@{AllowUnencrypted=\"true\"}'"
    echo "     netsh advfirewall firewall add rule name=\"WinRM HTTP\" protocol=TCP dir=in localport=5985 action=allow"
    echo ""
    echo "  2. La IP en ${INVENTORY} no es correcta."
    echo "     IP actual de win11 según DHCP:"
    virsh net-dhcp-leases default 2>/dev/null | grep -i win || echo "     (no encontrada en DHCP)"
    echo ""
    echo "  3. El usuario/password en inventory.ini no son correctos."
    exit 1
fi
