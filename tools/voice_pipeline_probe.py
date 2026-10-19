import json
from pathlib import Path
import runpy
import sys
import time


def main():
    api = runpy.run_path(str(Path(__file__).resolve().parent / "ha_ws.py"))
    sock = api["connect"]()
    send, recv = api["send"], api["recv"]
    send(sock, {
        "id": 1, "type": "assist_pipeline/run", "pipeline": sys.argv[1],
        "device_id": sys.argv[2], "start_stage": "intent", "end_stage": "tts",
        "input": {"text": "Consulta el modo actual de la casa. No cambies nada."},
    })
    start = time.monotonic()
    stages = []
    while True:
        message = recv(sock)
        if message.get("id") != 1:
            continue
        if message.get("type") == "result" and not message.get("success"):
            sys.exit("HA rechazo la prueba del pipeline")
        if message.get("type") != "event":
            continue
        event = message["event"]
        kind = event["type"]
        stages.append(kind)
        if kind == "error":
            sys.exit("El pipeline devolvio un error; revisar el ultimo paso confirmado")
        if kind == "run-end":
            break
    sock.close()
    required = {"intent-start", "intent-end", "tts-start", "tts-end", "run-end"}
    if not required <= set(stages):
        sys.exit("La prueba no completo todas las fases")
    print(json.dumps({"fases": [s for s in stages if s in required], "duracion_s": round(time.monotonic() - start, 2), "resultado": "correcto", "audio_reproducido": False}, ensure_ascii=False))


if __name__ == "__main__":
    main()
