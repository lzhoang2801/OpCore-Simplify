#!/usr/bin/env bash
# =============================================================================
# setup-macos-vm.sh — macOS VM via OpenCore Simplify sur openSUSE Tumbleweed
# Prérequis : QEMU installé (zypper), KVM activé
# Usage     : bash setup-macos-vm.sh [--macos VERSION] [--disk-size SIZE] [--help]
# =============================================================================
set -euo pipefail
IFS=$'\n\t'

# ── Vérification root ─────────────────────────────────────────────────────────
if [[ "$(id -u)" -ne 0 ]]; then
  echo -e "\033[0;31m[✘]\033[0m Ce script doit être exécuté en root : bash $0 $*"
  exit 1
fi

# ── Couleurs ──────────────────────────────────────────────────────────────────
RED='\033[0;31m'; GRN='\033[0;32m'; YEL='\033[1;33m'
BLU='\033[0;34m'; CYA='\033[0;36m'; RST='\033[0m'; BLD='\033[1m'

log()  { echo -e "${BLU}[$(date +%H:%M:%S)]${RST} $*"; }
ok()   { echo -e "${GRN}[✔]${RST} $*"; }
warn() { echo -e "${YEL}[!]${RST} $*"; }
die()  { echo -e "${RED}[✘] ERREUR :${RST} $*" >&2; exit 1; }
sep()  { echo -e "${CYA}────────────────────────────────────────────────────${RST}"; }

# ── Mode dry-run ──────────────────────────────────────────────────────────────
run() {
  if [[ "${DRYRUN:-0}" -eq 1 ]]; then
    echo -e "${CYA}[dryrun]${RST} $*"
  else
    "$@"
  fi
}

# ── Valeurs par défaut ────────────────────────────────────────────────────────
MACOS_VERSION="ventura"          # sequoia | sonoma | ventura | monterey | big-sur
DISK_SIZE="80G"
RAM="8G"
CPU_CORES=4
VM_DIR="${HOME}/VMs/macos-${MACOS_VERSION}"
OCS_DIR="${HOME}/opcore-simplify"
OCS_REPO="https://github.com/b23prodtm/OpCore-Simplify.git"
OCS_BRANCH="fix/validator"
FETCH_MACOS_URL="https://raw.githubusercontent.com/corpnewt/gibMacOS/master/gibMacOS.command"
OPENCORE_IMG="${VM_DIR}/OpenCore.img"
MACOS_DISK="${VM_DIR}/macos.qcow2"
RECOVERY_IMG="${VM_DIR}/BaseSystem.img"
OVMF_CODE=""   # détecté automatiquement
OVMF_VARS=""

# ── Parsing des arguments ─────────────────────────────────────────────────────
usage() {
cat <<EOF
${BLD}Usage :${RST} $0 [OPTIONS]

${BLD}Options :${RST}
  --macos VERSION    Version macOS à installer (défaut: ventura)
                     Valeurs: sequoia | sonoma | ventura | monterey | big-sur
  --disk-size SIZE   Taille du disque VM (défaut: 80G)
  --ram SIZE         RAM allouée (défaut: 8G)
  --cores N          Nombre de vCPUs (défaut: 4)
  --vm-dir PATH      Répertoire de la VM (défaut: ~/VMs/macos-VERSION)
  --ocs-dir PATH     Répertoire OpCore Simplify (défaut: ~/opcore-simplify)
  --skip-deps        Ne pas installer les dépendances système
  --skip-ocs         Ne pas relancer OpCore Simplify (EFI déjà généré)
  --skip-recovery    Ne pas re-télécharger le Recovery
  --run-only         Lancer directement la VM (skips tout sauf launch)
  --dryrun           Simuler toutes les étapes sans rien écrire ni installer
  --help             Afficher cette aide

${BLD}Exemples :${RST}
  $0 --macos sonoma --disk-size 120G
  $0 --macos ventura --skip-ocs   # EFI déjà dans \$OCS_DIR/Results/
EOF
exit 0
}

SKIP_DEPS=0; SKIP_OCS=0; SKIP_RECOVERY=0; RUN_ONLY=0; DRYRUN=0
while [[ $# -gt 0 ]]; do
  case "$1" in
    --macos)        MACOS_VERSION="$2"; shift 2 ;;
    --disk-size)    DISK_SIZE="$2";     shift 2 ;;
    --ram)          RAM="$2";           shift 2 ;;
    --cores)        CPU_CORES="$2";     shift 2 ;;
    --vm-dir)       VM_DIR="$2";        shift 2 ;;
    --ocs-dir)      OCS_DIR="$2";       shift 2 ;;
    --skip-deps)    SKIP_DEPS=1;        shift   ;;
    --skip-ocs)     SKIP_OCS=1;         shift   ;;
    --skip-recovery)SKIP_RECOVERY=1;    shift   ;;
    --run-only)     RUN_ONLY=1;         shift   ;;
    --dryrun)       DRYRUN=1;           shift   ;;
    --help|-h)      usage ;;
    *) die "Argument inconnu : $1. Lancez --help." ;;
  esac
done

VM_DIR="${HOME}/VMs/macos-${MACOS_VERSION}"
OPENCORE_IMG="${VM_DIR}/OpenCore.img"
MACOS_DISK="${VM_DIR}/macos.qcow2"
RECOVERY_IMG="${VM_DIR}/BaseSystem.img"

# ── Vérification OS ───────────────────────────────────────────────────────────
check_os() {
  sep; log "Vérification de l'environnement..."
  [[ -f /etc/os-release ]] || die "Impossible de détecter l'OS."
  # shellcheck disable=SC1091
  source /etc/os-release
  if [[ "${ID:-}" != "opensuse-tumbleweed" && "${ID_LIKE:-}" != *"suse"* ]]; then
    warn "OS détecté : ${PRETTY_NAME:-inconnu}"
    warn "Ce script cible openSUSE Tumbleweed. Adaptez les commandes zypper si nécessaire."
  else
    ok "OS : ${PRETTY_NAME}"
  fi

  # KVM disponible ?
  if [[ ! -e /dev/kvm ]]; then
    die "/dev/kvm introuvable. Activez la virtualisation dans le BIOS/UEFI (Intel VT-x / AMD-V)."
  fi
  ok "KVM disponible"

  # Droits sur /dev/kvm
  if ! groups | grep -qE "kvm|virt"; then
    warn "L'utilisateur n'est pas dans le groupe 'kvm'. Ajout..."
    run usermod -aG kvm "$USER"
    warn "Reconnectez-vous pour que le changement soit effectif, ou lancez : newgrp kvm"
  else
    ok "Groupe KVM OK"
  fi
}

# ── Installation des dépendances ──────────────────────────────────────────────
install_deps() {
  sep; log "Installation des dépendances via zypper..."

  local PKGS=(
    qemu-full          # QEMU complet (x86, audio, usb, etc.)
    qemu-ovmf-x86_64   # Firmware UEFI OVMF
    qemu-tools         # qemu-img, qemu-nbd
    python3            # pour OpCore Simplify
    python3-pip
    git
    dmidecode          # lecture hardware (utilisé par OpCore Simplify)
    acpica             # iasl pour tables ACPI
    wget curl          # téléchargements
    p7zip-full         # extraction archives macOS
  )

  run zypper --non-interactive refresh
  run zypper --non-interactive install --no-recommends "${PKGS[@]}" || \
    warn "Certains paquets peuvent déjà être installés."

  ok "Dépendances installées"

  # Trouver OVMF
  for path in \
    /usr/share/qemu/ovmf-x86_64-4m-code.bin \
    /usr/share/qemu/ovmf-x86_64-code.bin \
    /usr/share/OVMF/OVMF_CODE.fd; do
    if [[ -f "$path" ]]; then
      OVMF_CODE="$path"
      break
    fi
  done
  for path in \
    /usr/share/qemu/ovmf-x86_64-4m-vars.bin \
    /usr/share/qemu/ovmf-x86_64-vars.bin \
    /usr/share/OVMF/OVMF_VARS.fd; do
    if [[ -f "$path" ]]; then
      OVMF_VARS="$path"
      break
    fi
  done

  [[ -n "$OVMF_CODE" ]] || die "Firmware OVMF introuvable. Installez qemu-ovmf-x86_64."
  ok "OVMF CODE : $OVMF_CODE"
  ok "OVMF VARS : $OVMF_VARS"
}

# ── Préparation du répertoire VM ──────────────────────────────────────────────
prepare_dirs() {
  sep; log "Préparation du répertoire VM : ${VM_DIR}"
  mkdir -p "${VM_DIR}"
  # Copie locale des VARS OVMF (modifiable par la VM)
  if [[ ! -f "${VM_DIR}/OVMF_VARS.fd" ]]; then
    cp "${OVMF_VARS}" "${VM_DIR}/OVMF_VARS.fd"
    ok "OVMF_VARS copié dans ${VM_DIR}/"
  else
    ok "OVMF_VARS déjà présent"
  fi
}

# ── OpCore Simplify — génération EFI ─────────────────────────────────────────
run_opcore_simplify() {
  sep; log "OpCore Simplify — Génération de l'EFI OpenCore..."

  if [[ ! -d "${OCS_DIR}" ]]; then
    log "Clonage du dépôt OpCore Simplify (branche ${OCS_BRANCH})..."
    run git clone --branch "${OCS_BRANCH}" "${OCS_REPO}" "${OCS_DIR}"
  else
    local CURRENT_BRANCH; CURRENT_BRANCH=$(git -C "${OCS_DIR}" rev-parse --abbrev-ref HEAD)
    if [[ "${CURRENT_BRANCH}" != "${OCS_BRANCH}" ]]; then
      warn "Branche actuelle '${CURRENT_BRANCH}' ≠ '${OCS_BRANCH}', basculement..."
      run git -C "${OCS_DIR}" fetch origin
      run git -C "${OCS_DIR}" checkout "${OCS_BRANCH}"
    fi
    log "Mise à jour du dépôt OpCore Simplify..."
    run git -C "${OCS_DIR}" pull --ff-only origin "${OCS_BRANCH}" || warn "Mise à jour git échouée, version locale conservée."
  fi
  ok "Branche : ${OCS_BRANCH} @ $(git -C "${OCS_DIR}" rev-parse --short HEAD)"

  # Installer les dépendances Python
  if [[ -f "${OCS_DIR}/requirements.txt" ]]; then
    run pip3 install --quiet -r "${OCS_DIR}/requirements.txt"
  fi

  # Patch VM : forcer le profil SMBIOS MacPro7,1 ou iMacPro1,1 adapté QEMU
  # OpCore Simplify détecte le hardware réel → on peut le guider via env
  cat <<EOF

${YEL}${BLD}══════════════════════════════════════════════════════════════${RST}
${YEL}  OpCore Simplify va démarrer en mode interactif.${RST}
${YEL}  Conseils pour une VM QEMU macOS :${RST}
${YEL}  • SMBIOS recommandé : MacPro7,1 (ou iMacPro1,1)${RST}
${YEL}  • Désactiver SecureBoot / SIP dans les options${RST}
${YEL}  • Cocher : VirtIO pour le réseau (vmxnet3 ou e1000)${RST}
${YEL}  • GPU : ne pas cocher de GPU réel (VM)${RST}
${YEL}  • USB : USBInjectAll (pas USBToolBox pour Linux)${RST}
${YEL}══════════════════════════════════════════════════════════════${RST}

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

  # Localiser l'EFI généré
  OCS_EFI_DIR=$(find "${OCS_DIR}/Results" -maxdepth 2 -name "EFI" -type d 2>/dev/null | head -1)
  if [[ -z "${OCS_EFI_DIR}" ]]; then
    die "EFI introuvable dans ${OCS_DIR}/Results/. Lancez OpCore Simplify jusqu'au bout, puis relancez avec --skip-ocs."
  fi
  ok "EFI généré : ${OCS_EFI_DIR}"
  echo "${OCS_EFI_DIR}" > "${VM_DIR}/.ocs_efi_path"
}

# ── Création de l'image OpenCore (disque ESP) ─────────────────────────────────
build_opencore_img() {
  sep; log "Construction de l'image OpenCore (ESP 200 Mo)..."

  # ── Résoudre le chemin EFI (cache → recherche → saisie manuelle)
  local OCS_EFI_DIR=""

  # 1. Chemin sauvegardé
  local CACHED; CACHED=$(cat "${VM_DIR}/.ocs_efi_path" 2>/dev/null || true)
  if [[ -d "${CACHED}" ]]; then
    OCS_EFI_DIR="${CACHED}"
    ok "EFI depuis cache : ${OCS_EFI_DIR}"
  fi

  # 2. Recherche dynamique dans Results/
  if [[ -z "${OCS_EFI_DIR}" ]]; then
    OCS_EFI_DIR=$(find "${OCS_DIR}/Results" -maxdepth 4 -name "EFI" -type d 2>/dev/null | head -1 || true)
    if [[ -n "${OCS_EFI_DIR}" ]]; then
      ok "EFI trouvé : ${OCS_EFI_DIR}"
      echo "${OCS_EFI_DIR}" > "${VM_DIR}/.ocs_efi_path"
    fi
  fi

  # 3. Saisie manuelle
  if [[ -z "${OCS_EFI_DIR}" ]]; then
    warn "Aucun dossier EFI trouvé dans ${OCS_DIR}/Results/"
    warn "Lancez OpCore Simplify jusqu'au bout (Build OpenCore EFI) puis relancez."
    warn "Ou entrez le chemin manuellement (vide pour annuler) :"
    read -r -p "  Chemin vers le dossier EFI : " OCS_EFI_DIR
    [[ -d "${OCS_EFI_DIR}" ]] || die "Chemin invalide. Relancez OCS puis : bash $0 --skip-deps --skip-recovery"
    echo "${OCS_EFI_DIR}" > "${VM_DIR}/.ocs_efi_path"
  fi

  # Créer image FAT32 200 Mo
  run qemu-img create -f raw "${OPENCORE_IMG}" 200M
  # Partition GPT + ESP
  run sgdisk -Z -n 1:2048:411647 -t 1:EF00 -c 1:"EFI" "${OPENCORE_IMG}"

  # Monter via loop et formater
  local LOOP
  LOOP=$(losetup --find --partscan --show "${OPENCORE_IMG}")
  run mkfs.fat -F32 -n "EFI" "${LOOP}p1"

  local MNT; MNT=$(mktemp -d)
  run mount "${LOOP}p1" "${MNT}"
  run cp -r "${OCS_EFI_DIR}" "${MNT}/"
  sync
  run umount "${MNT}"
  rmdir "${MNT}"
  run losetup -d "${LOOP}"

  ok "Image OpenCore créée : ${OPENCORE_IMG}"
}

# ── Téléchargement du Recovery macOS ─────────────────────────────────────────
download_recovery() {
  sep; log "Téléchargement du Recovery macOS (${MACOS_VERSION})..."

  # Mapping version → identifiant Apple
  declare -A BOARD_IDS=(
    [sequoia]="Mac-7BA5B2DFE22DDD8C"
    [sonoma]="Mac-226CB3C6A851A671"
    [ventura]="Mac-4B682C642B45593E"
    [monterey]="Mac-FFE5EF870D7BA81A"
    [big-sur]="Mac-42FD25EABCABB274"
  )

  local BOARD_ID="${BOARD_IDS[${MACOS_VERSION}]:-}"
  [[ -n "$BOARD_ID" ]] || die "Version macOS inconnue : ${MACOS_VERSION}"

  local SCRIPT_DIR="${VM_DIR}/fetch-macOS"
  mkdir -p "${SCRIPT_DIR}"

  # Utiliser macrecovery.py (depuis OpenCorePkg) — plus fiable que gibMacOS
  if [[ ! -f "${SCRIPT_DIR}/macrecovery.py" ]]; then
    log "Téléchargement de macrecovery.py..."
    curl -fsSL \
      "https://raw.githubusercontent.com/acidanthera/OpenCorePkg/master/Utilities/macrecovery/macrecovery.py" \
      -o "${SCRIPT_DIR}/macrecovery.py"
  fi

  pushd "${SCRIPT_DIR}" > /dev/null
  log "Téléchargement du BaseSystem (peut prendre plusieurs minutes)..."
  python3 macrecovery.py \
    -b "${BOARD_ID}" \
    -m 00000000000000000 \
    download 2>&1 | tee "${VM_DIR}/macrecovery.log"
  popd > /dev/null

  # Convertir en image raw si nécessaire
  local CHUNKLIST="${SCRIPT_DIR}/com.apple.recovery.boot/BaseSystem.chunklist"
  local BASESYSTEM_DMG="${SCRIPT_DIR}/com.apple.recovery.boot/BaseSystem.dmg"

  if [[ -f "${BASESYSTEM_DMG}" ]]; then
    qemu-img convert -f dmg -O raw "${BASESYSTEM_DMG}" "${RECOVERY_IMG}" 2>/dev/null || \
      cp "${BASESYSTEM_DMG}" "${RECOVERY_IMG}"
    ok "Recovery image : ${RECOVERY_IMG}"
  else
    die "BaseSystem.dmg introuvable dans ${SCRIPT_DIR}/com.apple.recovery.boot/"
  fi
}

# ── Création du disque principal macOS ────────────────────────────────────────
create_macos_disk() {
  sep; log "Création du disque macOS (${DISK_SIZE})..."

  if [[ -f "${MACOS_DISK}" ]]; then
    warn "Le disque ${MACOS_DISK} existe déjà."
    read -r -p "Le recréer (perte des données) ? [o/N] " CONFIRM
    [[ "${CONFIRM,,}" == "o" ]] || { ok "Disque conservé."; return; }
  fi

  run qemu-img create -f qcow2 "${MACOS_DISK}" "${DISK_SIZE}"
  ok "Disque créé : ${MACOS_DISK} (${DISK_SIZE})"
}

# ── Génération du script de lancement QEMU ───────────────────────────────────
generate_launch_script() {
  sep; log "Génération du script de lancement QEMU..."

  # Détection du type d'accélération
  local ACCEL="kvm"
  # Si Xen dom0, on peut utiliser xen-hvm (nécessite xen-backend)
  if [[ -e /proc/xen/capabilities ]] && grep -q "control_d" /proc/xen/capabilities 2>/dev/null; then
    warn "Xen dom0 détecté. Utilisation de KVM via Xen HVM (kvm dans Xen dom0 nécessite xen-kvm)."
    # Dans un dom0 Xen, QEMU peut toujours utiliser /dev/kvm si xen-kvm est chargé
  fi

  local LAUNCH="${VM_DIR}/run-macos.sh"
  cat > "${LAUNCH}" <<LAUNCH
#!/usr/bin/env bash
# ─────────────────────────────────────────────────────────────
#  Lancement VM macOS ${MACOS_VERSION} — QEMU/KVM
#  Généré par setup-macos-vm.sh
# ─────────────────────────────────────────────────────────────
set -euo pipefail

VM_DIR="${VM_DIR}"
OPENCORE_IMG="${OPENCORE_IMG}"
MACOS_DISK="${MACOS_DISK}"
RECOVERY_IMG="${RECOVERY_IMG}"
OVMF_CODE="${OVMF_CODE}"
OVMF_VARS="\${VM_DIR}/OVMF_VARS.fd"

# Mode installation (1er démarrage) : inclure le Recovery
# Passer INSTALL_MODE=0 après installation
INSTALL_MODE="\${INSTALL_MODE:-1}"

EXTRA_DRIVES=""
if [[ "\$INSTALL_MODE" == "1" && -f "\${RECOVERY_IMG}" ]]; then
  EXTRA_DRIVES="-drive id=RecoveryDisk,if=none,file=\${RECOVERY_IMG},format=raw \\
    -device ide-hd,bus=sata.3,drive=RecoveryDisk"
  echo "[INFO] Mode installation : Recovery monté sur sata.3"
else
  echo "[INFO] Mode normal (INSTALL_MODE=0)"
fi

exec qemu-system-x86_64 \\
  -name "macOS-${MACOS_VERSION}" \\
  \\
  \`# ── Plateforme ────────────────────────────────────────────\` \\
  -machine q35,accel=${ACCEL},usb=on,vmport=off,smbios-entry-point-type=64 \\
  -cpu host,vendor=GenuineIntel,+sse3,+sse4.2,+avx2,+aes,+xsave,\\
kvm=on,vmware-cpuid-freq=on \\
  -smp cpus=${CPU_CORES},cores=${CPU_CORES},threads=1,sockets=1 \\
  -m ${RAM} \\
  \\
  \`# ── Firmware UEFI ─────────────────────────────────────────\` \\
  -drive if=pflash,format=raw,readonly=on,file=\${OVMF_CODE} \\
  -drive if=pflash,format=raw,file=\${OVMF_VARS} \\
  \\
  \`# ── OpenCore EFI ──────────────────────────────────────────\` \\
  -drive id=OpenCore,if=none,snapshot=off,format=raw,file=\${OPENCORE_IMG} \\
  -device ide-hd,bus=sata.0,drive=OpenCore \\
  \\
  \`# ── Disque macOS ──────────────────────────────────────────\` \\
  -drive id=MacHDD,if=none,file=\${MACOS_DISK},format=qcow2,cache=unsafe,discard=unmap \\
  -device ide-hd,bus=sata.1,drive=MacHDD \\
  \\
  \`# ── Recovery (mode install) ───────────────────────────────\` \\
  \${EXTRA_DRIVES} \\
  \\
  \`# ── USB 3.0 ───────────────────────────────────────────────\` \\
  -device qemu-xhci,id=usb \\
  -device usb-kbd \\
  -device usb-tablet \\
  \\
  \`# ── Réseau ────────────────────────────────────────────────\` \\
  -device vmxnet3,netdev=net0 \\
  -netdev user,id=net0 \\
  \\
  \`# ── Affichage ─────────────────────────────────────────────\` \\
  -device vmware-svga,vgamem_mb=128 \\
  -display sdl,gl=off \\
  \\
  \`# ── Audio ─────────────────────────────────────────────────\` \\
  -audiodev pa,id=snd0 \\
  -device ich9-intel-hda -device hda-duplex,audiodev=snd0 \\
  \\
  \`# ── Misc ──────────────────────────────────────────────────\` \\
  -no-shutdown \\
  -rtc base=localtime \\
  "\$@"
LAUNCH

  chmod +x "${LAUNCH}"
  ok "Script de lancement : ${LAUNCH}"

  # Script post-installation (sans recovery)
  local POST_INSTALL="${VM_DIR}/run-macos-installed.sh"
  cat > "${POST_INSTALL}" <<POSTINST
#!/usr/bin/env bash
# Lancer la VM après installation (sans Recovery)
INSTALL_MODE=0 exec "\$(dirname "\$0")/run-macos.sh" "\$@"
POSTINST
  chmod +x "${POST_INSTALL}"
  ok "Script post-install : ${POST_INSTALL}"
}

# ── Résumé et lancement ───────────────────────────────────────────────────────
print_summary() {
  sep
  echo -e "${BLD}${GRN}  VM macOS ${MACOS_VERSION} prête !${RST}"
  sep
  cat <<EOF

${BLD}Répertoire VM :${RST}   ${VM_DIR}
${BLD}Disque macOS  :${RST}   ${MACOS_DISK}
${BLD}OpenCore EFI  :${RST}   ${OPENCORE_IMG}
${BLD}Recovery      :${RST}   ${RECOVERY_IMG}
${BLD}RAM           :${RST}   ${RAM}
${BLD}CPUs          :${RST}   ${CPU_CORES}

${BLD}${YEL}Étapes suivantes :${RST}

  1. ${BLD}Première installation :${RST}
       bash ${VM_DIR}/run-macos.sh

  2. ${BLD}Dans OpenCore → sélectionner "Reset NVRAM"${RST} (premier démarrage)

  3. ${BLD}Dans le Recovery macOS :${RST}
       • Disk Utility → Effacer le disque (APFS, GUID)
       • Réinstaller macOS

  4. ${BLD}Après installation :${RST}
       bash ${VM_DIR}/run-macos-installed.sh
       # ou : INSTALL_MODE=0 bash ${VM_DIR}/run-macos.sh

${BLD}${YEL}Dépannage courant :${RST}

  • Écran noir au boot  → Dans OpenCore, vérifiez l'argument de boot -v (verbose)
  • Freeze ACPI         → Ajoutez boot-arg : igfxonln=1 ou -igfxnohdmi
  • Réseau absent       → vmxnet3 nécessite VMware Tools (dans macOS) ; 
                          ou remplacez par : -device e1000-82545em
  • Performance lente   → Vérifiez que KVM est actif : dmesg | grep kvm

${BLD}${CYA}OpCore Simplify — Mise à jour EFI :${RST}
  cd ${OCS_DIR} && python3 OpCore-Simplify.py
  # puis reconstruire l'image OpenCore :
  bash setup-macos-vm.sh --skip-deps --skip-recovery --macos ${MACOS_VERSION}

EOF
  sep
}

launch_vm() {
  sep; log "Lancement de la VM macOS en mode installation..."
  bash "${VM_DIR}/run-macos.sh"
}

# ═══════════════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════════════
sep
echo -e "${BLD}  macOS VM Setup — openSUSE Tumbleweed + QEMU/KVM${RST}"
echo -e "${BLD}  Version macOS cible : ${CYA}${MACOS_VERSION}${RST}"
sep

if [[ "$RUN_ONLY" -eq 1 ]]; then
  [[ -f "${VM_DIR}/run-macos.sh" ]] || die "Script de lancement introuvable. Lancez sans --run-only d'abord."
  launch_vm
  exit 0
fi

check_os

[[ "$SKIP_DEPS" -eq 0 ]] && install_deps || {
  # Détecter OVMF même si on skip les deps
  for path in /usr/share/qemu/ovmf-x86_64-4m-code.bin /usr/share/qemu/ovmf-x86_64-code.bin /usr/share/OVMF/OVMF_CODE.fd; do
    [[ -f "$path" ]] && { OVMF_CODE="$path"; break; }
  done
  for path in /usr/share/qemu/ovmf-x86_64-4m-vars.bin /usr/share/qemu/ovmf-x86_64-vars.bin /usr/share/OVMF/OVMF_VARS.fd; do
    [[ -f "$path" ]] && { OVMF_VARS="$path"; break; }
  done
  [[ -n "$OVMF_CODE" ]] || die "OVMF introuvable. Installez qemu-ovmf-x86_64."
}

prepare_dirs
[[ "$SKIP_OCS" -eq 0 ]]      && run_opcore_simplify
build_opencore_img
[[ "$SKIP_RECOVERY" -eq 0 ]] && download_recovery
create_macos_disk
generate_launch_script
print_summary

read -r -p "Lancer la VM maintenant ? [o/N] " START
[[ "${START,,}" == "o" ]] && launch_vm || ok "VM prête. Lancez manuellement : bash ${VM_DIR}/run-macos.sh"
