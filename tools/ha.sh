#!/bin/zsh
set -eu
: "${HA_URL:?Configura HA_URL}"
m=$1; p=$2; d=${3:-}
args=(-sS --fail-with-body --max-time 600 -X "$m" -H @- "${HA_URL%/}$p")
[[ -n "$d" ]] && args+=(-d "$d")
token="$(security find-generic-password -s "${HA_TOKEN_SERVICE:-casa-ambar-token}" -w)"
[[ -n "$token" ]] || exit 1
printf 'Authorization: Bearer %s\nContent-Type: application/json\n' "$token" | /usr/bin/curl "${args[@]}"
