import json
from pathlib import Path
import subprocess
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[2]
HARNESS = r'''
set -euo pipefail
PY=(/usr/bin/python3 -I)
MODE=--voice-instructions
STAMP=20261021-120000
RELEASE_TAG=v0.1.0
HA_HOST=ha.invalid
rssh() {
  if [[ "$1" == 'ha backups new '* ]]; then
    printf '%s\n' "$BACKUP_JSON"
  else
    local command="${1//\/config\/.casa-ambar/$REMOTE}"
    command="${command//\/tmp\/casa-ambar-deploy.lock/$REMOTE_LOCK}"
    /bin/bash -c "$command"
  fi
}
rscp() {
  local target="${2#root@ha.invalid:}"
  target="${target//\/config\/.casa-ambar/$REMOTE}"
  [[ "${FAIL_CURRENT:-0}" == 0 || "$target" != */current.json.tmp ]] || return 1
  cp "$1" "$target"
}
die() { printf '%s\n' "$*" >&2; exit 1; }
log() { :; }
source "$ROOT/tools/deployment.sh"
trap 'finish_deployment $?' EXIT
begin_deployment
exit "$FINAL_CODE"
'''


class DeploymentLifecycleTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.remote = self.root / "remote"
        self.remote.mkdir()
        self.work = self.root / "work"
        self.work.mkdir()
        self.previous = {"schema": 1, "scopes": {"configuration": {"tag": "v0.0.1"}}}
        (self.remote / "current.json").write_text(json.dumps(self.previous))
        (self.work / "source.json").write_text(json.dumps({"version": "0.1.0", "tag": "v0.1.0", "commit": "a" * 40, "components": {"card": "2.1.2"}}))

    def run_deployment(self, code="0", backup=None, fail_current="0"):
        env = {"PATH": "/usr/bin:/bin", "ROOT": str(ROOT), "WORK": str(self.work), "REMOTE": str(self.remote), "REMOTE_LOCK": str(self.root / "lock"), "CASA_DEPLOY_LOG_DIR": str(self.root / "logs"), "FINAL_CODE": code, "FAIL_CURRENT": fail_current, "BACKUP_JSON": json.dumps(backup or {"result": "ok", "data": {"slug": "a1b2c3d4"}})}
        return subprocess.run(["/bin/bash", "-c", HARNESS], env=env, capture_output=True, text=True)

    def record(self):
        return json.loads((self.remote / "deployments/20261021-120000.json").read_text())

    def test_success_records_partial_change_and_clears_marker_and_lock(self):
        result = self.run_deployment()
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(self.record()["status"], "applied")
        current = json.loads((self.remote / "current.json").read_text())
        self.assertEqual(current["scopes"]["configuration"], self.previous["scopes"]["configuration"])
        self.assertEqual(current["scopes"]["voice_instructions"]["tag"], "v0.1.0")
        self.assertFalse((self.remote / "incomplete").exists())
        self.assertFalse((self.root / "lock").exists())
        self.assertEqual(json.loads((self.root / "logs/20261021-120000.json").read_text()), self.record())

    def test_failure_preserves_previous_state_and_blocks_next_deployment(self):
        result = self.run_deployment(code="7")
        self.assertEqual(result.returncode, 7, result.stderr)
        self.assertEqual(self.record()["status"], "failed")
        self.assertEqual(json.loads((self.remote / "current.json").read_text()), self.previous)
        self.assertTrue((self.remote / "incomplete").exists())
        self.assertFalse((self.root / "lock").exists())
        self.work.mkdir()
        (self.work / "source.json").write_text('{}')
        second = self.run_deployment()
        self.assertNotEqual(second.returncode, 0)
        self.assertIn("incompleto", second.stderr)
        self.assertEqual(self.record()["status"], "failed")

    def test_invalid_backup_does_not_begin_changes(self):
        result = self.run_deployment(backup={"result": "error"})
        self.assertNotEqual(result.returncode, 0)
        self.assertFalse((self.remote / "incomplete").exists())
        self.assertFalse((self.remote / "deployments/20261021-120000.json").exists())
        self.assertEqual(json.loads((self.remote / "current.json").read_text()), self.previous)
        self.assertFalse((self.root / "lock").exists())

    def test_failed_current_write_never_claims_complete_success(self):
        result = self.run_deployment(fail_current="1")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("no se pudo actualizar", result.stderr)
        self.assertTrue((self.remote / "incomplete").exists())
        self.assertEqual(json.loads((self.remote / "current.json").read_text()), self.previous)
        self.assertEqual(self.record()["status"], "applied")


if __name__ == "__main__":
    unittest.main()
