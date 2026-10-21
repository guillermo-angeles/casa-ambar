# Instalación y reversión

Ejemplo orientado a HA OS/Supervisor, TECHO5 y herramientas de macOS. El entorno Docker es independiente y no instala nada en tus dispositivos. No ejecutes despliegues sin adaptar y revisar primero los archivos.

## Preparación

1. Ejecuta las pruebas de README. Adapta entidades, automatizaciones, notificaciones, dashboard y puertos HomeKit a tu instalación; revisa también `tools/voice_setup.py`. Si `configuration.yaml` ya tiene `homeassistant:` o `lovelace:`, integra sus claves antes de usar la fusión por marcadores: el script no resuelve claves YAML duplicadas.
2. Copia `.env.example` a `.env.local`, sustituye los hosts ficticios y carga sus variables con `source .env.local`. `HA_HOST` es el host SSH sin puerto; `HA_URL` es el origen HTTP(S) completo, incluyendo el puerto real. Configura `SSH_KEY`. El archivo privado está ignorado por Git. Las herramientas no cargan archivos de entorno automáticamente.
3. Guarda un token HA en el Llavero de macOS usando Acceso a Llaveros, como contraseña genérica con el servicio indicado en `HA_TOKEN_SERVICE`. Introduce las claves Anthropic/Groq en sus formularios de HA. No las escribas en `.env.local`, comandos, YAML versionados ni capturas.

## Seleccionar una versión

Los despliegues se ejecutan desde un clon Git, no desde el ZIP de fuentes de GitHub. Con la copia de trabajo limpia, selecciona una release publicada:

```sh
git fetch origin --tags
git switch --detach v0.1.0
tools/deploy.sh --version v0.1.0 --check
```

`--check` solo comprueba el estado local: etiqueta, commit, `VERSION`, changelog y versiones internas. No lee credenciales ni utiliza la red. El despliegue real vuelve a verificarlo antes de leer el token. Rechaza archivos modificados o nuevos sin confirmar; `.env.local` y los artefactos de compilación están ignorados.

La configuración pública contiene entidades de ejemplo. Si necesitas cambiar YAML, herramientas o tarjeta para tu vivienda, hazlo en un repositorio privado, confirma la adaptación y crea una versión propia, por ejemplo `0.1.0-casa.1` en `VERSION`, una entrada `## [0.1.0-casa.1] - AAAA-MM-DD` en el changelog y un tag `v0.1.0-casa.1` sobre ese commit. Despliega ese tag. Nunca publiques esas adaptaciones privadas ni muevas la etiqueta pública para hacerlas pasar por la release original.

## Despliegue

`tools/deploy.sh --version v0.1.0` solicita escribir `DESPLEGAR`, comprueba API/SSH, crea una copia completa mediante Supervisor, copia la configuración y ejecuta `ha core check` antes de reiniciar. Requiere SSH habilitado por el propietario y permisos suficientes. Si falla la comprobación restaura el archivo principal; los paquetes copiados pueden requerir restauración desde la copia completa. Guarda el identificador del despliegue y la copia mostrada por el script. La confirmación no se omite por seleccionar una versión.

Antes del cambio se registra la copia completa de Supervisor, con nombre e identificador real. El resultado se guarda en `/config/.casa-ambar/deployments/AAAAMMDD-HHMMSS.json`; `current.json` conserva los últimos despliegues correctos por alcance: configuración, dashcast, Groq o ajustes de voz. Un despliegue parcial no declara actualizado todo el sistema. Si nunca hubo un registro, el estado previo se indica como desconocido.

Se guarda además una copia local del registro en `~/.local/share/casa-ambar/deployments/`, configurable con `CASA_DEPLOY_LOG_DIR`. Son metadatos operativos privados: no los añadas a Git. Incluyen versiones, commit y copia de seguridad, sin tokens ni transcripciones.

Un cambio fallido conserva el estado previo como último registro correcto y mantiene `/config/.casa-ambar/incomplete`: los dispositivos pueden haber quedado parcialmente modificados. Otro despliegue se bloquea hasta restaurar o revisar ese estado. Un corte de proceso también puede dejar `/tmp/casa-ambar-deploy.lock`; comprueba que no hay otra operación en curso antes de retirarlo manualmente. No elimines marcadores para ignorar un fallo sin revisar el registro.

El script presupone una app local `local_casa_dashcast` ya instalada en `/local_apps/casa_dashcast`. Su creación inicial, opciones de conexión y credenciales se hacen en HA. `tools/deploy.sh --version v0.1.0 --dashcast-only` guarda el código anterior, reconstruye o actualiza y reinicia la app. Al cambiar la tarjeta, aumenta `VERSION` en el JS y el `?v=` del snippet; reinicia dashcast tras el despliegue.

Las opciones `--groq-stt`, `--voice-apps`, `--voice-setup`, `--voice-groq`, `--voice-whisper` y `--voice-instructions` preparan o ajustan voz con copia previa. Revisa los modelos y formularios reales antes de ejecutarlas: el código comprueba pasos de formulario y entidades y aborta si no coinciden. Para configurar el prompt debes definir `CASA_LOCALIDAD` con tu municipio; no se deduce de una dirección privada incluida en el código. `--voice-setup` puede modificar la exposición de otras entidades a Assist.

Para cámara, configura contraseña en TECHO5 antes de `--echo-camera`. La herramienta obtiene el acceso por SSH, lo guarda en el Llavero y en `secrets.yaml` privado, y no imprime su valor. Las herramientas de cámara y medidas de audio necesitan FFmpeg/FFprobe en `/opt/homebrew/bin`. No habilites acceso web anónimo ni publiques RTSP en internet.

## Pasos manuales en las interfaces

1. En HA, selecciona el dashboard Casa como predeterminado para el usuario de pantalla y asigna el pipeline Casa al Echo si no se ha confirmado automáticamente. Verifica reloj, clima, tacto y audio en el dispositivo real.
2. En Spotify, habilita el destino Connect del Echo y comprueba que su nombre coincide con el configurado. En la app móvil de HA, concede ubicación en segundo plano si quieres usar presencia.
3. En HomeKit, integra modos y cámara revisando antes los bridges existentes. No dupliques accesorios. El alta de cámara requiere emparejamiento manual; no borres paneles o accesorios anteriores sin revisar sus dependencias.

## Reversión

Selecciona el identificador exacto de un despliegue:

```sh
tools/rollback.sh --deployment AAAAMMDD-HHMMSS
```

La herramienta muestra la copia completa y las versiones anteriores registradas, explica que se perderán los cambios de HA posteriores a esa copia y exige escribir `REVERTIR`. Usa el identificador de copia guardado en ese registro; no elige copias por fecha, nombre o versión aproximada. También puedes restaurar la copia seleccionada desde la interfaz de HA. Si la restauración requiere descifrado, introdúcelo allí; no pases contraseñas por comandos ni las publiques.

La herramienta solo confirma que Supervisor ha aceptado la restauración: verifica después el arranque y los componentes en HA. La copia incluye la configuración y metadatos anteriores; no ejecuta borrados individuales de paquetes. Una restauración completa puede afectar otros cambios de tu instalación, por lo que requiere la autorización de su propietario.

Los registros `--dashcast-only` y `--echo-voice` no admiten la reversión genérica: HA no basta para restaurar todos sus archivos externos. Para dashcast conserva `/config/casa-dashcast-source-pre-AAAAMMDD-HHMMSS.tgz` además de la copia HA y restaura las fuentes de la app bajo supervisión del propietario; revisa su versión instalada antes de reconstruir. Para el Echo, `tools/rollback.sh --echo-voice` retira el montaje temporal y recupera su ejecutable persistente; no promete recuperar otro montaje temporal anterior. El binario anterior también se guarda localmente según [firmware/techo5](../firmware/techo5/README.md).

`tools/rollback.sh --voice-stt --version v0.1.0` vuelve a Whisper mediante un nuevo despliegue registrado; no restaura todo el pipeline anterior. Después de cualquier reversión externa, comprueba o actualiza los metadatos con evidencia real antes de otro despliegue; un registro previo no es una consulta del estado vivo. Ningún comando de esta guía debe usarse para desemparejar HomeKit.

Fuentes oficiales de los comandos de copias: [documentación de HA OS](https://www.home-assistant.io/common-tasks/os/#backups), [creación en HA CLI](https://github.com/home-assistant/cli/blob/master/cmd/backups_new.go) y [restauración en HA CLI](https://github.com/home-assistant/cli/blob/master/cmd/backups_restore.go).
