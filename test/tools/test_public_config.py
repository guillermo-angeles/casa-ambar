import os
from pathlib import Path
import runpy
import unittest
from unittest.mock import Mock, patch

ROOT = Path(__file__).resolve().parents[2]


class PublicConfigTests(unittest.TestCase):
    def test_unconfigured_websocket_never_reads_keychain_or_connects(self):
        with patch.dict(os.environ, {}, clear=True):
            module = runpy.run_path(str(ROOT / "tools/ha_ws.py"))
            with patch("subprocess.run") as keychain, patch("socket.create_connection") as network:
                with self.assertRaises(ValueError):
                    module["connect"]()
                keychain.assert_not_called()
                network.assert_not_called()

    def test_websocket_uses_configured_tls_host_and_port(self):
        with patch.dict(os.environ, {"HA_URL": "https://ha.example.test:9443", "HA_TOKEN_SERVICE": "test-token"}, clear=True):
            module = runpy.run_path(str(ROOT / "tools/ha_ws.py"))
        module["connect"].__globals__["recv"] = Mock(side_effect=[{"type": "auth_required"}, {"type": "auth_ok"}])
        sock = Mock()
        sock.recv.side_effect = [bytes([byte]) for byte in b"HTTP/1.1 101 Switching Protocols\r\n\r\n"]
        context = Mock()
        context.wrap_socket.return_value = sock
        with patch("subprocess.run", return_value=Mock(stdout="fake-token\n")), patch("socket.create_connection", return_value=sock) as network, patch("ssl.create_default_context", return_value=context):
            self.assertIs(module["connect"](), sock)
        network.assert_called_once_with(("ha.example.test", 9443), timeout=600)
        context.wrap_socket.assert_called_once_with(sock, server_hostname="ha.example.test")
        self.assertIn(b"Host: ha.example.test:9443", sock.sendall.call_args_list[0].args[0])

    def test_missing_locality_prevents_prompt_update(self):
        module = runpy.run_path(str(ROOT / "tools/voice_setup.py"))
        function = module["configure_agent"]
        api = Mock(return_value={"type": "form", "step_id": "init", "flow_id": "test"})
        function.__globals__["rest"] = api
        with patch.dict(os.environ, {}, clear=True), self.assertRaises(RuntimeError):
            function([{"entity_id": module["AGENT"], "config_entry_id": "test", "config_subentry_id": "test"}])
        self.assertEqual(api.call_count, 1)


if __name__ == "__main__":
    unittest.main()
