import asyncio
import io
import sys
import tempfile
import unittest
import wave
from types import SimpleNamespace
from unittest.mock import AsyncMock, patch

import aiohttp
from aiohttp import web

sys.path.insert(0, "/config")

from custom_components.casa_groq_stt import client as module
from custom_components.casa_groq_stt.client import GroqAuthError, GroqClient, GroqError, MODEL
from custom_components.casa_groq_stt.stt import GroqSpeechEntity
from homeassistant.components import stt
from homeassistant import bootstrap, loader
from homeassistant.helpers import entity_registry
from homeassistant.core import HomeAssistant


async def audio(*chunks):
    for chunk in chunks:
        yield chunk


class GroqTests(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.requests = []
        self.status = 200
        self.payload = {"text": "Enciende el salón"}
        self.delay = 0
        self.model_available = True
        self.app = web.Application()
        self.app.router.add_route("*", "/{path:.*}", self.handle)
        self.runner = web.AppRunner(self.app)
        await self.runner.setup()
        self.site = web.TCPSite(self.runner, "127.0.0.1", 0)
        await self.site.start()
        port = self.site._server.sockets[0].getsockname()[1]
        self.root_patch = patch.object(module, "API_ROOT", f"http://127.0.0.1:{port}")
        self.root_patch.start()
        self.session = aiohttp.ClientSession()
        self.client = GroqClient(self.session, "test-key-not-a-credential")

    async def asyncTearDown(self):
        await self.session.close()
        self.root_patch.stop()
        await self.runner.cleanup()

    async def handle(self, request):
        record = {"path": request.path, "auth": request.headers.get("Authorization")}
        if request.method == "POST":
            reader = await request.multipart()
            fields = {}
            while (part := await reader.next()) is not None:
                fields[part.name] = bytes(await part.read())
            record["fields"] = fields
        self.requests.append(record)
        await asyncio.sleep(self.delay)
        if self.status != 200:
            return web.Response(status=self.status, text="private-provider-response")
        if request.path == "/models":
            return web.json_response({"data": [{"id": MODEL}] if self.model_available else []})
        if self.payload is None:
            return web.Response(text="not-json", content_type="application/json")
        return web.json_response(self.payload)

    async def test_upload_is_spanish_wav_and_preserves_pcm(self):
        pcm = b"\x00\x01" * 1600
        text = await self.client.transcribe(audio(pcm[:1500], pcm[1500:]))
        self.assertEqual(text, "Enciende el salón")
        record = self.requests[0]
        self.assertEqual(record["path"], "/audio/transcriptions")
        self.assertEqual(record["auth"], "Bearer test-key-not-a-credential")
        fields = record["fields"]
        self.assertEqual(fields["language"], b"es")
        self.assertEqual(fields["model"], MODEL.encode())
        self.assertEqual(fields["response_format"], b"json")
        with wave.open(io.BytesIO(fields["file"]), "rb") as wav:
            self.assertEqual((wav.getnchannels(), wav.getsampwidth(), wav.getframerate()), (1, 2, 16000))
            self.assertEqual(wav.readframes(wav.getnframes()), pcm)

    async def test_key_and_model_validation_without_audio(self):
        await self.client.validate()
        self.assertEqual(self.requests[0]["path"], "/models")
        self.model_available = False
        with self.assertRaisesRegex(GroqError, "model_unavailable"):
            await self.client.validate()

    async def test_errors_are_sanitized_and_not_retried(self):
        for status, kind in ((401, GroqAuthError), (403, GroqAuthError), (429, GroqError), (500, GroqError), (302, GroqError)):
            with self.subTest(status=status):
                self.status = status
                before = len(self.requests)
                with self.assertRaises(kind) as caught:
                    await self.client.transcribe(audio(b"\x00\x00" * 10))
                self.assertNotIn("private", str(caught.exception))
                self.assertEqual(len(self.requests), before + 1)

    async def test_invalid_responses_fail_cleanly(self):
        for payload in (None, [], {}, {"text": 4}, {"text": "  "}):
            with self.subTest(payload=payload):
                self.payload = payload
                with self.assertRaises(GroqError):
                    await self.client.transcribe(audio(b"\x00\x00" * 10))

    async def test_empty_odd_or_oversize_audio_never_uploaded(self):
        for chunks in ((), (b"x",), (b"00", b"x" * module.MAX_AUDIO_BYTES)):
            with self.subTest(size=sum(map(len, chunks))):
                with self.assertRaises(GroqError):
                    await self.client.transcribe(audio(*chunks))
        self.assertFalse(self.requests)

    async def test_timeout_fails_without_retry(self):
        self.delay = 0.1
        with patch.object(module, "ClientTimeout", return_value=aiohttp.ClientTimeout(total=0.01)):
            with self.assertRaisesRegex(GroqError, "cannot_connect"):
                await self.client.validate()
        self.assertEqual(len(self.requests), 1)

    async def test_ha_entity_metadata_and_error_contract(self):
        entry = SimpleNamespace(runtime_data=self.client, async_start_reauth=AsyncMock())
        entity = GroqSpeechEntity(entry)
        metadata = stt.SpeechMetadata(language="es", format=stt.AudioFormats.WAV, codec=stt.AudioCodecs.PCM, bit_rate=16, sample_rate=16000, channel=1)
        self.assertTrue(entity.check_metadata(metadata))
        result = await entity.async_process_audio_stream(metadata, audio(b"00" * 10))
        self.assertEqual(result.result, stt.SpeechResultState.SUCCESS)
        self.status = 429
        with self.assertLogs("custom_components.casa_groq_stt.stt", level="WARNING") as logs:
            result = await entity.async_process_audio_stream(metadata, audio(b"00" * 10))
        self.assertEqual(result.result, stt.SpeechResultState.ERROR)
        self.assertNotIn("private", str(logs.output))
        metadata.language = "en"
        before = len(self.requests)
        result = await entity.async_process_audio_stream(metadata, audio(b"00"))
        self.assertEqual(result.result, stt.SpeechResultState.ERROR)
        self.assertEqual(len(self.requests), before)

    async def test_ha_flow_loads_platform_prevents_duplicates_and_reconfigures(self):
        with tempfile.TemporaryDirectory() as config_dir:
            hass = HomeAssistant(config_dir)
            import shutil
            shutil.copytree("/config/custom_components", f"{config_dir}/custom_components")
            try:
                loader.async_setup(hass)
                self.assertIsNotNone(await bootstrap.async_from_config_dict({"stt": {}, "http": {"server_host": "127.0.0.1", "server_port": 18124}}, hass))
                await hass.async_start()
                result = await hass.config_entries.flow.async_init(module.DOMAIN, context={"source": "user"})
                self.assertEqual(result["type"], "form")
                self.status = 401
                result = await hass.config_entries.flow.async_configure(result["flow_id"], {"api_key": "fake"})
                self.assertEqual(result["errors"], {"base": "invalid_auth"})
                self.status = 200
                result = await hass.config_entries.flow.async_configure(result["flow_id"], {"api_key": "fake"})
                self.assertEqual(result["type"], "create_entry")
                await hass.async_block_till_done()
                entry = result["result"]
                self.assertEqual(entry.state.value, "loaded")
                registry = entity_registry.async_get(hass)
                entities = entity_registry.async_entries_for_config_entry(registry, entry.entry_id)
                self.assertTrue(entities, [(key, str(type(value))) for key, value in hass.data.items() if "stt" in str(key)])
                self.assertEqual(entities[0].domain, "stt")
                duplicate = await hass.config_entries.flow.async_init(module.DOMAIN, context={"source": "user"})
                self.assertEqual(duplicate["reason"], "already_configured")
                change = await hass.config_entries.flow.async_init(module.DOMAIN, context={"source": "reconfigure", "entry_id": entry.entry_id})
                result = await hass.config_entries.flow.async_configure(change["flow_id"], {"api_key": "replacement-fake"})
                self.assertEqual(result["type"], "abort")
                await hass.async_block_till_done()
                self.assertEqual(entry.data["api_key"], "replacement-fake")
                self.assertEqual(entry.state.value, "loaded")
            finally:
                await hass.async_stop()


if __name__ == "__main__":
    unittest.main(verbosity=2)
