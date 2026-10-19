import asyncio
import json
import sys

import aiohttp

BASE = "http://localhost:8123"
CLIENT = BASE + "/"
USER, PASS = "test", "test-" + "pw-contenedor"
MODOS = {"dia": "Día", "tarde": "Tarde", "noche": "Noche", "cine": "Cine", "dormir": "Dormir", "fuera": "Fuera"}
fails = []


def check(ok, msg):
    print(("OK   " if ok else "FAIL ") + msg)
    if not ok:
        fails.append(msg)


async def main():
    async with aiohttp.ClientSession() as s:
        for _ in range(60):
            try:
                async with s.get(BASE + "/api/onboarding") as r:
                    if r.status == 200:
                        steps = await r.json()
                        break
            except aiohttp.ClientError:
                pass
            await asyncio.sleep(2)
        pending = [x["step"] for x in steps if not x["done"]]
        if "user" in pending:
            async with s.post(BASE + "/api/onboarding/users", json={"client_id": CLIENT, "name": "Test", "username": USER, "password": PASS, "language": "es"}) as r:
                code = (await r.json())["auth_code"]
        else:
            code = None
        if code:
            async with s.post(BASE + "/auth/token", data={"grant_type": "authorization_code", "code": code, "client_id": CLIENT}) as r:
                tok = (await r.json())["access_token"]
            h = {"Authorization": "Bearer " + tok}
            for step, body in (("core_config", {}), ("analytics", {}), ("integration", {"client_id": CLIENT, "redirect_uri": CLIENT})):
                async with s.post(BASE + "/api/onboarding/" + step, json=body, headers=h) as r:
                    print("onboarding", step, r.status)
        else:
            async with s.post(BASE + "/auth/login_flow", json={"client_id": CLIENT, "handler": ["homeassistant", None], "redirect_uri": CLIENT}) as r:
                fid = (await r.json())["flow_id"]
            async with s.post(BASE + "/auth/login_flow/" + fid, json={"username": USER, "password": PASS, "client_id": CLIENT}) as r:
                code = (await r.json())["result"]
            async with s.post(BASE + "/auth/token", data={"grant_type": "authorization_code", "code": code, "client_id": CLIENT}) as r:
                tok = (await r.json())["access_token"]
        h = {"Authorization": "Bearer " + tok}

        async with s.ws_connect(BASE + "/api/websocket") as ws:
            await ws.receive_json()
            await ws.send_json({"type": "auth", "access_token": tok})
            assert (await ws.receive_json())["type"] == "auth_ok"
            n = 0

            async def call(msg):
                nonlocal n
                n += 1
                await ws.send_json({"id": n, **msg})
                while True:
                    r = await ws.receive_json()
                    if r.get("id") == n:
                        return r

            async def state(e):
                async with s.get(BASE + "/api/states/" + e, headers=h) as r:
                    return await r.json() if r.status == 200 else None

            async def post_state(e, st):
                async with s.post(BASE + "/api/states/" + e, headers=h, json={"state": st}) as r:
                    return r.status

            async def service(dom, svc, data):
                async with s.post(f"{BASE}/api/services/{dom}/{svc}", headers=h, json=data) as r:
                    return r.status

            async def render(t):
                async with s.post(BASE + "/api/template", headers=h, json={"template": t}) as r:
                    return (await r.text()).strip()

            await post_state("device_tracker.stub_residente", "home")
            await asyncio.sleep(2)
            p = await state("person.residente")
            check(p and p["state"] == "home", "person.residente home (stub)")

            for dash in ("casa-ambar", "casa-pared"):
                r = await call({"type": "lovelace/config", "url_path": dash})
                ok = r["success"]
                views = r["result"].get("views", []) if ok else []
                check(ok and views, f"lovelace/config {dash}: {len(views)} vista(s)" if ok else f"lovelace/config {dash}: {r.get('error')}")
                if ok:
                    ents = set()

                    def walk(o):
                        if isinstance(o, dict):
                            for k, v in o.items():
                                if k in ("entity", "entity_id", "camera_image") and isinstance(v, str):
                                    ents.add(v)
                                walk(v)
                        elif isinstance(o, list):
                            for i in o:
                                walk(i)

                    walk(r["result"])
                    doms = ("light", "lock", "sensor", "binary_sensor", "switch", "script", "input_select", "input_boolean", "weather", "media_player", "camera", "todo", "person", "sun", "select", "event")
                    miss = []
                    for e in sorted(ents):
                        if e.split(".")[0] in doms and await state(e) is None:
                            miss.append(e)
                    print(f"  {dash}: entidades referenciadas sin estado:", miss)

            r = await call({"type": "frontend/get_themes"})
            th = r["result"]
            print("themes:", list(th["themes"].keys()))
            check("Ámbar" in th["themes"], "tema Ámbar listado")
            print("  modos del tema:", list(th["themes"].get("Ámbar", {}).get("modes", {}).keys()))

            await service("light", "turn_on", {"entity_id": ["light.lampara_sofa", "light.lampara_dormitorio"]})
            await service("input_boolean", "turn_on", {"entity_id": "input_boolean.stub_puerta_cerrada"})
            await asyncio.sleep(1)
            print("resumen:", await render("{{ states('sensor.casa_resumen') }} | {{ state_attr('sensor.casa_resumen','luces_encendidas') }} | {{ state_attr('sensor.casa_resumen','puerta') }} | {{ state_attr('sensor.casa_resumen','temperatura_exterior') }}"))

            esperado = {"Día": (4000, 100), "Noche": (2202, 30), "Cine": (2202, 15), "Dormir": (2202, 10), "Fuera": (2700, 0)}
            for key, modo in MODOS.items():
                before = await state("automation.casa_aplicar_modo")
                if (await state("input_select.modo_casa"))["state"] == modo:
                    await service("script", "modo_noche" if modo == "Día" else "modo_dia", {})
                    await asyncio.sleep(2)
                code_ = await service("script", "modo_" + key, {})
                await asyncio.sleep(3)
                m = await state("input_select.modo_casa")
                check(code_ == 200 and m["state"] == modo, f"script.modo_{key} -> modo_casa={m['state']}")
                t = await render("{{ states('sensor.casa_temperatura_color') }} K | {{ states('sensor.casa_brillo_objetivo') }} % | {{ states('sensor.casa_resumen') }}")
                print("   ", modo, t)

            r = await call({"type": "trace/list", "domain": "automation", "item_id": "casa_aplicar_modo"})
            traces = r.get("result", [])
            print("traces casa_aplicar_modo:", len(traces))
            bad = 0
            for t in traces:
                d = await call({"type": "trace/get", "domain": "automation", "item_id": "casa_aplicar_modo", "run_id": t["run_id"]})
                res = d["result"]
                err = res.get("error")
                to = res.get("trigger", "")
                if err:
                    bad += 1
                print("  ", t["run_id"][:6], t["state"], t.get("script_execution"), "error=" + str(err) if err else "", t.get("timestamp", {}).get("start", "")[11:19])
            check(len(traces) >= 5 and bad == 0, f"casa_aplicar_modo: {len(traces)} ejecuciones, {bad} con error")

            for item in ("casa_echo_pantalla_segun_modo", "casa_luz_sigue_al_sol"):
                r = await call({"type": "trace/list", "domain": "automation", "item_id": item})
                errs = []
                for t in r.get("result", []):
                    d = await call({"type": "trace/get", "domain": "automation", "item_id": item, "run_id": t["run_id"]})
                    if d["result"].get("error"):
                        errs.append(d["result"]["error"])
                print("  traces", item, len(r.get("result", [])), "errores:", errs)
            camera = await state("camera.echo_salon_camera")
            check(camera and camera["state"] not in ("unavailable", "unknown"), "Cámara Echo simulada disponible")
            async with s.get(BASE + "/api/camera_proxy/camera.echo_salon_camera", headers=h) as image:
                payload = await image.read()
                check(image.status == 200 and len(payload) > 100, "Snapshot de cámara Echo disponible para HomeKit")
            entries = await call({"type": "config_entries/get", "domain": "homekit"})
            camera_entries = [entry for entry in entries.get("result", []) if entry.get("title", "").startswith("Camara Echo Salon")]
            check(len(camera_entries) == 1 and camera_entries[0].get("state") == "loaded", "Un único accesorio HomeKit Echo arranca correctamente")

            async with s.post(BASE + "/api/states/media_player.spotify", headers=h, json={"state": "idle", "attributes": {"source_list": ["MacBook Pro"]}}) as response:
                check(response.status == 201, "Spotify simulado solo con destino MacBook Pro")
            result = await call({"type": "call_service", "domain": "script", "service": "spotify_favoritos"})
            traces = await call({"type": "trace/list", "domain": "script", "item_id": "spotify_favoritos"})
            runs = traces.get("result", [])
            check(result.get("success") and runs and all(run.get("script_execution") == "aborted" and run.get("last_step") == "sequence/1/then/0" for run in runs), "Favoritos aborta antes de seleccionar o reproducir si falta el Echo")

            print("lights:", {e: (await state(e))["state"] for e in ("light.lampara_sofa", "light.lampara_comedor", "light.lampara_dormitorio", "light.led_tv")})

    print("FALLOS:", fails)
    sys.exit(1 if fails else 0)


asyncio.run(main())
