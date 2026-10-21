#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
if [[ ${1:-} == --help ]]; then
  printf 'Uso: tools/rollback.sh --deployment AAAAMMDD-HHMMSS | --echo-voice | --voice-stt --version vX.Y.Z\n'
  exit 0
fi
MODE="${1:-}"
case "$MODE" in
  --deployment) [[ $# -eq 2 && "$2" =~ ^[0-9]{8}-[0-9]{6}$ ]] || exit 1 ;;
  --echo-voice) [[ $# -eq 1 ]] || exit 1 ;;
  --voice-stt) [[ $# -eq 3 && "$2" == --version ]] || exit 1 ;;
  *) echo 'Selecciona un despliegue concreto; consulta --help' >&2; exit 1 ;;
esac
source "$ROOT/tools/lib.sh"
[[ -f "$SSH_KEY" ]] || die "no existe la clave SSH configurada"
WORK="$(mktemp -d)"
trap 'rm -rf "$WORK"' EXIT

if [[ "$MODE" == --deployment ]]; then
  DEPLOYMENT="$2"
  rssh "cat '/config/.casa-ambar/deployments/${DEPLOYMENT}.json'" > "$WORK/deployment.json" || die "registro de despliegue no disponible"
  SLUG="$("${PY[@]}" "$ROOT/tools/release.py" rollback-info "$WORK/deployment.json" "$DEPLOYMENT")" || die "no se pudo verificar el registro; no se restaurara ninguna copia"
  printf 'Se restaurara la copia COMPLETA de HA %s anterior al despliegue %s.\n' "$SLUG" "$DEPLOYMENT"
  printf 'Se perderan los cambios posteriores a esa copia. El Echo no forma parte de la copia de HA.\n'
  "${PY[@]}" - "$WORK/deployment.json" <<'PY'
import json, sys
record = json.load(open(sys.argv[1]))
print('Version del despliegue:', record['source']['tag'])
scopes = record['previous']['scopes']
print('Versiones anteriores:', ', '.join(key + '=' + value['tag'] for key, value in scopes.items()) or 'sin registro previo')
PY
elif [[ "$MODE" == --voice-stt ]]; then
  printf 'Casa volvera a Whisper local mediante %s; Claude y Piper se conservan.\n' "$3"
else
  printf 'Se retirara el montaje temporal del Echo y se reiniciara su ejecutable persistente; sus ajustes se conservan.\n'
fi
read -r -p 'Escribe REVERTIR para continuar: ' answer
[[ "$answer" == REVERTIR ]] || die "cancelado"

if [[ "$MODE" == --echo-voice ]]; then
  ssh -i "$SSH_KEY" -o IdentitiesOnly=yes -o BatchMode=yes -o ConnectTimeout=5 "root@${ECHO_HOST:?Configura ECHO_HOST}" \
    'umount -l /usr/local/bin/techo5 && killall techo5'
  printf 'Montaje temporal retirado. Verifica el Echo y su reconexion.\n'
elif [[ "$MODE" == --voice-stt ]]; then
  echo DESPLEGAR | "$ROOT/tools/deploy.sh" --version "$3" --voice-whisper
else
  rssh "ha backups restore '$SLUG' --no-progress" || die "restauracion no confirmada; revisa el estado y la copia en la interfaz HA"
  printf 'Supervisor acepto la restauracion de %s. Verifica el arranque y las versiones en HA antes de otro despliegue.\n' "$SLUG"
fi
