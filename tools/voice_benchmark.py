import argparse
import io
import json
import os
import subprocess
import time
import urllib.parse
import urllib.request
import wave


BASE = os.environ.get("HA_URL", "http://homeassistant.invalid:8123").rstrip("/")
PHRASES = (
    "Enciende la luz del salón.",
    "Pon el modo noche.",
    "Añade leche y pan a la lista de la compra.",
)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--engine", choices=("stt.faster_whisper", "stt.casa_groq_stt"), default="stt.faster_whisper")
    args = parser.parse_args()
    token = subprocess.run(
        ["security", "find-generic-password", "-s", os.environ.get("HA_TOKEN_SERVICE", "casa-ambar-token"), "-w"],
        capture_output=True, text=True, check=True,
    ).stdout.strip()

    def request(path, data=None, headers=None):
        req = urllib.request.Request(
            BASE + path, data=data,
            headers={"Authorization": "Bearer " + token, **(headers or {})},
        )
        with urllib.request.urlopen(req, timeout=120) as response:
            return response.read()

    for phrase in PHRASES:
        start = time.monotonic()
        result = json.loads(request(
            "/api/tts_get_url",
            json.dumps({"engine_id": "tts.piper", "message": phrase, "language": "es_ES", "cache": False}).encode(),
            {"Content-Type": "application/json"},
        ))
        parsed = urllib.parse.urlparse(result["url"])
        if not parsed.path.startswith("/api/tts_proxy/"):
            raise ValueError("Ruta de audio de HA no reconocida")
        audio = request(parsed.path)
        tts_seconds = time.monotonic() - start
        decoded = subprocess.run(
            ["/opt/homebrew/bin/ffmpeg", "-v", "error", "-i", "pipe:0", "-f", "wav", "-acodec", "pcm_s16le", "-ar", "16000", "-ac", "1", "pipe:1"],
            input=audio, capture_output=True, check=True,
        ).stdout
        with wave.open(io.BytesIO(decoded)) as stream:
            pcm = stream.readframes(stream.getnframes())
        duration = len(pcm) / 32000
        start = time.monotonic()
        transcript = json.loads(request(
            "/api/stt/" + args.engine, pcm,
            {"Content-Type": "audio/wav", "X-Speech-Content": "format=wav;codec=pcm;sample_rate=16000;bit_rate=16;channel=1;language=es"},
        ))
        print(json.dumps({"motor": args.engine, "frase": phrase, "audio_s": round(duration, 2), "tts_s": round(tts_seconds, 2), "stt_s": round(time.monotonic() - start, 2), "transcripcion": transcript.get("text"), "resultado": transcript.get("result")}, ensure_ascii=False), flush=True)


if __name__ == "__main__":
    main()
