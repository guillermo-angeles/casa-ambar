import argparse
import datetime
import hashlib
import json
from pathlib import Path
import re
import subprocess
import sys


VERSION_PATTERN = r"(?:0|[1-9][0-9]*)\.(?:0|[1-9][0-9]*)\.(?:0|[1-9][0-9]*)(?:-(?:0|[1-9][0-9]*|[0-9]*[a-zA-Z-][0-9a-zA-Z-]*)(?:\.(?:0|[1-9][0-9]*|[0-9]*[a-zA-Z-][0-9a-zA-Z-]*))*)?"
SCOPES = {
    "configuration": ("configuration",), "--echo-camera": ("configuration",),
    "--dashcast-only": ("dashcast",), "--groq-stt": ("groq_stt",),
    "--voice-apps": ("voice_apps",),
    "--voice-setup": ("voice_apps", "voice_pipeline", "voice_instructions"),
    "--voice-instructions": ("voice_instructions",), "--voice-groq": ("voice_stt",),
    "--voice-whisper": ("voice_stt",), "--echo-voice": ("echo_voice",),
}


def git(root, *args):
    return subprocess.check_output(["git", "-C", str(root), *args], stderr=subprocess.DEVNULL, text=True).strip()


def manifest(root, tag, native=False):
    version = (root / "VERSION").read_text().strip()
    if not re.fullmatch(VERSION_PATTERN, version) or tag != "v" + version:
        raise ValueError("La version solicitada no coincide con VERSION")
    commit = git(root, "rev-parse", "HEAD")
    if git(root, "status", "--porcelain", "--untracked-files=normal"):
        raise ValueError("El repositorio contiene cambios sin confirmar")
    if git(root, "rev-parse", "--verify", "refs/tags/" + tag + "^{commit}") != commit:
        raise ValueError("Selecciona el commit exacto de la etiqueta solicitada")
    if not re.search(r"^## \[" + re.escape(version) + r"\] - [0-9]{4}-[0-9]{2}-[0-9]{2}$", (root / "CHANGELOG.md").read_text(), re.M):
        raise ValueError("Falta la entrada versionada en CHANGELOG.md")
    card = re.search(r'^const VERSION = "([^"]+)";', (root / "config/www/casa-ambar/casa-ambar-card.js").read_text()).group(1)
    if "?v=" + card + "\n" not in (root / "config/configuration.snippet.yaml").read_text():
        raise ValueError("La version de la tarjeta no coincide con el recurso Lovelace")
    dashcast = re.search(r'^version: "([^"]+)"$', (root / "apps/dashcast/config.yaml").read_text(), re.M).group(1)
    groq = json.loads((root / "custom_components/casa_groq_stt/manifest.json").read_text())["version"]
    result = {"version": version, "tag": tag, "commit": commit, "components": {"card": card, "dashcast": dashcast, "groq_stt": groq}}
    if native:
        built = json.loads((root / "test/echo-voz/build-manifest.json").read_text())
        binary_hash = hashlib.sha256((root / "test/echo-voz/techo5-casa-arm").read_bytes()).hexdigest()
        patch_hash = hashlib.sha256((root / "firmware/techo5/casa-voice.patch").read_bytes()).hexdigest()
        if built != {"commit": commit, "binary_sha256": binary_hash, "patch_sha256": patch_hash}:
            raise ValueError("Compila el binario de voz desde esta version")
        result["native_binary_sha256"] = binary_hash
    return result


def release_notes(root, tag):
    version = (root / "VERSION").read_text().strip()
    if tag != "v" + version:
        raise ValueError("La version no coincide con VERSION")
    match = re.search(r"^## \[" + re.escape(version) + r"\] - [0-9]{4}-[0-9]{2}-[0-9]{2}\n(.*?)(?=^## |\Z)", (root / "CHANGELOG.md").read_text(), re.M | re.S)
    if not match or not match.group(1).strip():
        raise ValueError("No hay notas para esta version")
    return match.group(1).strip()


def backup_slug(response):
    if response.get("result") != "ok":
        raise ValueError("Supervisor no confirmo la copia completa")
    slug = response.get("data", {}).get("slug", "")
    if not re.fullmatch(r"[a-z0-9]{6,64}", slug):
        raise ValueError("La copia no tiene un identificador valido")
    return slug


def prepare(source, previous, mode, stamp, backup):
    if mode not in SCOPES or not re.fullmatch(r"[0-9]{8}-[0-9]{6}", stamp):
        raise ValueError("Operacion o identificador de despliegue no valido")
    if previous.get("schema") != 1 or not isinstance(previous.get("scopes"), dict):
        raise ValueError("El registro instalado no tiene el formato esperado")
    slug = backup_slug(backup)
    updated = {scope: {**source, "deployment": stamp} for scope in SCOPES[mode]}
    current = {"schema": 1, "scopes": {**previous["scopes"], **updated}}
    return {
        "schema": 1, "deployment": stamp, "created_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "status": "pending", "mode": mode, "source": source, "backup_slug": slug,
        "backup_name": "pre-casa-ambar-" + source["version"] + "-" + stamp,
        "previous": previous, "current": current,
    }


def rollback_info(record, deployment):
    if record.get("schema") != 1 or record.get("deployment") != deployment:
        raise ValueError("El registro no corresponde al despliegue solicitado")
    if record.get("status") not in ("applied", "failed", "pending"):
        raise ValueError("Estado del despliegue no reconocido")
    if record.get("mode") in ("--echo-voice", "--dashcast-only"):
        raise ValueError("Esta operacion requiere revertir tambien el Echo o las fuentes de dashcast; consulta DESPLIEGUE.md")
    slug = record.get("backup_slug", "")
    if not re.fullmatch(r"[a-z0-9]{6,64}", slug):
        raise ValueError("El registro no contiene una copia valida")
    return slug


def main():
    parser = argparse.ArgumentParser()
    commands = parser.add_subparsers(dest="command", required=True)
    verify = commands.add_parser("verify")
    verify.add_argument("tag")
    verify.add_argument("--native", action="store_true")
    verify.add_argument("--root", type=Path, default=Path(__file__).resolve().parent.parent)
    notes = commands.add_parser("notes")
    notes.add_argument("tag")
    notes.add_argument("--root", type=Path, default=Path(__file__).resolve().parent.parent)
    record = commands.add_parser("prepare")
    record.add_argument("source", type=Path)
    record.add_argument("previous", type=Path)
    record.add_argument("backup", type=Path)
    record.add_argument("mode")
    record.add_argument("stamp")
    finish = commands.add_parser("finish")
    finish.add_argument("record", type=Path)
    finish.add_argument("status", choices=("applied", "failed"))
    restore = commands.add_parser("rollback-info")
    restore.add_argument("record", type=Path)
    restore.add_argument("deployment")
    args = parser.parse_args()
    if args.command == "verify":
        result = manifest(args.root, args.tag, args.native)
    elif args.command == "notes":
        print(release_notes(args.root, args.tag))
        return
    elif args.command == "prepare":
        result = prepare(*[json.loads(path.read_text()) for path in (args.source, args.previous)], args.mode, args.stamp, json.loads(args.backup.read_text()))
    elif args.command == "finish":
        result = json.loads(args.record.read_text())
        result["status"] = args.status
        args.record.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n")
        result = result["current"]
    else:
        print(rollback_info(json.loads(args.record.read_text()), args.deployment))
        return
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    try:
        main()
    except (ValueError, KeyError, OSError, AttributeError, subprocess.CalledProcessError):
        sys.exit("No se pudo verificar la version o el registro; revisa etiqueta, VERSION, estado Git y formato de la copia")
