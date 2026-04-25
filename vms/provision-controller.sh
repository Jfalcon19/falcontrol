#!/usr/bin/env bash
# provision-controller.sh — Aprovisiona la VM falcontrol-controller (Debian 13)
# Idempotente: comprueba si la VM ya existe antes de crear nada.
# Uso: bash vms/provision-controller.sh

set -euo pipefail

# ─── Configuración ───────────────────────────────────────────────────────────
LIBVIRT_URI="qemu:///system"   # la red "default" vive en system, no en session

VM_NAME="falcontrol-controller"
VM_RAM=4096       # MiB
VM_VCPUS=2
VM_DISK=30        # GiB
VM_OS_VARIANT="debian13"
VM_IMAGE_DIR="/var/lib/libvirt/images"
BASE_IMAGE="debian-13-genericcloud-amd64.qcow2"
BASE_IMAGE_URL="https://cloud.debian.org/images/cloud/trixie/latest/debian-13-genericcloud-amd64.qcow2"
VM_IMAGE="${VM_IMAGE_DIR}/${VM_NAME}.qcow2"
SEED_IMAGE="${VM_IMAGE_DIR}/${VM_NAME}-seed.img"
SSH_KEY="${HOME}/.ssh/falcontrol_ed25519"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CLOUD_INIT_DIR="${SCRIPT_DIR}/cloud-init"
TMP_DIR=$(mktemp -d)

# ─── Colores ─────────────────────────────────────────────────────────────────
RED='\033[0;31m'; GREEN='\033[0;32m'; YELLOW='\033[1;33m'; NC='\033[0m'
info()  { echo -e "${GREEN}[INFO]${NC}  $*"; }
warn()  { echo -e "${YELLOW}[WARN]${NC}  $*"; }
error() { echo -e "${RED}[ERROR]${NC} $*" >&2; }

cleanup() { rm -rf "${TMP_DIR}"; }
trap cleanup EXIT

# ─── 1. Comprobar dependencias ───────────────────────────────────────────────
for cmd in virsh virt-install cloud-localds qemu-img; do
    if ! command -v "${cmd}" &>/dev/null; then
        error "Dependencia no encontrada: ${cmd}. Instala libvirt-clients virt-install cloud-image-utils."
        exit 1
    fi
done

# ─── 2. Verificar acceso a qemu:///system ────────────────────────────────────
if ! virsh --connect "${LIBVIRT_URI}" version &>/dev/null; then
    error "No se puede conectar a ${LIBVIRT_URI}."
    echo ""
    echo "  Asegurate de que tu usuario pertenece al grupo 'libvirt':"
    echo "    sudo usermod -aG libvirt \$(whoami)"
    echo "  Luego cierra sesion y vuelve a entrar, o ejecuta:"
    echo "    newgrp libvirt"
    echo ""
    exit 1
fi
info "Conexion a ${LIBVIRT_URI} OK."

# ─── 3. Verificar (y arrancar si es necesario) la red default ────────────────
NET_STATE=$(virsh --connect "${LIBVIRT_URI}" net-info default 2>/dev/null \
    | grep -i "^Active:" | awk '{print $2}' || echo "missing")

if [[ "${NET_STATE}" == "missing" ]]; then
    error "La red 'default' no existe en ${LIBVIRT_URI}. Creala con:"
    echo "  virsh --connect ${LIBVIRT_URI} net-define /usr/share/libvirt/networks/default.xml"
    echo "  virsh --connect ${LIBVIRT_URI} net-autostart default"
    echo "  virsh --connect ${LIBVIRT_URI} net-start default"
    exit 1
elif [[ "${NET_STATE}" != "yes" ]]; then
    warn "Red 'default' inactiva. Arrancandola..."
    virsh --connect "${LIBVIRT_URI}" net-start default
    info "Red 'default' activa."
else
    info "Red 'default' activa."
fi

# ─── 4. Comprobar si la VM ya existe ─────────────────────────────────────────
if virsh --connect "${LIBVIRT_URI}" dominfo "${VM_NAME}" &>/dev/null; then
    warn "La VM '${VM_NAME}' ya existe. Usa 'virsh --connect ${LIBVIRT_URI} start ${VM_NAME}' para arrancarla."
    warn "Si quieres recrearla, ejecuta primero:"
    warn "  virsh --connect ${LIBVIRT_URI} destroy ${VM_NAME}"
    warn "  virsh --connect ${LIBVIRT_URI} undefine ${VM_NAME} --remove-all-storage"
    exit 0
fi

info "Creando VM '${VM_NAME}'..."

# ─── 5. Generar clave SSH dedicada si no existe ───────────────────────────────
if [[ ! -f "${SSH_KEY}" ]]; then
    info "Generando clave SSH dedicada en ${SSH_KEY}..."
    ssh-keygen -t ed25519 -f "${SSH_KEY}" -N "" -C "falcontrol-dev"
fi
SSH_PUBKEY=$(cat "${SSH_KEY}.pub")

# ─── 6. Comprobar imagen base ─────────────────────────────────────────────────
if [[ ! -f "${VM_IMAGE_DIR}/${BASE_IMAGE}" ]]; then
    error "Imagen base no encontrada: ${VM_IMAGE_DIR}/${BASE_IMAGE}"
    echo ""
    echo "  Descargala con:"
    echo "    sudo wget -O '${VM_IMAGE_DIR}/${BASE_IMAGE}' '${BASE_IMAGE_URL}'"
    echo "  O bien:"
    echo "    sudo curl -L -o '${VM_IMAGE_DIR}/${BASE_IMAGE}' '${BASE_IMAGE_URL}'"
    echo ""
    exit 1
fi

# ─── 7. Crear disco de la VM ──────────────────────────────────────────────────
info "Creando disco ${VM_IMAGE} (${VM_DISK} GiB)..."
sudo qemu-img create -f qcow2 -b "${VM_IMAGE_DIR}/${BASE_IMAGE}" -F qcow2 "${VM_IMAGE}" "${VM_DISK}G"

# ─── 8. Preparar cloud-init ───────────────────────────────────────────────────
info "Preparando seed cloud-init..."
sed \
    -e "s|FALCONTROL_VM_HOSTNAME|${VM_NAME}|g" \
    -e "s|FALCONTROL_SSH_PUBKEY|${SSH_PUBKEY}|g" \
    "${CLOUD_INIT_DIR}/user-data.yaml" > "${TMP_DIR}/user-data"

sed \
    -e "s|FALCONTROL_VM_HOSTNAME|${VM_NAME}|g" \
    -e "s|FALCONTROL_INSTANCE_ID|$(uuidgen 2>/dev/null || date +%s)|g" \
    "${CLOUD_INIT_DIR}/meta-data.yaml" > "${TMP_DIR}/meta-data"

cloud-localds -N "${CLOUD_INIT_DIR}/network-config.yaml" \
    "${SEED_IMAGE}" "${TMP_DIR}/user-data" "${TMP_DIR}/meta-data"

# ─── 9. Instalar la VM ────────────────────────────────────────────────────────
info "Ejecutando virt-install..."
virt-install \
    --connect "${LIBVIRT_URI}" \
    --name "${VM_NAME}" \
    --memory "${VM_RAM}" \
    --vcpus "${VM_VCPUS}" \
    --disk "path=${VM_IMAGE},format=qcow2,bus=virtio" \
    --disk "path=${SEED_IMAGE},device=cdrom" \
    --os-variant "${VM_OS_VARIANT}" \
    --network network=default,model=virtio \
    --graphics none \
    --console pty,target_type=serial \
    --import \
    --noautoconsole \
    --wait 0

info "VM '${VM_NAME}' creada. Esperando a que aparezca lease DHCP (max 120 s)..."

# Espera activa: busca lease DHCP por MAC (mas fiable que por nombre)
VM_MAC=$(virsh --connect "${LIBVIRT_URI}" domiflist "${VM_NAME}" 2>/dev/null \
    | awk '/virtio/{print $5}')
IP="UNKNOWN"
for i in $(seq 1 24); do
    sleep 5
    IP=$(virsh --connect "${LIBVIRT_URI}" net-dhcp-leases default 2>/dev/null \
        | grep -i "${VM_MAC}" | grep -oP '(\d{1,3}\.){3}\d{1,3}' | head -1 || true)
    if [[ -n "${IP}" ]]; then
        break
    fi
    IP="UNKNOWN"
done

info "IP detectada: ${IP}"

INVENTORY="${SCRIPT_DIR}/inventory.ini"
if grep -q "CONTROLLER_IP" "${INVENTORY}" 2>/dev/null; then
    sed -i "s|CONTROLLER_IP|${IP}|" "${INVENTORY}"
    info "inventory.ini actualizado con IP ${IP}."
fi

info "OK: '${VM_NAME}' lista. Conectate con:"
echo "  ssh -i ${SSH_KEY} admin@${IP}"
