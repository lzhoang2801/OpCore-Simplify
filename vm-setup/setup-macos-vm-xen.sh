#!/usr/bin/env bash
# =============================================================================
# setup-macos-vm-xen.sh — macOS VM via OpenCore Simplify
#                          openSUSE Tumbleweed + Xen HVM (xl/libxl)
#
# Prérequis : dom0 Xen actif, réseau bridge xenbr0 (ou virbr0)
# Usage     : bash setup-macos-vm-xen.sh [--macos VERSION] [--help]
# =============================================================================
set -euo pipefail
IFS=$'\n\t'

# ── Vérification root ─────────────────────────────────────────────────────────
if [[ "$(id -u)" -ne 0 ]]; then
  echo -e "\033[0;31m[✘]\033[0m Ce script doit être exécuté en root : bash $0 $*"
  exit 1
fi

RED='\033[0;31m'; GRN='\033[0;32m'; YEL='\033[1;33m'
BLU='\033[0;34m'; CYA='\033[0;36m'; RST='\033[0m'; BLD='\033[1m'

log()  { echo -e "${BLU}[$(date +%H:%M:%S)]${RST} $*"; }
ok()   { echo -e "${GRN}[✔]${RST} $*"; }
warn() { echo -e "${YEL}[!]${RST} $*"; }
die()  { echo -e "${RED}[✘]${RST} $*" >&2; exit 1; }
sep()  { echo -e "${CYA}────────────────────────────────────────────────────${RST}"; }

# ── Mode dry-run ──────────────────────────────────────────────────────────────
# En dryrun, les commandes destructives/lentes sont simulées
run() {
  if [[ "${DRYRUN:-0}" -eq 1 ]]; then
    echo -e "${CYA}[dryrun]${RST} $*"
  else
    "$@"
  fi
}

# ── Valeurs par défaut ────────────────────────────────────────────────────────
MACOS_VERSION="ventura"   # sequoia | sonoma | ventura | monterey | big-sur
DISK_SIZE="80G"
RAM_MB=8192               # en Mo (Xen utilise des Mo)
CPU_CORES=4
BRIDGE="xenbr0"           # bridge réseau Xen ; fallback virbr0
VM_DIR="${HOME}/VMs/macos-${MACOS_VERSION}"
OCS_DIR="${HOME}/opcore-simplify"
OCS_REPO="https://github.com/b23prodtm/OpCore-Simplify.git"
OCS_BRANCH="fix/validator"

SKIP_DEPS=0; SKIP_OCS=0; SKIP_RECOVERY=0; RUN_ONLY=0; DRYRUN=0

usage() {
cat <<EOF
${BLD}Usage :${RST} $0 [OPTIONS]

  --macos VERSION      Version cible (défaut: ventura)
                       sequoia | sonoma | ventura | monterey | big-sur
  --disk-size SIZE     Taille disque (défaut: 80G)
  --ram MB             RAM en Mo (défaut: 8192)
  --cores N            vCPUs (défaut: 4)
  --bridge BRIDGE      Bridge réseau (défaut: xenbr0)
  --vm-dir PATH        Répertoire VM
  --ocs-dir PATH       Répertoire OpCore Simplify
  --skip-deps          Ne pas installer les paquets
  --skip-ocs           EFI déjà généré
  --skip-recovery      Ne pas re-télécharger le BaseSystem
  --run-only           Lancer la VM directement (xl create)
  --dryrun             Simuler toutes les étapes sans rien écrire ni installer
  --help
EOF
exit 0
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --macos)         MACOS_VERSION="$2"; shift 2 ;;
    --disk-size)     DISK_SIZE="$2";     shift 2 ;;
    --ram)           RAM_MB="$2";        shift 2 ;;
    --cores)         CPU_CORES="$2";     shift 2 ;;
    --bridge)        BRIDGE="$2";        shift 2 ;;
    --vm-dir)        VM_DIR="$2";        shift 2 ;;
    --ocs-dir)       OCS_DIR="$2";       shift 2 ;;
    --skip-deps)     SKIP_DEPS=1;        shift   ;;
    --skip-ocs)      SKIP_OCS=1;         shift   ;;
    --skip-recovery) SKIP_RECOVERY=1;    shift   ;;
    --run-only)      RUN_ONLY=1;         shift   ;;
    --dryrun)        DRYRUN=1;           shift   ;;
    --help|-h)       usage ;;
    *) die "Argument inconnu : $1" ;;
  esac
done

VM_DIR="${HOME}/VMs/macos-${MACOS_VERSION}"
OPENCORE_IMG="${VM_DIR}/OpenCore.img"
MACOS_DISK="${VM_DIR}/macos.qcow2"
RECOVERY_IMG="${VM_DIR}/BaseSystem.img"
OVMF_CODE=""
OVMF_VARS_SRC=""

# ── 1. Vérifications Xen dom0 ─────────────────────────────────────────────────
check_xen() {
  sep; log "Vérification de l'environnement Xen..."

  # dom0 ?
  if [[ ! -d /proc/xen ]]; then
    die "/proc/xen absent. Ce script doit tourner dans un dom0 Xen."
  fi
  if ! grep -q "control_d" /proc/xen/capabilities 2>/dev/null; then
    die "Pas en dom0 (capabilities ne contient pas 'control_d')."
  fi
  ok "Xen dom0 confirmé"

  # xl disponible ?
  command -v xl &>/dev/null || die "'xl' introuvable. Installez xen-tools."
  ok "xl : $(xl info | awk '/^xen_version/{print $3}')"

  # Version Xen
  local XEN_VER; XEN_VER=$(xl info 2>/dev/null | awk '/^xen_version/{print $3}')
  ok "Xen version : ${XEN_VER}"

  # Bridge réseau
  if ! ip link show "${BRIDGE}" &>/dev/null; then
    warn "Bridge '${BRIDGE}' introuvable."
    # Tenter virbr0 comme fallback
    if ip link show virbr0 &>/dev/null; then
      BRIDGE="virbr0"
      warn "Utilisation de virbr0 à la place."
    else
      warn "Aucun bridge réseau trouvé. La VM démarrera sans réseau."
      warn "Créez un bridge : ip link add ${BRIDGE} type bridge && ip link set ${BRIDGE} up"
      BRIDGE=""
    fi
  else
    ok "Bridge réseau : ${BRIDGE}"
  fi
}

# ── 2. Dépendances zypper ─────────────────────────────────────────────────────
install_deps() {
  sep; log "Installation des dépendances..."

  local PKGS=(
    xen-tools              # xl, xenstore-*, xen-detect
    xen-libs               # libxenctrl etc.
    qemu-x86               # device model QEMU pour Xen HVM
    qemu-tools             # qemu-img
    ovmf                   # firmware UEFI — paquet openSUSE
    python3 python3-pip
    git wget curl
    dmidecode acpica       # pour OpCore Simplify
    p7zip-full
    gdisk                  # sgdisk pour partitionner l'ESP
  )

  run zypper --non-interactive refresh
  # ovmf peut s'appeler différemment sur Tumbleweed
  run zypper --non-interactive install --no-recommends "${PKGS[@]}" 2>/dev/null || \
  run zypper --non-interactive install --no-recommends \
    xen-tools xen-libs qemu-x86 qemu-tools \
    python3 python3-pip git wget curl \
    dmidecode acpica p7zip-full gdisk || true

  ok "Paquets installés"
  _find_ovmf
}

_find_ovmf() {
  # Xen embarque souvent son propre OVMF
  local CANDIDATES_CODE=(
    /usr/lib/xen/boot/ovmf.bin             # OVMF intégré Xen (Tumbleweed)
    /usr/share/qemu/ovmf-x86_64-4m-code.bin
    /usr/share/qemu/ovmf-x86_64-code.bin
    /usr/share/OVMF/OVMF_CODE.fd
  )
  local CANDIDATES_VARS=(
    /usr/lib/xen/boot/ovmf-vars.bin
    /usr/share/qemu/ovmf-x86_64-4m-vars.bin
    /usr/share/qemu/ovmf-x86_64-vars.bin
    /usr/share/OVMF/OVMF_VARS.fd
  )
  for f in "${CANDIDATES_CODE[@]}"; do [[ -f "$f" ]] && { OVMF_CODE="$f"; break; }; done
  for f in "${CANDIDATES_VARS[@]}"; do [[ -f "$f" ]] && { OVMF_VARS_SRC="$f"; break; }; done

  [[ -n "$OVMF_CODE" ]] || die "OVMF_CODE introuvable. Installez 'ovmf' ou vérifiez /usr/lib/xen/boot/"
  ok "OVMF CODE : ${OVMF_CODE}"
  [[ -n "$OVMF_VARS_SRC" ]] && ok "OVMF VARS : ${OVMF_VARS_SRC}" || warn "OVMF VARS absent (mode stateless)"
}

# ── 3. Répertoire VM ──────────────────────────────────────────────────────────
prepare_dirs() {
  sep; log "Préparation de ${VM_DIR}..."
  mkdir -p "${VM_DIR}"
  if [[ -n "${OVMF_VARS_SRC}" && ! -f "${VM_DIR}/OVMF_VARS.fd" ]]; then
    cp "${OVMF_VARS_SRC}" "${VM_DIR}/OVMF_VARS.fd"
    ok "OVMF_VARS.fd copié (persistant par VM)"
  fi
}

# ── 4. OpCore Simplify ────────────────────────────────────────────────────────
run_opcore_simplify() {
  sep; log "OpCore Simplify — génération EFI OpenCore..."

  if [[ ! -d "${OCS_DIR}" ]]; then
    run git clone --branch "${OCS_BRANCH}" "${OCS_REPO}" "${OCS_DIR}"
  else
    local CURRENT_BRANCH; CURRENT_BRANCH=$(git -C "${OCS_DIR}" rev-parse --abbrev-ref HEAD)
    if [[ "${CURRENT_BRANCH}" != "${OCS_BRANCH}" ]]; then
      warn "Branche actuelle '${CURRENT_BRANCH}' ≠ '${OCS_BRANCH}', basculement..."
      run git -C "${OCS_DIR}" fetch origin
      run git -C "${OCS_DIR}" checkout "${OCS_BRANCH}"
    fi
    run git -C "${OCS_DIR}" pull --ff-only origin "${OCS_BRANCH}" || \
      warn "git pull échoué, version locale conservée."
  fi
  ok "Branche : ${OCS_BRANCH} @ $(git -C "${OCS_DIR}" rev-parse --short HEAD)"

  [[ -f "${OCS_DIR}/requirements.txt" ]] && \
    run pip3 install --quiet -r "${OCS_DIR}/requirements.txt"

  cat <<EOF

${YEL}${BLD}══════════════════════════════════════════════════════════════
  OpCore Simplify — Conseils pour VM Xen HVM
  ──────────────────────────────────────────
  • SMBIOS     : MacPro7,1  (Ventura/Sonoma/Sequoia)
                 iMacPro1,1 (Monterey/Big Sur)
  • GPU        : AUCUN (la VM utilise le framebuffer VNC/SDL)
  • USB        : USBInjectAll  (pas USBToolBox, incompatible Linux)
  • Ethernet   : e1000 ou vmxnet3 selon dispo dans macOS
  • SIP/Secure Boot : désactiver pour débug initial
  • Ctrl+C dans OCS = abandon propre, reprise possible
══════════════════════════════════════════════════════════════${RST}

EOF

  pushd "${OCS_DIR}" > /dev/null
  set +e
  python3 OpCore-Simplify.py
  OCS_EXIT=$?
  set -e
  popd > /dev/null

  if [[ $OCS_EXIT -ne 0 ]]; then
    warn "OpCore Simplify a quitté avec le code ${OCS_EXIT} (Ctrl+C ou erreur)."
    warn "Si l'EFI a quand même été généré dans Results/, le script continue."
    warn "Sinon, relancez : bash $0 --skip-deps --skip-recovery"
  fi

  local EFI_PATH
  EFI_PATH=$(find "${OCS_DIR}/Results" -maxdepth 3 -name "EFI" -type d 2>/dev/null | head -1)
  [[ -n "${EFI_PATH}" ]] || die "EFI non trouvé dans ${OCS_DIR}/Results/"
  echo "${EFI_PATH}" > "${VM_DIR}/.ocs_efi_path"
  ok "EFI : ${EFI_PATH}"
}

# ── 5. Image OpenCore (ESP FAT32) ─────────────────────────────────────────────
build_opencore_img() {
  sep; log "Construction de l'image OpenCore (ESP 200 Mo)..."

  # ── Résoudre le chemin EFI (priorité : cache → recherche → saisie manuelle)
  local EFI_PATH=""

  # 1. Chemin sauvegardé par run_opcore_simplify
  local CACHED; CACHED=$(cat "${VM_DIR}/.ocs_efi_path" 2>/dev/null || true)
  if [[ -d "${CACHED}" ]]; then
    EFI_PATH="${CACHED}"
    ok "EFI depuis cache : ${EFI_PATH}"
  fi

  # 2. Recherche dynamique dans OCS_DIR/Results/
  if [[ -z "${EFI_PATH}" ]]; then
    EFI_PATH=$(find "${OCS_DIR}/Results" -maxdepth 4 -name "EFI" -type d 2>/dev/null | head -1 || true)
    if [[ -n "${EFI_PATH}" ]]; then
      ok "EFI trouvé : ${EFI_PATH}"
      echo "${EFI_PATH}" > "${VM_DIR}/.ocs_efi_path"
    fi
  fi

  # 3. Fallback : saisie manuelle
  if [[ -z "${EFI_PATH}" ]]; then
    warn "Aucun dossier EFI trouvé automatiquement dans ${OCS_DIR}/Results/"
    warn "Lancez OpCore Simplify jusqu'au bout (Build OpenCore EFI) puis relancez."
    warn "Ou entrez le chemin manuellement (laisser vide pour annuler) :"
    read -r -p "  Chemin vers le dossier EFI : " EFI_PATH
    [[ -d "${EFI_PATH}" ]] || die "Chemin invalide. Relancez OpCore Simplify puis : bash $0 --skip-deps --skip-recovery"
    echo "${EFI_PATH}" > "${VM_DIR}/.ocs_efi_path"
  fi

  run qemu-img create -f raw "${OPENCORE_IMG}" 200M

  # Table GPT + partition ESP
  run sgdisk -Z "${OPENCORE_IMG}"
  run sgdisk -n 1:2048:411647 -t 1:EF00 -c 1:"EFI System" "${OPENCORE_IMG}"

  # Formater + copier via loop device
  local LOOP; LOOP=$(losetup --find --partscan --show "${OPENCORE_IMG}")
  run mkfs.fat -F32 -n "EFI" "${LOOP}p1"

  local MNT; MNT=$(mktemp -d)
  run mount "${LOOP}p1" "${MNT}"
  run cp -r "${EFI_PATH}" "${MNT}/"
  sync
  run umount "${MNT}"; rmdir "${MNT}"
  run losetup -d "${LOOP}"

  ok "OpenCore.img : ${OPENCORE_IMG}"
}

# ── 6. Recovery macOS ─────────────────────────────────────────────────────────
download_recovery() {
  sep; log "Téléchargement du Recovery macOS (${MACOS_VERSION})..."

  declare -A BOARD_IDS=(
    [sequoia]="Mac-7BA5B2DFE22DDD8C"
    [sonoma]="Mac-226CB3C6A851A671"
    [ventura]="Mac-4B682C642B45593E"
    [monterey]="Mac-FFE5EF870D7BA81A"
    [big-sur]="Mac-42FD25EABCABB274"
  )
  local BOARD="${BOARD_IDS[${MACOS_VERSION}]:-}"
  [[ -n "$BOARD" ]] || die "Version inconnue : ${MACOS_VERSION}"

  local DLDIR="${VM_DIR}/macrecovery"
  mkdir -p "${DLDIR}"

  [[ -f "${DLDIR}/macrecovery.py" ]] || \
    curl -fsSL \
      "https://raw.githubusercontent.com/acidanthera/OpenCorePkg/master/Utilities/macrecovery/macrecovery.py" \
      -o "${DLDIR}/macrecovery.py"

  pushd "${DLDIR}" > /dev/null
  python3 macrecovery.py -b "${BOARD}" -m 00000000000000000 download
  popd > /dev/null

  local DMG; DMG=$(find "${DLDIR}" -name "BaseSystem.dmg" | head -1)
  [[ -f "${DMG}" ]] || die "BaseSystem.dmg introuvable dans ${DLDIR}"

  # Convertir DMG → raw (Xen ne parle pas DMG nativement)
  qemu-img convert -f dmg -O raw "${DMG}" "${RECOVERY_IMG}" 2>/dev/null || cp "${DMG}" "${RECOVERY_IMG}"
  ok "Recovery : ${RECOVERY_IMG}"
}

# ── 7. Disque macOS ───────────────────────────────────────────────────────────
create_macos_disk() {
  sep; log "Création du disque macOS (${DISK_SIZE})..."
  if [[ -f "${MACOS_DISK}" ]]; then
    warn "${MACOS_DISK} existe déjà."
    read -r -p "Recréer (efface les données) ? [o/N] " C
    [[ "${C,,}" == "o" ]] || { ok "Disque conservé."; return; }
  fi
  run qemu-img create -f qcow2 "${MACOS_DISK}" "${DISK_SIZE}"
  ok "Disque : ${MACOS_DISK} (${DISK_SIZE})"
}

# ── 8. Génération de la configuration xl ─────────────────────────────────────
generate_xl_config() {
  sep; log "Génération de la configuration Xen HVM (xl)..."

  local VARS_LINE=""
  if [[ -f "${VM_DIR}/OVMF_VARS.fd" ]]; then
    VARS_LINE="nvramstore = \"${VM_DIR}/OVMF_VARS.fd\""
  fi

  local NET_LINE=""
  if [[ -n "${BRIDGE}" ]]; then
    NET_LINE="vif = ['model=e1000, bridge=${BRIDGE}']"
  else
    NET_LINE="# vif = []  # Pas de bridge détecté — configurez manuellement"
  fi

  # Config mode installation (Recovery monté)
  cat > "${VM_DIR}/macos-install.xl" <<XL
# ═══════════════════════════════════════════════════════════════
#  Configuration Xen HVM — macOS ${MACOS_VERSION} (mode INSTALLATION)
#  Utilisation : xl create ${VM_DIR}/macos-install.xl
# ═══════════════════════════════════════════════════════════════

name        = "macos-${MACOS_VERSION}-install"
type        = "hvm"

# ── Ressources ────────────────────────────────────────────────
vcpus       = ${CPU_CORES}
memory      = ${RAM_MB}

# ── Firmware UEFI ─────────────────────────────────────────────
# Xen utilise son propre OVMF ; si absent, spécifier le chemin :
# bios        = "ovmf"
# bios_path_override = "${OVMF_CODE}"
bios        = "ovmf"
${VARS_LINE}

# ── CPU : présenter comme Intel (requis par macOS) ────────────
cpuid = [
    "0x00000001:ecx=0x00000000:ecx=~0x80000002",
]
# Désactiver APIC x2 (problèmes avec macOS dans certains Xen)
apic        = 1
acpi        = 1
hpet        = 1

# ── Disques ───────────────────────────────────────────────────
# sata.0 : OpenCore EFI (boot)
# sata.1 : Disque macOS principal
# sata.2 : BaseSystem Recovery
disk = [
    'format=raw,  vdev=hda, access=ro, target=${OPENCORE_IMG}',
    'format=qcow2,vdev=hdb, access=rw, target=${MACOS_DISK}',
    'format=raw,  vdev=hdc, access=ro, target=${RECOVERY_IMG}',
]

# ── Réseau ────────────────────────────────────────────────────
${NET_LINE}

# ── USB ───────────────────────────────────────────────────────
usbdevice   = ['tablet']

# ── Affichage : VNC (headless / SSH tunnel) ───────────────────
vnc         = 1
vnclisten   = "127.0.0.1"
vncport     = 5910
vncpasswd   = ""
# Alternative SDL (si Xorg local) :
# sdl         = 1

# ── Device model (QEMU sous Xen) ─────────────────────────────
device_model_version    = "qemu-xen"
device_model_args_hvm   = [
    "-cpu", "Penryn,vendor=GenuineIntel,+sse3,+sse4.2,+avx2,+aes",
    "-global", "PIIX4_PM.disable_s3=1",
    "-global", "PIIX4_PM.disable_s4=1",
]

# ── Divers ────────────────────────────────────────────────────
on_poweroff = "destroy"
on_reboot   = "restart"
on_crash    = "preserve"
XL

  # Config mode normal (sans Recovery)
  cat > "${VM_DIR}/macos.xl" <<XL
# ═══════════════════════════════════════════════════════════════
#  Configuration Xen HVM — macOS ${MACOS_VERSION} (mode NORMAL)
#  Utilisation : xl create ${VM_DIR}/macos.xl
# ═══════════════════════════════════════════════════════════════

name        = "macos-${MACOS_VERSION}"
type        = "hvm"
vcpus       = ${CPU_CORES}
memory      = ${RAM_MB}
bios        = "ovmf"
${VARS_LINE}

cpuid = [
    "0x00000001:ecx=0x00000000:ecx=~0x80000002",
]
apic = 1
acpi = 1
hpet = 1

disk = [
    'format=raw,  vdev=hda, access=ro, target=${OPENCORE_IMG}',
    'format=qcow2,vdev=hdb, access=rw, target=${MACOS_DISK}',
]

${NET_LINE}
usbdevice   = ['tablet']
vnc         = 1
vnclisten   = "127.0.0.1"
vncport     = 5910
vncpasswd   = ""

device_model_version    = "qemu-xen"
device_model_args_hvm   = [
    "-cpu", "Penryn,vendor=GenuineIntel,+sse3,+sse4.2,+avx2,+aes",
    "-global", "PIIX4_PM.disable_s3=1",
    "-global", "PIIX4_PM.disable_s4=1",
]

on_poweroff = "destroy"
on_reboot   = "restart"
on_crash    = "preserve"
XL

  # Script wrapper de lancement
  cat > "${VM_DIR}/run-install.sh" <<'SH'
#!/usr/bin/env bash
# Lance la VM macOS en mode installation (Recovery monté)
XLCFG="$(dirname "$0")/macos-install.xl"
echo "[*] Démarrage VM macOS (mode installation) via xl..."
xl create "${XLCFG}"
echo "[*] Pour voir l'écran, connectez un client VNC sur localhost:5910"
echo "    Exemple : vncviewer localhost:5910"
echo "    Ou via SSH : ssh -L 5910:127.0.0.1:5910 user@dom0 puis vncviewer localhost:5910"
SH
  chmod +x "${VM_DIR}/run-install.sh"

  cat > "${VM_DIR}/run.sh" <<'SH'
#!/usr/bin/env bash
# Lance la VM macOS en mode normal (après installation)
XLCFG="$(dirname "$0")/macos.xl"
echo "[*] Démarrage VM macOS via xl..."
xl create "${XLCFG}"
echo "[*] VNC : vncviewer localhost:5910"
SH
  chmod +x "${VM_DIR}/run.sh"

  ok "Configs xl générées :"
  ok "  Installation : ${VM_DIR}/macos-install.xl"
  ok "  Normal       : ${VM_DIR}/macos.xl"
}

# ── 9. Résumé final ───────────────────────────────────────────────────────────
print_summary() {
  sep
  echo -e "${BLD}${GRN}  VM macOS ${MACOS_VERSION} — Xen HVM — prête !${RST}"
  sep
  cat <<EOF

${BLD}Répertoire :${RST}  ${VM_DIR}
${BLD}RAM        :${RST}  ${RAM_MB} Mo
${BLD}CPUs       :${RST}  ${CPU_CORES}
${BLD}Bridge     :${RST}  ${BRIDGE:-"(aucun)"}

${BLD}${YEL}── Étape 1 : Installation macOS ──────────────────────────────${RST}
  xl create ${VM_DIR}/macos-install.xl
  vncviewer localhost:5910

  Dans OpenCore picker :
    1. Sélectionner "Reset NVRAM" (1er démarrage uniquement)
    2. Démarrer sur "macOS BaseSystem"
    3. Disk Utility → Effacer le disque (APFS, GUID)
    4. Réinstaller macOS → sélectionner le disque APFS

${BLD}${YEL}── Étape 2 : Après installation ──────────────────────────────${RST}
  xl create ${VM_DIR}/macos.xl
  vncviewer localhost:5910

${BLD}${YEL}── Commandes xl utiles ────────────────────────────────────────${RST}
  xl list                        # VMs actives
  xl console macos-${MACOS_VERSION}      # Console série
  xl destroy macos-${MACOS_VERSION}      # Forcer l'extinction
  xl pause / xl unpause          # Suspendre/reprendre

${BLD}${YEL}── Si VNC distant (SSH tunnel) ────────────────────────────────${RST}
  # Sur votre poste local :
  ssh -L 5910:127.0.0.1:5910 user@dom0-host
  vncviewer localhost:5910

EOF
  sep
}

launch_vm() {
  sep; log "Lancement de la VM macOS (mode installation)..."
  xl create "${VM_DIR}/macos-install.xl"
  log "VM démarrée. Connectez-vous via VNC : vncviewer localhost:5910"
}

# ═══════════════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════════════
sep
echo -e "${BLD}  macOS VM Setup — openSUSE Tumbleweed + Xen HVM${RST}"
echo -e "${BLD}  Version macOS : ${CYA}${MACOS_VERSION}${RST}"
sep

if [[ "$RUN_ONLY" -eq 1 ]]; then
  [[ -f "${VM_DIR}/run-install.sh" ]] || die "VM non configurée. Lancez sans --run-only d'abord."
  launch_vm; exit 0
fi

check_xen
[[ "$SKIP_DEPS" -eq 0 ]] && install_deps || _find_ovmf
prepare_dirs
[[ "$SKIP_OCS" -eq 0 ]]      && run_opcore_simplify
build_opencore_img
[[ "$SKIP_RECOVERY" -eq 0 ]] && download_recovery
create_macos_disk
generate_xl_config
print_summary

read -r -p "Lancer la VM maintenant (xl create) ? [o/N] " GO
[[ "${GO,,}" == "o" ]] && launch_vm || ok "Lancez manuellement : bash ${VM_DIR}/run-install.sh"
