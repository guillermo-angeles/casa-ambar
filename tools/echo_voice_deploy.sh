#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
[[ ${1:-} =~ ^[0-9]{8}-[0-9]{6}$ ]] || { echo 'Usar tools/deploy.sh --version vX.Y.Z --echo-voice' >&2; exit 1; }
STAMP="$1"
BINARY="$ROOT/test/echo-voz/techo5-casa-arm"
KEY="${SSH_KEY:-$HOME/.ssh/id_ed25519}"
ECHO_HOST="${ECHO_HOST:?Configura ECHO_HOST}"
SSH_ECHO=(ssh -i "$KEY" -o IdentitiesOnly=yes -o BatchMode=yes -o ConnectTimeout=5 "root@$ECHO_HOST")
SCP_ECHO=(scp -O -i "$KEY" -o IdentitiesOnly=yes -o BatchMode=yes -o ConnectTimeout=5)
ORIGINAL="${ECHO_EXPECTED_SHA256:?Configura ECHO_EXPECTED_SHA256 tras verificar tu ejecutable}"
[[ "$ORIGINAL" =~ ^[a-f0-9]{64}$ ]] || { echo "Hash SHA256 no valido" >&2; exit 1; }
[[ -f "$BINARY" ]] || { echo 'Compilar primero con tools/build_echo_voice.sh' >&2; exit 1; }
CURRENT="$("${SSH_ECHO[@]}" 'sha256sum /usr/local/bin/techo5' | awk '{print $1}')"
[[ "$CURRENT" == "$ORIGINAL" ]] || { echo 'El ejecutable del Echo ha cambiado; revisar antes de sustituirlo' >&2; exit 1; }
BACKUP="${CASA_BACKUP_DIR:-$HOME/.local/share/casa-ambar/backups}/pre-casa-voice-$STAMP"
mkdir -m 700 -p "$BACKUP"
"${SCP_ECHO[@]}" "root@$ECHO_HOST:/usr/local/bin/techo5" "$BACKUP/techo5-anterior"
chmod 600 "$BACKUP/techo5-anterior"
[[ "$(shasum -a 256 "$BACKUP/techo5-anterior" | awk '{print $1}')" == "$CURRENT" ]] || exit 1
REMOTE="/tmp/techo5-casa-$STAMP"
"${SCP_ECHO[@]}" "$BINARY" "root@$ECHO_HOST:$REMOTE"
EXPECTED="$(shasum -a 256 "$BINARY" | awk '{print $1}')"
ACTUAL="$("${SSH_ECHO[@]}" "sha256sum '$REMOTE'" | awk '{print $1}')"
[[ "$EXPECTED" == "$ACTUAL" ]] || { echo 'Copia no verificada' >&2; exit 1; }
"${SSH_ECHO[@]}" "set -e; chmod 755 '$REMOTE'; cp -p /usr/local/bin/techo5 '/tmp/techo5-casa-previous-$STAMP'; if grep -q ' /usr/local/bin/techo5 ' /proc/mounts; then umount -l /usr/local/bin/techo5; fi; if ! mount --bind '$REMOTE' /usr/local/bin/techo5; then mount --bind '/tmp/techo5-casa-previous-$STAMP' /usr/local/bin/techo5; exit 1; fi; killall techo5"
sleep 8
if ! "${SSH_ECHO[@]}" "test -n \"\$(pidof techo5)\" && test \"\$(sha256sum /proc/\$(pidof techo5)/exe | cut -d ' ' -f 1)\" = '$EXPECTED'"; then
  "${SSH_ECHO[@]}" 'umount -l /usr/local/bin/techo5 && killall techo5' || true
  echo 'No se pudo verificar el proceso; se ha intentado volver al ejecutable original' >&2
  exit 1
fi
printf 'Diseño de voz en prueba reversible. Copia: %s. Un reinicio del Echo recupera el ejecutable original.\n' "$BACKUP"
