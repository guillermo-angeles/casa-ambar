import argparse
import json
import os
from pathlib import Path
import subprocess
import sys
import time
import urllib.request


ROOT = Path(__file__).resolve().parent.parent
BASE = os.environ.get("HA_URL", "http://homeassistant.invalid:8123").rstrip("/")
AGENT = "conversation.claude_conversation"
ECHO = "select.echo_salon_assistant"
ALLOWED = {
    "light.lampara_sofa", "light.lampara_comedor", "light.lampara_pie",
    "light.lampara_dormitorio", "light.lampara_recibidor", "light.led_cocina", "light.led_tv",
    "media_player.tv_salon", "media_player.spotify", "media_player.echo_salon_speaker",
    "weather.aemet", "sensor.aemet_temperature", "sensor.aemet_temperature_feeling",
    "sensor.aemet_humidity", "sensor.aemet_daily_forecast_temperature",
    "sensor.aemet_daily_forecast_temperature_low", "sensor.casa_resumen",
    "input_select.modo_casa", "calendar.cookidoo_plan_de_comidas",
    "todo.cookidoo_lista_de_la_compra", "todo.cookidoo_compras_adicionales",
    "script.spotify_favoritos", "script.voz_estado_casa", "script.voz_escena_estancia",
    "script.voz_lista_compra_anadir",
    *{"script.modo_" + mode for mode in ("dia", "tarde", "noche", "cine", "dormir", "fuera")},
}
MODEL_OPTIONS = {
    "max_tokens": 4096, "thinking_effort": "medium",
    "code_execution": True, "web_search": True, "web_search_max_uses": 5,
    "user_location": False, "web_fetch": True, "web_fetch_max_uses": 3,
}


def ws(command):
    response = subprocess.run(
        ["/usr/bin/python3", "-I", str(ROOT / "tools/ha_ws.py")],
        input=json.dumps([command]), capture_output=True, text=True, timeout=600,
    )
    if response.returncode:
        raise RuntimeError("Fallo de conexion WebSocket")
    result = json.loads(response.stdout)[0]
    if not result.get("success"):
        raise RuntimeError("HA rechazo una operacion de voz")
    return result.get("result")


def rest(path, data):
    token = subprocess.run(
        ["security", "find-generic-password", "-s", os.environ.get("HA_TOKEN_SERVICE", "casa-ambar-token"), "-w"],
        capture_output=True, text=True, check=True,
    ).stdout.strip()
    req = urllib.request.Request(
        BASE + path, data=json.dumps(data).encode(),
        headers={"Authorization": "Bearer " + token, "Content-Type": "application/json"},
    )
    with urllib.request.urlopen(req, timeout=180) as response:
        return json.load(response)


def require_step(flow, step):
    if flow.get("type") != "form" or flow.get("step_id") != step or flow.get("errors"):
        raise RuntimeError("El formulario de Anthropic no coincide con el esperado")


def configure_agent(registry):
    entry = next(e for e in registry if e["entity_id"] == AGENT)
    flow = rest("/api/config/config_entries/subentries/flow", {
        "handler": [entry["config_entry_id"], "conversation"],
        "subentry_id": entry["config_subentry_id"],
    })
    require_step(flow, "init")
    path = "/api/config/config_entries/subentries/flow/" + flow["flow_id"]
    prompt = (ROOT / "config/voice/casa-instrucciones.txt").read_text()
    locality = os.environ.get("CASA_LOCALIDAD", "").strip()
    if not locality:
        raise RuntimeError("Configura CASA_LOCALIDAD antes de preparar el agente")
    flow = rest(path, {
        "recommended": False, "llm_hass_api": ["assist"],
        "prompt": prompt.replace("TU_MUNICIPIO", locality),
    })
    require_step(flow, "additional")
    flow = rest(path, {"chat_model": "claude-haiku-5-5", "prompt_caching": "automatic"})
    require_step(flow, "model")
    fields = {field["name"] for field in flow["data_schema"]}
    if not MODEL_OPTIONS.keys() <= fields:
        raise RuntimeError("Faltan opciones de modelo requeridas")
    flow = rest(path, MODEL_OPTIONS)
    if flow.get("type") != "abort" or flow.get("reason") != "reconfigure_successful":
        raise RuntimeError("No se confirmo la configuracion de Anthropic")
    print("Haiku5.5: esfuerzo medio, 4096 tokens, busqueda5, lectura3 y codigo remoto", flush=True)


def configure_exposure(states):
    available = {e["entity_id"] for e in states}
    missing = ALLOWED - available
    if missing:
        raise RuntimeError("Faltan entidades de voz: " + ", ".join(sorted(missing)))
    exposed = ws({"type": "homeassistant/expose_entity/list"})["exposed_entities"]
    remove = [entity for entity, assistants in exposed.items() if assistants.get("conversation") and entity not in ALLOWED]
    forbidden = [e for e in available if e.startswith(("lock.", "camera."))]
    ws({"type": "homeassistant/expose_new_entities/set", "assistant": "conversation", "expose_new": False})
    ws({"type": "homeassistant/expose_entity", "assistants": ["conversation"], "entity_ids": sorted(set(remove + forbidden)), "should_expose": False})
    ws({"type": "homeassistant/expose_entity", "assistants": ["conversation"], "entity_ids": sorted(ALLOWED), "should_expose": True})
    actual = ws({"type": "homeassistant/expose_entity/list"})["exposed_entities"]
    actual = {e for e, assistants in actual.items() if assistants.get("conversation")}
    if actual != ALLOWED:
        raise RuntimeError("La exposicion final no coincide con la permitida")
    print("Assist: entidades permitidas verificadas; cerraduras y camaras excluidas", flush=True)


def configure_pipeline(registry):
    voices = ws({"type": "tts/engine/voices", "engine_id": "tts.piper", "language": "es_ES"})
    if "es_ES-davefx-medium" not in {v["voice_id"] for v in voices["voices"]}:
        raise RuntimeError("La voz Piper requerida no esta disponible")
    fields = {
        "name": "Casa", "language": "es", "conversation_engine": AGENT,
        "conversation_language": "es", "stt_engine": "stt.faster_whisper", "stt_language": "es",
        "tts_engine": "tts.piper", "tts_language": "es_ES", "tts_voice": "es_ES-davefx-medium",
        "wake_word_entity": None, "wake_word_id": None, "prefer_local_intents": True,
    }
    pipelines = ws({"type": "assist_pipeline/pipeline/list"})["pipelines"]
    existing = [p for p in pipelines if p["name"] == "Casa"]
    if len(existing) > 1:
        raise RuntimeError("Hay mas de un pipeline Casa; no se creara otro")
    if existing:
        pipeline_id = existing[0]["id"]
        fields["stt_engine"] = existing[0]["stt_engine"]
        ws({"type": "assist_pipeline/pipeline/update", "pipeline_id": pipeline_id, **fields})
    else:
        pipeline_id = ws({"type": "assist_pipeline/pipeline/create", **fields})["id"]
    echo = next(e for e in registry if e["entity_id"] == ECHO)
    areas = ws({"type": "config/area_registry/list"})
    salon = next(a["area_id"] for a in areas if a["name"] == "Salón")
    ws({"type": "config/device_registry/update", "device_id": echo["device_id"], "area_id": salon})
    return pipeline_id


def select_stt(engine):
    if engine not in ("stt.casa_groq_stt", "stt.faster_whisper"):
        raise RuntimeError("Motor STT no permitido")
    states = ws({"type": "get_states"})
    target = next((e for e in states if e["entity_id"] == engine), None)
    if target is None or target["state"] == "unavailable":
        raise RuntimeError("El motor STT no esta disponible")
    pipelines = ws({"type": "assist_pipeline/pipeline/list"})["pipelines"]
    casa = [p for p in pipelines if p["name"] == "Casa"]
    if len(casa) != 1:
        raise RuntimeError("Debe existir un unico pipeline Casa")
    before = casa[0]
    expected = {**before, "stt_engine": engine}
    fields = {key: value for key, value in expected.items() if key != "id"}
    ws({"type": "assist_pipeline/pipeline/update", "pipeline_id": before["id"], **fields})
    actual = ws({"type": "assist_pipeline/pipeline/list"})["pipelines"]
    if next((p for p in actual if p["id"] == before["id"]), None) != expected:
        raise RuntimeError("El pipeline no confirma el cambio exclusivo de STT")
    print("Casa: motor STT verificado " + engine, flush=True)


def connect(pipeline_id):
    result = rest("/api/conversation/process", {
        "agent_id": AGENT, "language": "es",
        "text": "Consulta con tus herramientas el modo actual de la casa y dime cual es. Solo consulta; no cambies nada.",
    })
    response = result.get("response", {})
    if response.get("response_type") == "error" or not response.get("speech", {}).get("plain", {}).get("speech"):
        raise RuntimeError("El agente no supero la prueba de consulta")
    print("Prueba de consulta del agente: " + response["speech"]["plain"]["speech"], flush=True)
    for _ in range(60):
        states = ws({"type": "get_states"})
        echo = next(e for e in states if e["entity_id"] == ECHO)
        if "Casa" in echo.get("attributes", {}).get("options", []):
            break
        time.sleep(2)
    else:
        raise RuntimeError("El Echo aun no ofrece el pipeline Casa")
    ws({"type": "call_service", "domain": "select", "service": "select_option", "service_data": {"entity_id": ECHO, "option": "Casa"}})
    ws({"type": "call_service", "domain": "select", "service": "select_option", "service_data": {"entity_id": "select.echo_salon_assistant_1_reply_delivery", "option": "Streamed"}})
    states = ws({"type": "get_states"})
    if next(e["state"] for e in states if e["entity_id"] == ECHO) != "Casa":
        raise RuntimeError("El Echo no confirmo el asistente Casa")
    print("Echo asignado a Casa: " + pipeline_id, flush=True)


def main():
    parser = argparse.ArgumentParser()
    selection = parser.add_mutually_exclusive_group()
    selection.add_argument("--instructions-only", action="store_true")
    selection.add_argument("--stt-engine", choices=("stt.casa_groq_stt", "stt.faster_whisper"))
    args = parser.parse_args()
    if args.stt_engine:
        select_stt(args.stt_engine)
        return
    registry = ws({"type": "config/entity_registry/list"})
    if args.instructions_only:
        configure_agent(registry)
        return
    configure_agent(registry)
    configure_exposure(ws({"type": "get_states"}))
    connect(configure_pipeline(registry))


if __name__ == "__main__":
    try:
        main()
    except Exception:
        sys.exit("Configuracion de voz incompleta; revisar el ultimo paso confirmado, sin borrar ni restablecer dispositivos")
