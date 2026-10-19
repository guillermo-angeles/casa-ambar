import importlib.util
import json
from pathlib import Path
import unittest

spec = importlib.util.spec_from_file_location("camera_access", Path(__file__).resolve().parents[2] / "tools/echo_camera_access.py")
camera_access = importlib.util.module_from_spec(spec)
spec.loader.exec_module(camera_access)


class SecretMergeTests(unittest.TestCase):
    def test_preserves_other_secrets_and_formatting(self):
        old = '# existing settings\nother_secret: "unchanged"\n'
        merged = camera_access.merge_secret(old, "-rtsp_transport tcp -i rtsp://example.invalid/camera")
        self.assertTrue(merged.startswith(old))
        self.assertEqual(merged.count("echo_camera_rtsp:"), 1)

    def test_replaces_only_the_managed_secret(self):
        old = 'other_secret: "echo_camera_rtsp: keep"\necho_camera_rtsp: "old"\nlast_secret: true\n'
        merged = camera_access.merge_secret(old, "new")
        self.assertEqual(merged, 'other_secret: "echo_camera_rtsp: keep"\necho_camera_rtsp: "new"\nlast_secret: true\n')
        self.assertEqual(camera_access.merge_secret(merged, "new"), merged)

    def test_quotes_special_characters_without_changing_them(self):
        source = '-rtsp_transport tcp -i rtsp://example.invalid/camera?x="test"&v=1'
        merged = camera_access.merge_secret("", source)
        self.assertEqual(json.loads(merged.split(":", 1)[1]), source)

    def test_refuses_unmanaged_block_without_disclosing_its_value(self):
        with self.assertRaises(RuntimeError) as result:
            camera_access.merge_secret("echo_camera_rtsp: |\n  private-test-data\n", "new")
        self.assertNotIn("private-test-data", str(result.exception))


if __name__ == "__main__":
    unittest.main()
