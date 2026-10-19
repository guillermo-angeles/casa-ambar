import json
import os
import subprocess
import time
import urllib.parse
import urllib.request


BASE = os.environ.get("HA_URL", "http://homeassistant.invalid:8123").rstrip("/")
SAMPLES = (
    "Esta es una prueba de velocidad de la voz. El asistente debe empezar a responder pronto y hablar con claridad, sin esperar a que termine de prepararse toda la respuesta.",
    "Esta es una prueba de una respuesta más larga para comparar dos motores de voz. Queremos saber cuánto tarda en aparecer el primer audio y cuánto tarda en estar disponible el archivo completo. El texto es sintético y no contiene información de la casa ni conversaciones personales. Una buena experiencia debe combinar una voz clara, un ritmo natural y una espera corta. No basta con responder deprisa si después resulta difícil entender lo que se está diciendo.",
)
ENGINES = (("tts.piper", "es_ES"), ("tts.google_translate_en_com", "es-es"))


def main():
    token = subprocess.run(
        ["security", "find-generic-password", "-s", os.environ.get("HA_TOKEN_SERVICE", "casa-ambar-token"), "-w"],
        capture_output=True, text=True, check=True,
    ).stdout.strip()

    def request(path, data=None):
        return urllib.request.urlopen(urllib.request.Request(
            BASE + path, data=json.dumps(data).encode() if data is not None else None,
            headers={"Authorization": "Bearer " + token, "Content-Type": "application/json"},
        ), timeout=120)

    for engine, language in ENGINES:
        for sample, message in enumerate(SAMPLES, start=1):
            start = time.monotonic()
            with request("/api/tts_get_url", {"engine_id": engine, "message": message, "language": language, "cache": False}) as response:
                result = json.load(response)
            url_ready = time.monotonic() - start
            path = urllib.parse.urlparse(result["url"]).path
            if not path.startswith("/api/tts_proxy/"):
                raise ValueError("Ruta de audio no reconocida")
            with request(path) as response:
                first = response.read(1)
                first_audio = time.monotonic() - start
                audio = first + response.read()
            complete = time.monotonic() - start
            decoded = subprocess.run(
                ["/opt/homebrew/bin/ffmpeg", "-v", "error", "-i", "pipe:0", "-f", "s16le", "-ar", "16000", "-ac", "1", "pipe:1"],
                input=audio, capture_output=True, check=True,
            ).stdout
            print(json.dumps({"motor": engine, "muestra": sample, "caracteres": len(message), "url_s": round(url_ready, 2), "primer_audio_http_s": round(first_audio, 2), "audio_completo_s": round(complete, 2), "duracion_audio_s": round(len(decoded) / 32000, 2)}, ensure_ascii=False), flush=True)


if __name__ == "__main__":
    main()
