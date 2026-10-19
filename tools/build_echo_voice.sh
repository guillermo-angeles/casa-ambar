#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
OUT="$ROOT/test/echo-voz/build"
SOURCE="$OUT/source"
UPSTREAM=8f39f704319b802d7fcb094518b7563e2b660a1c
mkdir -p "$OUT"
if [[ ! -d "$SOURCE/.git" ]]; then
  git init "$SOURCE"
  git -C "$SOURCE" remote add origin https://github.com/HuskerMinion/techo5.git
  git -C "$SOURCE" fetch --depth 1 origin "$UPSTREAM"
  git -C "$SOURCE" checkout --detach FETCH_HEAD
fi
[[ "$(git -C "$SOURCE" rev-parse HEAD)" == "$UPSTREAM" ]] || { echo 'Version de fuentes inesperada' >&2; exit 1; }
if git -C "$SOURCE" apply --check "$ROOT/firmware/techo5/casa-voice.patch" 2>/dev/null; then
  git -C "$SOURCE" apply "$ROOT/firmware/techo5/casa-voice.patch"
else
  git -C "$SOURCE" apply --reverse --check "$ROOT/firmware/techo5/casa-voice.patch"
fi
docker run --rm \
  -v "$SOURCE:/src" -v "$ROOT:/casa" \
  -v ha-casa-go-mod:/go/pkg/mod -v ha-casa-go-build:/root/.cache/go-build \
  -e CASA_VOICE_BACKGROUND=/casa/test/echo-v5/casa.png \
  -e CASA_VOICE_OUTPUT=/casa/test/echo-voz/native \
  -w /src/echod golang:1.26 \
  sh -c 'go test ./internal/feature/... ./internal/hardware/... ./internal/config ./internal/update/... && GOOS=linux GOARCH=arm GOARM=7 CGO_ENABLED=0 go build -trimpath -ldflags "-s -w -X github.com/HuskerMinion/techo5/echod/internal/layout.Version=v1.2.22 -X github.com/HuskerMinion/techo5/echod/internal/layout.GitCommit=casa-voz-2" -o /casa/test/echo-voz/techo5-casa-arm ./cmd/echod'
shasum -a 256 "$ROOT/test/echo-voz/techo5-casa-arm"
