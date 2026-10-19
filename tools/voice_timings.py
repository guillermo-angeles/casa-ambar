import datetime
import json
import os
from pathlib import Path
import subprocess


ROOT = Path(__file__).resolve().parent
PIPELINE = os.environ.get("HA_PIPELINE_ID", "")


def request(command):
    result = subprocess.run(
        ["/usr/bin/python3", "-I", str(ROOT / "ha_ws.py")],
        input=json.dumps([command]), capture_output=True, text=True, check=True,
    )
    response = json.loads(result.stdout)[0]
    if not response.get("success"):
        raise RuntimeError("No se pudieron consultar los tiempos del pipeline")
    return response["result"]


def summarize(events):
    phases = {}
    for event in events:
        if event.get("type") != "intent-progress":
            phases[event["type"]] = datetime.datetime.fromisoformat(event["timestamp"])

    def elapsed(start, end):
        if start not in phases or end not in phases:
            return None
        return round((phases[end] - phases[start]).total_seconds(), 3)

    return {
        "escucha_y_stt_s": elapsed("stt-start", "stt-end"),
        "interpretacion_s": elapsed("intent-start", "intent-end"),
        "metadatos_tts_s": elapsed("tts-start", "tts-end"),
        "pipeline_s": elapsed("run-start", "run-end"),
    }


def main():
    if not PIPELINE:
        raise SystemExit("Configura HA_PIPELINE_ID")
    runs = request({"type": "assist_pipeline/pipeline_debug/list", "pipeline_id": PIPELINE})["pipeline_runs"]
    summaries = []
    for run in runs[-5:]:
        events = request({"type": "assist_pipeline/pipeline_debug/get", "pipeline_id": PIPELINE, "pipeline_run_id": run["pipeline_run_id"]})["events"]
        summaries.append({"fecha": run["timestamp"], **summarize(events)})
    print(json.dumps({"mediciones": summaries, "nota": "STT incluye escucha. TTS solo mide sus eventos, no el primer audio ni la reproduccion."}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
