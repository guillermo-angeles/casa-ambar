HA_HOST="${HA_HOST:?Configura HA_HOST}"
HA_URL="${HA_URL:?Configura HA_URL}"
HA_TOKEN_SERVICE="${HA_TOKEN_SERVICE:-casa-ambar-token}"
SSH_KEY="${SSH_KEY:-$HOME/.ssh/id_ed25519}"
SSH_OPTS=(-i "$SSH_KEY" -o IdentitiesOnly=yes -o BatchMode=yes -o ConnectTimeout=10 -o StrictHostKeyChecking=accept-new)
OLD_AUTOMATIONS=()
MARK_BEGIN="# >>> casa-ambar"
MARK_END="# <<< casa-ambar"
CURL=/usr/bin/curl
PY=(/usr/bin/python3 -I)

die() { printf 'ERROR: %s\n' "$*" >&2; exit 1; }
log() { printf '==> %s\n' "$*"; }

rssh() { ssh "${SSH_OPTS[@]}" "root@${HA_HOST}" "$@"; }
rscp() { scp -q "${SSH_OPTS[@]}" "$@"; }

load_token() {
  HA_TOKEN="$(security find-generic-password -s "$HA_TOKEN_SERVICE" -w 2>/dev/null)" || die "no se pudo leer el token del Llavero"
  [[ -n "$HA_TOKEN" ]] || die "token vacio"
}

api() {
  local method="$1" path="$2" data="${3:-}"
  local args=(-sS --max-time 30 -X "$method" -K <(printf 'header = "Authorization: Bearer %s"\n' "$HA_TOKEN") -H 'Content-Type: application/json')
  [[ -n "$data" ]] && args+=(-d "$data")
  "$CURL" "${args[@]}" "${HA_URL}${path}"
}

api_code() {
  "$CURL" -s -o /dev/null -w '%{http_code}' --max-time 5 -K <(printf 'header = "Authorization: Bearer %s"\n' "$HA_TOKEN") "${HA_URL}$1" 2>/dev/null || true
}

wait_for_ha() {
  local tries="${1:-60}" i code
  for ((i = 0; i < tries; i++)); do
    code="$(api_code /api/)"
    [[ "$code" == "200" ]] && return 0
    sleep 5
  done
  return 1
}

wait_for_down() {
  local i code
  for ((i = 0; i < 12; i++)); do
    code="$(api_code /api/)"
    [[ "$code" != "200" ]] && return 0
    sleep 5
  done
  return 0
}

automation_service() {
  local action="$1" id="$2" body
  body="$("${PY[@]}" -c 'import json,sys; print(json.dumps({"entity_id": "automation."+sys.argv[1]}))' "$id")"
  api POST "/api/services/automation/${action}" "$body" >/dev/null
}

automation_exists() {
  [[ "$(api_code "/api/states/automation.$1")" == "200" ]]
}
