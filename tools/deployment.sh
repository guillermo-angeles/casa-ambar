DEPLOYMENT_READY=false
DEPLOYMENT_LOCKED=false
DEPLOYMENT_DIR=/config/.casa-ambar

save_deployment() {
  rscp "$WORK/deployment.json" "root@${HA_HOST}:${DEPLOYMENT_DIR}/deployments/${STAMP}.json.tmp" || return 1
  rssh "chmod 600 '${DEPLOYMENT_DIR}/deployments/${STAMP}.json.tmp' && mv '${DEPLOYMENT_DIR}/deployments/${STAMP}.json.tmp' '${DEPLOYMENT_DIR}/deployments/${STAMP}.json'" || return 1
}

begin_deployment() {
  rssh 'mkdir /tmp/casa-ambar-deploy.lock' || die "hay otro despliegue o un bloqueo pendiente en /tmp/casa-ambar-deploy.lock"
  DEPLOYMENT_LOCKED=true
  rssh "test ! -f '${DEPLOYMENT_DIR}/incomplete'" || die "hay un despliegue incompleto; revisa su registro antes de continuar"
  rssh "umask 077; mkdir -p '${DEPLOYMENT_DIR}/deployments'; if test -f '${DEPLOYMENT_DIR}/current.json'; then cat '${DEPLOYMENT_DIR}/current.json'; else printf '%s\n' '{\"schema\":1,\"scopes\":{}}'; fi" > "$WORK/previous.json"
  BACKUP_NAME="pre-casa-ambar-${RELEASE_TAG#v}-${STAMP}"
  log "Copia completa previa a ${RELEASE_TAG} (puede tardar)"
  rssh "ha backups new --name 'pre-casa-ambar-${RELEASE_TAG#v}-${STAMP}' --no-progress --raw-json" > "$WORK/backup.json" || die "fallo la copia; no se han desplegado archivos"
  "${PY[@]}" "$ROOT/tools/release.py" prepare "$WORK/source.json" "$WORK/previous.json" "$WORK/backup.json" -- "${MODE:-configuration}" "$STAMP" > "$WORK/deployment.json" || die "no se pudo verificar la copia ni preparar el registro"
  save_deployment || die "no se pudo guardar el registro previo; no se desplegaran archivos"
  DEPLOYMENT_READY=true
  rssh "umask 077; printf '%s\n' '$STAMP' > '${DEPLOYMENT_DIR}/incomplete'" || die "no se pudo registrar el inicio del cambio"
  printf 'Registro de despliegue: %s/deployments/%s.json\n' "$DEPLOYMENT_DIR" "$STAMP"
}

finish_deployment() {
  local code="$1" status=failed
  trap - EXIT
  if $DEPLOYMENT_READY; then
    [[ "$code" -eq 0 ]] && status=applied
    if ! "${PY[@]}" "$ROOT/tools/release.py" finish "$WORK/deployment.json" "$status" > "$WORK/current.json" || ! save_deployment; then
      printf 'No se pudo finalizar el registro del despliegue %s.\n' "$STAMP" >&2
      code=1
    elif [[ "$status" == applied ]]; then
      if ! rscp "$WORK/current.json" "root@${HA_HOST}:${DEPLOYMENT_DIR}/current.json.tmp" || ! rssh "chmod 600 '${DEPLOYMENT_DIR}/current.json.tmp' && mv '${DEPLOYMENT_DIR}/current.json.tmp' '${DEPLOYMENT_DIR}/current.json' && rm -f '${DEPLOYMENT_DIR}/incomplete'"; then
        printf 'Despliegue aplicado, pero no se pudo actualizar current.json. Revisa el registro %s.\n' "$STAMP" >&2
        code=1
      fi
    fi
    local log_dir="${CASA_DEPLOY_LOG_DIR:-$HOME/.local/share/casa-ambar/deployments}"
    if ! mkdir -p "$log_dir" || ! (umask 077; cat "$WORK/deployment.json" > "$log_dir/$STAMP.json"); then
      printf 'No se pudo guardar la copia local del registro.\n' >&2
      code=1
    fi
  fi
  if $DEPLOYMENT_LOCKED; then
    rssh 'rmdir /tmp/casa-ambar-deploy.lock' >/dev/null 2>&1 || true
  fi
  rm -rf "$WORK"
  exit "$code"
}
