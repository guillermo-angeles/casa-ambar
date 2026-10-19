from pathlib import Path
import runpy
import unittest
from unittest.mock import Mock, patch


MODULE = runpy.run_path(str(Path(__file__).resolve().parents[2] / "tools/voice_setup.py"))


class VoiceSetupTests(unittest.TestCase):
    def test_sensitive_entities_are_never_allowed(self):
        self.assertFalse(any(e.startswith(("lock.", "camera.")) for e in MODULE["ALLOWED"]))

    def test_missing_entities_abort_before_exposure_changes(self):
        function = MODULE["configure_exposure"]
        function.__globals__["ws"] = api = Mock()
        with self.assertRaises(RuntimeError):
            function([])
        api.assert_not_called()

    def test_exposure_removes_unexpected_entities_and_disables_auto_exposure(self):
        function = MODULE["configure_exposure"]
        allowed = MODULE["ALLOWED"]
        exposed = {"lock.test": {"conversation": True}, "switch.unrelated": {"conversation": True}}
        calls = []

        def api(command):
            calls.append(command)
            if command["type"].endswith("/list"):
                return {"exposed_entities": dict(exposed)}
            if command["type"] == "homeassistant/expose_entity":
                for entity in command["entity_ids"]:
                    if command["should_expose"]:
                        exposed[entity] = {"conversation": True}
                    else:
                        exposed.pop(entity, None)

        function.__globals__["ws"] = api
        function([{"entity_id": entity} for entity in allowed | {"lock.test", "camera.test"}])
        self.assertEqual(set(exposed), allowed)
        self.assertIn({"type": "homeassistant/expose_new_entities/set", "assistant": "conversation", "expose_new": False}, calls)
        removed = next(c for c in calls if c.get("should_expose") is False)
        self.assertTrue({"lock.test", "camera.test", "switch.unrelated"} <= set(removed["entity_ids"]))

    def test_agent_failure_prevents_assignment(self):
        function = MODULE["connect"]
        function.__globals__["rest"] = Mock(return_value={"response": {"response_type": "error"}})
        function.__globals__["ws"] = api = Mock()
        with self.assertRaises(RuntimeError):
            function("test")
        api.assert_not_called()

    def test_unexpected_form_is_rejected(self):
        function = MODULE["configure_agent"]
        api = Mock(return_value={"type": "form", "step_id": "unknown"})
        function.__globals__["rest"] = api
        with self.assertRaises(RuntimeError):
            function([{"entity_id": MODULE["AGENT"], "config_entry_id": "test", "config_subentry_id": "test"}])
        self.assertEqual(api.call_count, 1)

    def test_regular_setup_preserves_selected_transcription_engine(self):
        module = runpy.run_path(str(Path(__file__).resolve().parents[2] / "tools/voice_setup.py"))
        function = module["configure_pipeline"]
        api = Mock(side_effect=[
            {"voices": [{"voice_id": "es_ES-davefx-medium"}]},
            {"pipelines": [{"name": "Casa", "id": "casa-test", "stt_engine": "stt.casa_groq_stt"}]},
            None, [{"name": "Salón", "area_id": "salon"}], None,
        ])
        function.__globals__["ws"] = api
        function([{"entity_id": module["ECHO"], "device_id": "echo-test"}])
        update = api.call_args_list[2].args[0]
        self.assertEqual(update["stt_engine"], "stt.casa_groq_stt")

    def test_stt_switch_changes_only_engine_in_existing_pipeline(self):
        module = runpy.run_path(str(Path(__file__).resolve().parents[2] / "tools/voice_setup.py"))
        function = module["select_stt"]
        before = {"id": "casa-test", "name": "Casa", "language": "es", "stt_engine": "stt.faster_whisper", "conversation_engine": "conversation.test", "tts_engine": "tts.piper", "prefer_local_intents": True}
        after = {**before, "stt_engine": "stt.casa_groq_stt"}
        api = Mock(side_effect=[
            [{"entity_id": "stt.casa_groq_stt", "state": "unknown"}],
            {"pipelines": [before]}, None, {"pipelines": [after]},
        ])
        function.__globals__["ws"] = api
        function("stt.casa_groq_stt")
        update = api.call_args_list[2].args[0]
        self.assertEqual(update["pipeline_id"], before["id"])
        self.assertEqual({k: v for k, v in update.items() if k not in ("type", "pipeline_id")}, {k: v for k, v in after.items() if k != "id"})

    def test_unavailable_stt_aborts_before_pipeline_changes(self):
        module = runpy.run_path(str(Path(__file__).resolve().parents[2] / "tools/voice_setup.py"))
        function = module["select_stt"]
        api = Mock(return_value=[{"entity_id": "stt.casa_groq_stt", "state": "unavailable"}])
        function.__globals__["ws"] = api
        with self.assertRaises(RuntimeError):
            function("stt.casa_groq_stt")
        self.assertEqual(api.call_count, 1)

    def test_instructions_update_leaves_pipeline_and_exposure_untouched(self):
        module = runpy.run_path(str(Path(__file__).resolve().parents[2] / "tools/voice_setup.py"))
        function = module["main"]
        namespace = function.__globals__
        namespace["ws"] = Mock(return_value=[])
        namespace["configure_agent"] = agent = Mock()
        namespace["configure_exposure"] = exposure = Mock()
        namespace["configure_pipeline"] = pipeline = Mock()
        namespace["connect"] = connect = Mock()
        with patch("sys.argv", ["voice_setup.py", "--instructions-only"]):
            function()
        agent.assert_called_once_with([])
        exposure.assert_not_called()
        pipeline.assert_not_called()
        connect.assert_not_called()


if __name__ == "__main__":
    unittest.main()
