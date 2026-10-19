#!/bin/sh
set -eu

OPTIONS=/data/options.json
export HA_URL="$(jq -r '.ha_url // empty' "$OPTIONS")"
export HA_TOKEN="$(jq -r '.ha_token // empty' "$OPTIONS")"
export DASHCAST_KEY="$(jq -r '.dashcast_key // empty' "$OPTIONS")"
export LISTEN=:9555

exec setpriv --reuid=65534 --regid=65534 --clear-groups /usr/local/bin/dashcast
