import asyncio
import io
import wave

from aiohttp import ClientError, ClientSession, ClientTimeout, FormData

DOMAIN = "casa_groq_stt"
MODEL = "whisper-large-v3-turbo"
API_ROOT = "https://api.groq.com/openai/v1"
MAX_AUDIO_BYTES = 16000 * 2 * 120


class GroqError(Exception):
    pass


class GroqAuthError(GroqError):
    pass


class GroqClient:
    def __init__(self, session: ClientSession, api_key: str):
        self.session = session
        self._api_key = api_key

    async def _request(self, path, **kwargs):
        try:
            async with self.session.request(
                "POST" if "data" in kwargs else "GET",
                f"{API_ROOT}/{path}",
                headers={"Authorization": f"Bearer {self._api_key}"},
                timeout=ClientTimeout(total=25),
                allow_redirects=False,
                **kwargs,
            ) as response:
                if response.status in (401, 403):
                    raise GroqAuthError("invalid_auth")
                if response.status == 429:
                    raise GroqError("rate_limit")
                if response.status != 200:
                    raise GroqError("provider_error")
                return await response.json()
        except (ClientError, asyncio.TimeoutError, ValueError):
            raise GroqError("cannot_connect") from None

    async def validate(self):
        data = await self._request("models")
        if not isinstance(data, dict) or not isinstance(data.get("data"), list):
            raise GroqError("invalid_response")
        if not any(isinstance(item, dict) and item.get("id") == MODEL for item in data["data"]):
            raise GroqError("model_unavailable")

    async def transcribe(self, stream):
        pcm = bytearray()
        async for chunk in stream:
            if len(pcm) + len(chunk) > MAX_AUDIO_BYTES:
                raise GroqError("audio_too_long")
            pcm.extend(chunk)
        if not pcm or len(pcm) % 2:
            raise GroqError("invalid_audio")
        output = io.BytesIO()
        with wave.open(output, "wb") as wav:
            wav.setnchannels(1)
            wav.setsampwidth(2)
            wav.setframerate(16000)
            wav.writeframes(pcm)
        form = FormData()
        form.add_field("file", output.getvalue(), filename="audio.wav", content_type="audio/wav")
        form.add_field("model", MODEL)
        form.add_field("language", "es")
        form.add_field("response_format", "json")
        data = await self._request("audio/transcriptions", data=form)
        if not isinstance(data, dict) or not isinstance(data.get("text"), str):
            raise GroqError("invalid_response")
        text = data["text"].strip()
        if not text:
            raise GroqError("empty_transcription")
        return text
