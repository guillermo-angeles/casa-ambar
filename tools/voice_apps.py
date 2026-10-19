import json
from pathlib import Path
import subprocess
import sys


ROOT = Path(__file__).resolve().parent
APPS = {
    "core_whisper": {"model": "small-int8", "language": "es", "beam_size": 1, "debug_logging": False},
    "core_piper": {"voice": "es_ES-davefx-medium", "debug_logging": False},
}


def supervisor(endpoint, method="get", data=None):
    command = {"type": "supervisor/api", "endpoint": endpoint, "method": method, "timeout": 480}
    if data is not None:
        command["data"] = data
    result = subprocess.run(
        ["/usr/bin/python3", "-I", str(ROOT / "ha_ws.py")],
        input=json.dumps([command]), text=True, capture_output=True, timeout=600,
    )
    if result.returncode:
        raise RuntimeError("No se pudo consultar Supervisor")
    response = json.loads(result.stdout)[0]
    if not response.get("success"):
        raise RuntimeError("Supervisor rechazo la operacion")
    return response.get("result") or {}


def main():
    installed = {app["slug"] for app in supervisor("/addons")["addons"]}
    for slug, settings in APPS.items():
        if slug not in installed:
            print("Instalando", slug, flush=True)
            supervisor(f"/addons/{slug}/install", "post")
        info = supervisor(f"/addons/{slug}/info")
        options = {**info["options"], **settings}
        if options != info["options"]:
            supervisor(f"/addons/{slug}/options", "post", {"options": options})
            if info["state"] == "started":
                supervisor(f"/addons/{slug}/restart", "post")
        if info["state"] != "started":
            supervisor(f"/addons/{slug}/start", "post")
        info = supervisor(f"/addons/{slug}/info")
        print(json.dumps({"app": slug, "version": info.get("version"), "state": info.get("state"), "ajustes": settings}), flush=True)


if __name__ == "__main__":
    try:
        main()
    except (RuntimeError, ValueError, KeyError, subprocess.TimeoutExpired):
        sys.exit("Preparacion de voz incompleta; revisar el estado de las apps en HA")
