import argparse
import ctypes
import datetime
import json
import os
from pathlib import Path
import re
import subprocess
import tempfile
from urllib.parse import quote

SSH = ["ssh", "-i", os.environ.get("SSH_KEY", str(Path.home() / ".ssh/id_ed25519")), "-o", "IdentitiesOnly=yes", "-o", "BatchMode=yes", "-o", "ConnectTimeout=5"]
ECHO_HOST = os.environ.get("ECHO_HOST", "echo.invalid")
ECHO = "root@" + ECHO_HOST
HA = "root@" + os.environ.get("HA_HOST", "homeassistant.invalid")
SERVICE = os.environ.get("CAMERA_TOKEN_SERVICE", "casa-ambar-camera").encode()


def run(args, data=None, timeout=30):
    try:
        result = subprocess.run(args, input=data, capture_output=True, timeout=timeout)
    except (OSError, subprocess.TimeoutExpired):
        raise RuntimeError("La operación privada no pudo completarse") from None
    if result.returncode:
        raise RuntimeError("La operación privada terminó con error")
    return result.stdout


def credentials():
    state = json.loads(run(SSH + [ECHO, "cat /data/misc/techo5/state.json"]))
    camera = state.get("cam_stream", {})
    password = camera.get("pass", "")
    if len(password) < 12:
        raise RuntimeError("La cámara todavía no tiene una contraseña válida guardada")
    return camera.get("user") or "camera", password


def keychain_store(account, password):
    security = ctypes.CDLL("/System/Library/Frameworks/Security.framework/Security")
    core = ctypes.CDLL("/System/Library/Frameworks/CoreFoundation.framework/CoreFoundation")
    ptr, size, text = ctypes.c_void_p, ctypes.c_uint32, ctypes.c_char_p
    security.SecKeychainFindGenericPassword.argtypes = [ptr, size, text, size, text, ctypes.POINTER(size), ctypes.POINTER(ptr), ctypes.POINTER(ptr)]
    security.SecKeychainAddGenericPassword.argtypes = [ptr, size, text, size, text, size, ptr, ctypes.POINTER(ptr)]
    security.SecKeychainItemModifyAttributesAndData.argtypes = [ptr, ptr, size, ptr]
    for name in ["SecKeychainFindGenericPassword", "SecKeychainAddGenericPassword", "SecKeychainItemModifyAttributesAndData"]:
        getattr(security, name).restype = ctypes.c_int32
    core.CFRelease.argtypes = [ptr]
    account_bytes, password_bytes = account.encode(), password.encode()
    data = ctypes.create_string_buffer(password_bytes)
    item = ptr()
    status = security.SecKeychainFindGenericPassword(None, len(SERVICE), SERVICE, len(account_bytes), account_bytes, None, None, ctypes.byref(item))
    try:
        if status == 0:
            status = security.SecKeychainItemModifyAttributesAndData(item, None, len(password_bytes), data)
        elif status == -25300:
            status = security.SecKeychainAddGenericPassword(None, len(SERVICE), SERVICE, len(account_bytes), account_bytes, len(password_bytes), data, None)
        if status != 0:
            raise RuntimeError("No se pudo guardar el acceso en el Llavero (estado %d)" % status)
    finally:
        if item:
            core.CFRelease(item)


def merge_secret(old, source):
    line = "echo_camera_rtsp: " + json.dumps(source, ensure_ascii=False)
    found = re.search(r"(?m)^echo_camera_rtsp\s*:([^\n]*)$", old)
    if found:
        try:
            json.loads(found.group(1).strip())
        except (ValueError, TypeError):
            raise RuntimeError("El secreto existente requiere revisión; no se ha sobrescrito") from None
        return old[:found.start()] + line + old[found.end():]
    return old.rstrip("\n") + ("\n" if old else "") + line + "\n"


def install_secret(uri):
    old = run(SSH + [HA, "test ! -f /config/secrets.yaml || cat /config/secrets.yaml"]).decode()
    updated = merge_secret(old, "-rtsp_transport tcp -i " + uri)
    if old != updated:
        stamp = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
        backup = "/config/secrets.yaml.pre-echo-" + stamp
        target = "/config/secrets.yaml.echo-" + stamp
        command = "umask 077; if [ -f /config/secrets.yaml ]; then cp -p /config/secrets.yaml " + backup + " || exit 1; fi; cat > " + target + " && chmod 600 " + target + " && mv " + target + " /config/secrets.yaml"
        run(SSH + [HA, command], updated.encode())
    print("Acceso guardado en Llavero y secreto privado de HA preparado")


def probe(uri):
    with tempfile.TemporaryDirectory(prefix="ha-echo-camera-") as directory:
        path = Path(directory) / "input.ffconcat"
        path.write_text("ffconcat version 1.0\nfile '" + uri + "'\noption rtsp_transport tcp\noption timeout 5000000\n")
        path.chmod(0o600)
        common = ["-v", "error", "-protocol_whitelist", "file,rtsp,tcp,udp,rtp", "-safe", "0", "-f", "concat", "-i", str(path)]
        raw = run(["/opt/homebrew/bin/ffprobe"] + common + ["-show_entries", "stream=codec_name,width,height,r_frame_rate", "-of", "json"], timeout=20)
        streams = json.loads(raw).get("streams", [])
        if not any(s.get("width", 0) > 0 and s.get("height", 0) > 0 for s in streams):
            raise RuntimeError("El stream no devuelve vídeo válido")
        print(json.dumps({"video": streams}, ensure_ascii=False))
        progress = run(["/opt/homebrew/bin/ffmpeg"] + common + ["-nostats", "-progress", "pipe:1", "-frames:v", "5", "-vf", "scale=640:360,fps=10", "-c:v", "libx264", "-preset", "veryfast", "-threads", "2", "-an", "-f", "null", "-"], timeout=25).decode()
        frames = [int(n) for n in re.findall(r"(?m)^frame=(\d+)$", progress)]
        if not frames or max(frames) < 5:
            raise RuntimeError("No se pudieron convertir cinco fotogramas")
        print("RTSP autenticado y conversión H.264 640x360 comprobados")


def main():
    parser = argparse.ArgumentParser()
    modes = parser.add_mutually_exclusive_group(required=True)
    modes.add_argument("--probe", action="store_true")
    modes.add_argument("--install-secret", action="store_true")
    args = parser.parse_args()
    if ECHO_HOST.endswith(".invalid") or HA.endswith(".invalid"):
        raise RuntimeError("Configura ECHO_HOST y HA_HOST")
    account, password = credentials()
    keychain_store(account, password)
    uri = "rtsp://" + quote(account, safe="") + ":" + quote(password, safe="") + "@" + ECHO_HOST + ":8554/camera"
    if args.probe:
        probe(uri)
    else:
        install_secret(uri)


if __name__ == "__main__":
    try:
        main()
    except (RuntimeError, ValueError):
        print("No se pudo completar el acceso privado a la cámara; no se muestran datos sensibles")
        raise SystemExit(1)
