#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
docker compose down >/dev/null 2>&1 || true
./prepare.sh
docker compose run --rm --no-deps --entrypoint "" homeassistant python -m homeassistant --script check_config -c /config
docker compose up -d
sleep 30
docker exec -i casa-ambar-public-test python3 - < ../groq/test_stt.py
docker exec -i casa-ambar-public-test python3 - < e2e.py
grep -E "WARNING|ERROR" config/home-assistant.log || true
docker compose stop
