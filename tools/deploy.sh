#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
if [[ ${1:-} == --help ]]; then
  printf 'Uso: tools/deploy.sh --version vX.Y.Z [--check|--dashcast-only|--echo-camera|--voice-apps|--voice-setup|--groq-stt|--echo-voice|--voice-groq|--voice-whisper|--voice-instructions]\n'
  exit 0
fi
[[ ${1:-} == --version && $# -ge 2 && $# -le 3 ]] || { echo 'Indica --version vX.Y.Z; consulta --help' >&2; exit 1; }
RELEASE_TAG="$2"
MODE="${3:-}"
case "$MODE" in
  ""|--check|--dashcast-only|--echo-camera|--voice-apps|--voice-setup|--groq-stt|--echo-voice|--voice-groq|--voice-whisper|--voice-instructions) ;;
  *) echo 'Opcion no valida' >&2; exit 1 ;;
esac
if [[ "$MODE" == --echo-voice ]]; then
  SOURCE_MANIFEST="$(/usr/bin/python3 -I "$ROOT/tools/release.py" verify "$RELEASE_TAG" --native)" || exit 1
else
  SOURCE_MANIFEST="$(/usr/bin/python3 -I "$ROOT/tools/release.py" verify "$RELEASE_TAG")" || exit 1
fi
if [[ "$MODE" == --check ]]; then
  printf '%s\n' "$SOURCE_MANIFEST"
  exit 0
fi
source "$ROOT/tools/lib.sh"
source "$ROOT/tools/deployment.sh"
set -- "$MODE"
DASHCAST_ONLY=false
[[ ${1:-} == "--dashcast-only" ]] && DASHCAST_ONLY=true
ECHO_CAMERA=false
[[ ${1:-} == "--echo-camera" ]] && ECHO_CAMERA=true
VOICE_APPS=false
[[ ${1:-} == "--voice-apps" ]] && VOICE_APPS=true
VOICE_SETUP=false
[[ ${1:-} == "--voice-setup" ]] && VOICE_SETUP=true
GROQ_STT=false
[[ ${1:-} == "--groq-stt" ]] && GROQ_STT=true
ECHO_VOICE=false
[[ ${1:-} == "--echo-voice" ]] && ECHO_VOICE=true
CFG="$ROOT/config"
STAMP="$(date +%Y%m%d-%H%M%S)"
REMOTE_BACKUP="/config/configuration.yaml.pre-casa-${STAMP}"
WORK="$(mktemp -d)"
trap 'finish_deployment $?' EXIT
printf '%s\n' "$SOURCE_MANIFEST" > "$WORK/source.json"

[[ -f "$CFG/configuration.snippet.yaml" ]] || die "falta configuration.snippet.yaml"
[[ -f "$SSH_KEY" ]] || die "no existe la clave SSH $SSH_KEY"

printf 'Version seleccionada: %s\n' "$RELEASE_TAG"
if [[ ${1:-} == "--voice-instructions" ]]; then
  printf 'Se actualizaran las instrucciones de Claude con copia y check, sin cambiar el pipeline ni reiniciar HA.\n'
elif [[ ${1:-} == "--voice-groq" || ${1:-} == "--voice-whisper" ]]; then
  printf 'Se cambiara solo la transcripcion de Casa, con copia completa y check, sin reiniciar HA.\n'
elif $ECHO_VOICE; then
  [[ -f "$ROOT/test/echo-voz/techo5-casa-arm" ]] || die "compilar primero con tools/build_echo_voice.sh"
  printf 'Se probara el diseño de voz con copia completa y binario reversible del Echo, conservando sus ajustes.\n'
elif $GROQ_STT; then
  printf 'Se instalara el adaptador Groq con copia completa, check y reinicio de HA, sin cambiar el pipeline.\n'
elif $VOICE_SETUP; then
  printf 'Se configurara el asistente Casa y se asignara al Echo tras verificar el agente, con copia completa.\n'
elif $VOICE_APPS; then
  printf 'Se instalaran Whisper y Piper con copia completa, sin reiniciar HA ni cambiar el asistente del Echo.\n'
elif $DASHCAST_ONLY; then
  printf 'Se reconstruira y reiniciara dashcast en %s, con copia completa y del codigo anterior.\n' "$HA_HOST"
else
  printf 'Se desplegara config/ en la instancia real de Home Assistant (%s).\n' "$HA_HOST"
  printf 'Incluye copia de seguridad completa y reinicio; revisa los paquetes de ejemplo antes de desplegar.\n'
fi
read -r -p "Escribe DESPLEGAR para continuar: " answer
[[ "$answer" == "DESPLEGAR" ]] || die "cancelado"

load_token

log "Comprobando acceso a la API y a SSH"
[[ "$(api_code /api/)" == "200" ]] || die "la API no responde o el token no es valido"
rssh true || die "SSH no disponible: abre el puerto 22 del add-on Terminal & SSH"

begin_deployment

if [[ ${1:-} == "--voice-instructions" ]]; then
  rssh "ha core check" >/dev/null || die "configuracion no valida; no se han cambiado las instrucciones"
  "${PY[@]}" "$ROOT/tools/voice_setup.py" --instructions-only || die "no se confirmaron las instrucciones"
  printf 'Copia completa HA: %s.\n' "$BACKUP_NAME"
  exit 0
fi

if [[ ${1:-} == "--voice-groq" || ${1:-} == "--voice-whisper" ]]; then
  rssh "ha core check" >/dev/null || die "configuracion no valida; no se ha cambiado STT"
  ENGINE=stt.casa_groq_stt
  [[ ${1:-} == "--voice-whisper" ]] && ENGINE=stt.faster_whisper
  "${PY[@]}" "$ROOT/tools/voice_setup.py" --stt-engine "$ENGINE" || die "revisar el estado del pipeline antes de continuar"
  printf 'Copia completa HA: %s.\n' "$BACKUP_NAME"
  exit 0
fi

if $ECHO_VOICE; then
  rssh "ha core check" >/dev/null || die "configuracion no valida; no se ha modificado el Echo"
  "$ROOT/tools/echo_voice_deploy.sh" "$STAMP"
  printf 'Copia completa HA: %s.\n' "$BACKUP_NAME"
  exit 0
fi

if $GROQ_STT; then
  log "Comprobando la configuracion antes de instalar Groq"
  rssh "ha core check" >/dev/null || die "configuracion no valida; no se ha instalado Groq"
  rssh "mkdir -p /config/custom_components; if test -d /config/custom_components/casa_groq_stt; then tar -czf /config/casa-groq-stt-pre-${STAMP}.tgz -C /config/custom_components casa_groq_stt; fi"
  rscp -r "$ROOT/custom_components/casa_groq_stt" "root@${HA_HOST}:/config/custom_components/"
  rssh "ha core check" >/dev/null || die "fallo la comprobacion; revisar Groq antes de reiniciar"
  api POST /api/services/homeassistant/restart >/dev/null || true
  wait_for_down
  wait_for_ha 72 || die "HA no responde; revisar copia pre-casa-ambar-${RELEASE_TAG#v}-${STAMP}"
  printf '\nAdaptador Groq instalado. Copia completa: %s. Pipeline conservado.\n' "$BACKUP_NAME"
  exit 0
fi

if $VOICE_APPS || $VOICE_SETUP; then
  log "Comprobando la configuracion antes de instalar voz"
  rssh "ha core check" >/dev/null || die "configuracion no valida; no se han instalado apps"
  "${PY[@]}" "$ROOT/tools/voice_apps.py" || die "preparacion de voz incompleta; revisar apps sin borrar ni desinstalar"
  if $VOICE_SETUP; then
    "${PY[@]}" "$ROOT/tools/voice_setup.py" || die "asistente de voz incompleto; revisar el ultimo paso confirmado"
    printf '\nAsistente Casa configurado. Copia completa: %s.\n' "$BACKUP_NAME"
    exit 0
  fi
  printf '\nApps de voz preparadas. Copia completa: %s. El asistente del Echo no se ha cambiado.\n' "$BACKUP_NAME"
  exit 0
fi

if $ECHO_CAMERA; then
  "${PY[@]}" "$ROOT/tools/echo_camera_access.py" --install-secret || die "no se pudo preparar el secreto privado de la camara"
fi

if $DASHCAST_ONLY; then
  APP_BACKUP="/config/casa-dashcast-source-pre-${STAMP}.tgz"
  log "Guardando el codigo anterior de dashcast"
  rssh "tar -czf '${APP_BACKUP}' -C /local_apps casa_dashcast" || die "fallo la copia del codigo; no se ha tocado nada"
  log "Copiando y reconstruyendo dashcast"
  rscp -r "$ROOT/apps/dashcast/." "root@${HA_HOST}:/local_apps/casa_dashcast/"
  rssh "ha store reload" >/dev/null
  APP_OPERATION="$(rssh "ha apps info local_casa_dashcast --raw-json" | "${PY[@]}" -c 'import json,sys; d=json.load(sys.stdin); d=d.get("data",d); print("update" if d.get("version_latest") and d.get("version") != d["version_latest"] else "rebuild")')"
  rssh "ha apps ${APP_OPERATION} local_casa_dashcast" || die "fallo la reconstruccion; codigo anterior en ${APP_BACKUP}"
  rssh "ha apps restart local_casa_dashcast" || die "dashcast no se pudo reiniciar"
  printf '\nDashcast desplegado. Copia completa: %s. Codigo anterior: %s\n' "$BACKUP_NAME" "$APP_BACKUP"
  exit 0
fi

log "Copiando ficheros"
rssh "mkdir -p /config/packages /config/themes /config/dashboards /config/www"
rscp "$CFG"/packages/*.yaml "root@${HA_HOST}:/config/packages/"
rscp "$CFG/themes/ambar.yaml" "root@${HA_HOST}:/config/themes/"
rscp "$CFG"/dashboards/*.yaml "root@${HA_HOST}:/config/dashboards/"
rscp -r "$CFG/www/." "root@${HA_HOST}:/config/www/"

log "Fusionando configuration.yaml"
rssh "cp -p /config/configuration.yaml '${REMOTE_BACKUP}'"
rscp "root@${HA_HOST}:/config/configuration.yaml" "$WORK/configuration.yaml"
"${PY[@]}" - "$WORK/configuration.yaml" "$CFG/configuration.snippet.yaml" "$MARK_BEGIN" "$MARK_END" <<'PYEOF'
import re, sys
cfg_path, snip_path, begin, end = sys.argv[1:5]
cfg = open(cfg_path, encoding="utf-8").read()
snippet = open(snip_path, encoding="utf-8").read().strip("\n")
block = f"{begin}\n{snippet}\n{end}\n"
pattern = re.compile(re.escape(begin) + r".*?" + re.escape(end) + r"\n?", re.S)
if pattern.search(cfg):
    cfg = pattern.sub(lambda _: block, cfg)
else:
    if cfg and not cfg.endswith("\n"):
        cfg += "\n"
    cfg += "\n" + block
open(cfg_path, "w", encoding="utf-8").write(cfg)
PYEOF
rscp "$WORK/configuration.yaml" "root@${HA_HOST}:/config/configuration.yaml"

log "Comprobando la configuracion"
if ! check_out="$(rssh "ha core check" 2>&1)"; then
  printf '%s\n' "$check_out" | tail -n 30 >&2
  rssh "cp -p '${REMOTE_BACKUP}' /config/configuration.yaml"
  die "la comprobacion fallo; configuration.yaml restaurado"
fi

log "Reiniciando Home Assistant"
api POST /api/services/homeassistant/restart >/dev/null || true
wait_for_down
wait_for_ha 72 || die "Home Assistant no responde tras el reinicio; revisa la instancia (rollback: tools/rollback.sh)"

log "Desactivando automatizaciones antiguas"
disabled=()
missing=()
for id in "${OLD_AUTOMATIONS[@]}"; do
  if automation_exists "$id"; then
    automation_service turn_off "$id"
    disabled+=("$id")
  else
    missing+=("$id")
  fi
done

printf '\n== Resumen ==\n'
printf 'Copia completa:        %s\n' "$BACKUP_NAME"
printf 'configuration.yaml:    fusionado (copia en %s)\n' "$REMOTE_BACKUP"
printf 'Ficheros copiados:     %s paquetes, tema ambar, %s dashboards\n' "$(ls "$CFG"/packages/*.yaml | wc -l | tr -d ' ')" "$(ls "$CFG"/dashboards/*.yaml | wc -l | tr -d ' ')"
printf 'Automatizaciones off:  %s\n' "${disabled[*]:-ninguna}"
[[ ${#missing[@]} -gt 0 ]] && printf 'No encontradas:        %s\n' "${missing[*]}"
printf 'Siguiente paso:        docs/DESPLIEGUE.md\n'
