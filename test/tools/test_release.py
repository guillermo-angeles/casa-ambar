import copy
import hashlib
import json
from pathlib import Path
import runpy
import subprocess
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[2]
MODULE = runpy.run_path(str(ROOT / "tools/release.py"))


class ReleaseTests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.root = Path(self.directory.name)
        for name in ("VERSION", "CHANGELOG.md", "config/www/casa-ambar/casa-ambar-card.js", "config/configuration.snippet.yaml", "apps/dashcast/config.yaml", "custom_components/casa_groq_stt/manifest.json", "tools/deploy.sh", "tools/release.py"):
            target = self.root / name
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes((ROOT / name).read_bytes())
        (self.root / ".gitignore").write_text("test/echo-voz/\n")
        (self.root / "CHANGELOG.md").write_text("## [0.1.0] - 2026-10-21\n")
        self.git("init", "-q")
        self.git("config", "user.name", "Test")
        self.git("config", "user.email", "test@example.invalid")
        self.git("add", ".")
        self.git("-c", "core.hooksPath=/dev/null", "-c", "commit.gpgsign=false", "commit", "-qm", "fixture")
        self.git("tag", "v0.1.0")

    def git(self, *args):
        return subprocess.check_output(["git", "-C", str(self.root), *args], stderr=subprocess.DEVNULL, text=True).strip()

    def test_clean_tag_produces_component_manifest(self):
        source = MODULE["manifest"](self.root, "v0.1.0")
        self.assertEqual(source["commit"], self.git("rev-parse", "HEAD"))
        self.assertEqual(source["components"], {"card": "2.1.2", "dashcast": "0.2.0", "groq_stt": "0.1.0"})

    def test_dirty_or_untracked_checkout_is_rejected(self):
        for path in ("VERSION", "untracked.txt"):
            with self.subTest(path=path):
                target = self.root / path
                original = target.read_bytes() if target.exists() else None
                target.write_text("changed")
                with self.assertRaises(ValueError):
                    MODULE["manifest"](self.root, "v0.1.0")
                if original is None:
                    target.unlink()
                else:
                    target.write_bytes(original)

    def test_wrong_tag_or_untagged_commit_is_rejected(self):
        with self.assertRaises(ValueError):
            MODULE["manifest"](self.root, "v9.0.0")
        self.git("-c", "core.hooksPath=/dev/null", "-c", "commit.gpgsign=false", "commit", "--allow-empty", "-qm", "later")
        with self.assertRaises(ValueError):
            MODULE["manifest"](self.root, "v0.1.0")

    def test_check_mode_is_offline_and_requires_no_credentials(self):
        result = subprocess.run(["/bin/bash", str(self.root / "tools/deploy.sh"), "--version", "v0.1.0", "--check"], capture_output=True, text=True, env={"PATH": "/usr/bin:/bin"})
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(json.loads(result.stdout)["tag"], "v0.1.0")

    def test_release_notes_select_only_the_requested_version(self):
        (self.root / "CHANGELOG.md").write_text("## Sin publicar\nFuture\n## [0.1.0] - 2026-10-21\nCurrent release\n## [0.0.1] - 2026-10-20\nEarlier\n")
        self.assertEqual(MODULE["release_notes"](self.root, "v0.1.0"), "Current release")
        with self.assertRaises(ValueError):
            MODULE["release_notes"](self.root, "v0.0.1")

    def test_native_binary_must_match_tag_and_hashes(self):
        folder = self.root / "test/echo-voz"
        folder.mkdir(parents=True)
        patch = self.root / "firmware/techo5/casa-voice.patch"
        patch.parent.mkdir(parents=True)
        patch.write_bytes(b"test patch")
        self.git("add", "firmware")
        self.git("-c", "core.hooksPath=/dev/null", "-c", "commit.gpgsign=false", "commit", "-qm", "patch")
        self.git("tag", "-f", "v0.1.0")
        (folder / "techo5-casa-arm").write_bytes(b"fake binary")
        built = {"commit": self.git("rev-parse", "HEAD"), "binary_sha256": hashlib.sha256(b"fake binary").hexdigest(), "patch_sha256": hashlib.sha256(b"test patch").hexdigest()}
        (folder / "build-manifest.json").write_text(json.dumps(built))
        self.assertIn("native_binary_sha256", MODULE["manifest"](self.root, "v0.1.0", True))
        (folder / "techo5-casa-arm").write_bytes(b"other binary")
        with self.assertRaises(ValueError):
            MODULE["manifest"](self.root, "v0.1.0", True)


class DeploymentRecordTests(unittest.TestCase):
    def setUp(self):
        self.source = {"version": "0.1.0", "tag": "v0.1.0", "commit": "a" * 40, "components": {"card": "2.1.2"}}
        self.previous = {"schema": 1, "scopes": {"configuration": {"version": "0.0.1", "tag": "v0.0.1"}}}
        self.backup = {"result": "ok", "data": {"slug": "a1b2c3d4"}}

    def prepare(self, mode="configuration"):
        return MODULE["prepare"](self.source, self.previous, mode, "20261021-120000", self.backup)

    def test_partial_deployment_preserves_other_component_versions(self):
        original = copy.deepcopy(self.previous)
        record = self.prepare("--dashcast-only")
        self.assertEqual(record["current"]["scopes"]["configuration"], self.previous["scopes"]["configuration"])
        self.assertEqual(record["current"]["scopes"]["dashcast"]["tag"], "v0.1.0")
        self.assertEqual(record["previous"], original)
        self.assertEqual(self.previous, original)
        self.assertEqual(record["status"], "pending")
        self.assertEqual(record["backup_slug"], "a1b2c3d4")

    def test_voice_setup_records_every_changed_scope(self):
        record = self.prepare("--voice-setup")
        for scope in ("voice_apps", "voice_pipeline", "voice_instructions"):
            self.assertEqual(record["current"]["scopes"][scope]["tag"], "v0.1.0")
        self.assertEqual(record["current"]["scopes"]["configuration"], self.previous["scopes"]["configuration"])

    def test_failed_or_invalid_backup_is_rejected(self):
        for backup in ({"result": "error"}, {"result": "ok", "data": {"slug": "bad; command"}}, {"result": "ok", "data": {}}):
            with self.subTest(backup=backup), self.assertRaises(ValueError):
                MODULE["prepare"](self.source, self.previous, "configuration", "20261021-120000", backup)

    def test_rollback_requires_exact_record_and_safe_backup_identifier(self):
        record = self.prepare()
        record["status"] = "applied"
        self.assertEqual(MODULE["rollback_info"](record, "20261021-120000"), "a1b2c3d4")
        with self.assertRaises(ValueError):
            MODULE["rollback_info"](record, "20261021-120001")
        record["backup_slug"] = "bad; command"
        with self.assertRaises(ValueError):
            MODULE["rollback_info"](record, "20261021-120000")

    def test_native_and_dashcast_require_component_rollback(self):
        for mode in ("--echo-voice", "--dashcast-only"):
            record = self.prepare(mode)
            with self.assertRaises(ValueError):
                MODULE["rollback_info"](record, "20261021-120000")


if __name__ == "__main__":
    unittest.main()
