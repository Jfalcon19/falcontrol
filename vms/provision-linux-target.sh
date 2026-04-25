#!/usr/bin/env bash
# provision-linux-target.sh — Aprovisiona la VM falcontrol-linux (Debian 13)
# Idempotente: comprueba si la VM ya existe antes de crear nada.
# Uso: bash vms/provision-linux-target.sh

set -euo pipefail

VM_NAME="falcontrol-linux"
VM_RAM=2048       # MiB
VM_VCPUS=1
VM_DISK=15        # GiB
VM_OS_VARIANT="debian12"
VM_IMAGE_DIR="/var/lib/libvirt/images"
BASE_IMAGE="debian-13-genericcloud-amd64.qcow2"
BASE_IMAGE_URL="https://cloud.debian.org/images/cloud/trixie/latest/debian-13-genericcloud-amd64.qcow2"
VM_IMAGE="${VM_IMAGE_DIR}/${VM_NAME}.qcow2"
SEED_IMAGE="${VM_IMAGE_DIR}/${VM_NAME}-seed.img"
SSH_KEY="${HOME}/.ssh/falcontrol_ed25519"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CLOUD_INIT_DIR="${SCRIPT_DIR}/cloud-init"
TMP_DIR=$(mktemp -d)

RED='\033[0;31m'; GREEN='\033[0;32m'; YELLOW='\033[1;33m'; NC='\033[0m'
info()  { echo -e "${GREEN}[INFO]${NC}  $*"; }
warn()  { echo -e "${YELLOW}[WARN]${NC}  $*"; }
error() { echo -e "${RED}[ERROR]${NC} $*" >&2; }

cleanup() { rm -rf "${TMP_DIR}"; }
trap cleanup EXIT

for cmd in virsh virt-install cloud-localds qemu-img; do
    if ! command -v "${cmd}" &>/dev/null; then
        error "Dependencia no encontrada: ${cmd}"
        exit 1
    fi
done

if virsh dominfo "${VM_NAME}" &>/dev/null; then
    warn "La VM '${VM_NAME}' ya existe. Usa 'virsh start ${VM_NAME}' para arrancarla."
    exit 0
fi

info "Creando VM '${VM_NAME}'…"

if [[ ! -f "${SSH_KEY}" ]]; then
    info "Generando clave SSH dedicada en ${SSH_KEY}…"
    ssh-keygen -t ed25519 -f "${SSH_KEY}" -N "" -C "falcontrol-dev"
fi
SSH_PUBKEY=$(cat "${SSH_KEY}.pub")

if [[ ! -f "${VM_IMAGE_DIR}/${BASE_IMAGE}" ]]; then
    error "Imagen base no encontrada: ${VM_IMAGE_DIR}/${BASE_IMAGE}"
    echo ""
    echo "  Descárgala con:"
    echo "    wget -O '${VM_IMAGE_DIR}/${BASE_IMAGE}' '${BASE_IMAGE_URL}'"
    echo ""
    exit 1
fi

info "Creando disco ${VM_IMAGE} (${VM_DISK} GiB)…"
sudo qemu-img create -f qcow2 -b "${VM_IMAGE_DIR}/${BASE_IMAGE}" -F qcow2 "${VM_IMAGE}" "${VM_DISK}G"

info "Preparando seed cloud-init…"
sed \
    -e "s|FALCONTROL_VM_HOSTNAME|${VM_NAME}|g" \
    -e "s|FALCONTROL_SSH_PUBKEY|${SSH_PUBKEY}|g" \
    "${CLOUD_INIT_DIR}/user-data.yaml" > "${TMP_DIR}/user-data"

sed \
    -e "s|FALCONTROL_VM_HOSTNAME|${VM_NAME}|g" \
    -e "s|FALCONTROL_INSTANCE_ID|$(uuidgen 2>/dev/null || date +%s)|g" \
    "${CLOUD_INIT_DIR}/meta-data.yaml" > "${TMP_DIR}/meta-data"

cloud-localds "${SEED_IMAGE}" "${TMP_DIR}/user-data" "${TMP_DIR}/meta-data"

info "Ejecutando virt-install…"
virt-install \
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

info "VM '${VM_NAME}' creada. Esperando a que arranque…"
sleep 30

IP=$(virsh domifaddr "${VM_NAME}" --source agent 2>/dev/null \
    | grep -oP '(\d{1,3}\.){3}\d{1,3}' | grep -v '127\.' | head -1 \
    || virsh net-dhcp-leases default 2>/dev/null \
    | grep "${VM_NAME}" | grep -oP '(\d{1,3}\.){3}\d{1,3}' | head -1 \
    || echo "UNKNOWN")

info "IP detectada: ${IP}"

info "✓ '${VM_NAME}' lista. Conéctate con:"
echo "  ssh -i ${SSH_KEY} admin@${IP}"
