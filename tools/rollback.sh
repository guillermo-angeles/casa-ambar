#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
source "$ROOT/tools/lib.sh"
CFG="$ROOT/config"
[[ $# -eq 0 || ( $# -eq 1 && ( "${1:-}" == "--echo-voice" || "${1:-}" == "--voice-stt" ) ) ]] || die "opcion no valida"

[[ -f "$SSH_KEY" ]] || die "no existe la clave SSH $SSH_KEY"

if [[ ${1:-} == "--voice-stt" ]]; then
  printf 'Casa volvera a transcribir con Whisper local; se conservaran Claude y Piper.\n'
elif [[ ${1:-} == "--echo-voice" ]]; then
  printf 'Se retirara el binario temporal del Echo y se reiniciara su proceso; sus ajustes se conservan.\n'
else
  printf 'Se revertira el despliegue de Casa Ambar en %s.\n' "$HA_HOST"
fi
read -r -p "Escribe REVERTIR para continuar: " answer
[[ "$answer" == "REVERTIR" ]] || die "cancelado"

if [[ ${1:-} == "--echo-voice" ]]; then
  ssh -i "$SSH_KEY" -o IdentitiesOnly=yes -o BatchMode=yes -o ConnectTimeout=5 "root@${ECHO_HOST:?Configura ECHO_HOST}" \
    'umount -l /usr/local/bin/techo5 && killall techo5'
  printf 'Ejecutable original restaurado. Esperar la reconexion del Echo.\n'
  exit 0
fi

if [[ ${1:-} == "--voice-stt" ]]; then
  echo DESPLEGAR | "$ROOT/tools/deploy.sh" --voice-whisper
  exit 0
fi

load_token
rssh true || die "SSH no disponible: abre el puerto 22 del add-on Terminal & SSH"

backup="$(rssh "ls -1 /config/configuration.yaml.pre-casa-* 2>/dev/null | sort | head -n 1" || true)"
[[ -n "$backup" ]] || die "no hay copia configuration.yaml.pre-casa-* en /config"

log "Restaurando configuration.yaml desde $(basename "$backup")"
rssh "cp -p '${backup}' /config/configuration.yaml"

log "Borrando ficheros desplegados"
for f in "$CFG"/packages/*.yaml; do rssh "rm -f '/config/packages/$(basename "$f")'"; done
rssh "rm -f /config/themes/ambar.yaml"
for f in "$CFG"/dashboards/*.yaml; do rssh "rm -f '/config/dashboards/$(basename "$f")'"; done

log "Comprobando la configuracion restaurada"
rssh "ha core check" >/dev/null 2>&1 || die "la configuracion restaurada no pasa la comprobacion; revisa a mano"

log "Reiniciando Home Assistant"
api POST /api/services/homeassistant/restart >/dev/null || true
wait_for_down
wait_for_ha 72 || die "Home Assistant no responde tras el reinicio"

log "Reactivando automatizaciones antiguas"
for id in "${OLD_AUTOMATIONS[@]}"; do
  if automation_exists "$id"; then
    automation_service turn_on "$id"
    printf 'activada: %s\n' "$id"
  else
    printf 'no encontrada: %s\n' "$id"
  fi
done

printf '\nRollback completado. La copia completa pre-casa-ambar-* sigue en Ajustes > Sistema > Copias de seguridad.\n'
