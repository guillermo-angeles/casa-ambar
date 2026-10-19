# Instalación y reversión

Ejemplo orientado a HA OS/Supervisor, TECHO5 y herramientas de macOS. El entorno Docker es independiente y no instala nada en tus dispositivos. No ejecutes despliegues sin adaptar y revisar primero los archivos.

## Preparación

1. Ejecuta las pruebas de README. Adapta entidades, automatizaciones, notificaciones, dashboard y puertos HomeKit a tu instalación; revisa también `tools/voice_setup.py`. Si `configuration.yaml` ya tiene `homeassistant:` o `lovelace:`, integra sus claves antes de usar la fusión por marcadores: el script no resuelve claves YAML duplicadas.
2. Copia `.env.example` a `.env.local`, sustituye los hosts ficticios y carga sus variables con `source .env.local`. `HA_HOST` es el host SSH sin puerto; `HA_URL` es el origen HTTP(S) completo, incluyendo el puerto real. Configura `SSH_KEY`. El archivo privado está ignorado por Git. Las herramientas no cargan archivos de entorno automáticamente.
3. Guarda un token HA en el Llavero de macOS usando Acceso a Llaveros, como contraseña genérica con el servicio indicado en `HA_TOKEN_SERVICE`. Introduce las claves Anthropic/Groq en sus formularios de HA. No las escribas en `.env.local`, comandos, YAML versionados ni capturas.

## Despliegue

`tools/deploy.sh` solicita escribir `DESPLEGAR`, comprueba API/SSH, crea una copia completa mediante Supervisor, copia la configuración y ejecuta `ha core check` antes de reiniciar. Requiere SSH habilitado por el propietario y permisos suficientes. Si falla la comprobación restaura el archivo principal; los paquetes copiados pueden requerir restauración desde la copia completa. Guarda el identificador de copia mostrado por el script.

El script presupone una app local `local_casa_dashcast` ya instalada en `/local_apps/casa_dashcast`. Su creación inicial, opciones de conexión y credenciales se hacen en HA. `--dashcast-only` guarda el código anterior, reconstruye o actualiza y reinicia la app. Al cambiar la tarjeta, aumenta `VERSION` en el JS y el `?v=` del snippet; reinicia dashcast tras el despliegue.

Las opciones `--groq-stt`, `--voice-apps`, `--voice-setup`, `--voice-groq`, `--voice-whisper` y `--voice-instructions` preparan o ajustan voz con copia previa. Revisa los modelos y formularios reales antes de ejecutarlas: el código comprueba pasos de formulario y entidades y aborta si no coinciden. Para configurar el prompt debes definir `CASA_LOCALIDAD` con tu municipio; no se deduce de una dirección privada incluida en el código. `--voice-setup` puede modificar la exposición de otras entidades a Assist.

Para cámara, configura contraseña en TECHO5 antes de `--echo-camera`. La herramienta obtiene el acceso por SSH, lo guarda en el Llavero y en `secrets.yaml` privado, y no imprime su valor. Las herramientas de cámara y medidas de audio necesitan FFmpeg/FFprobe en `/opt/homebrew/bin`. No habilites acceso web anónimo ni publiques RTSP en internet.

## Pasos manuales en las interfaces

1. En HA, selecciona el dashboard Casa como predeterminado para el usuario de pantalla y asigna el pipeline Casa al Echo si no se ha confirmado automáticamente. Verifica reloj, clima, tacto y audio en el dispositivo real.
2. En Spotify, habilita el destino Connect del Echo y comprueba que su nombre coincide con el configurado. En la app móvil de HA, concede ubicación en segundo plano si quieres usar presencia.
3. En HomeKit, integra modos y cámara revisando antes los bridges existentes. No dupliques accesorios. El alta de cámara requiere emparejamiento manual; no borres paneles o accesorios anteriores sin revisar sus dependencias.

## Reversión

`tools/rollback.sh` solicita `REVERTIR`, restaura la configuración principal anterior y retira los archivos gestionados por este ejemplo. No restaura íntegramente paquetes que sobrescribieran archivos propios: para ese caso utiliza la copia completa de HA. No ejecutes esta reversión sobre una instalación ajena sin revisar sus rutas y copias.

La interfaz de voz nativa es experimental y se documenta en [firmware/techo5](../firmware/techo5/README.md). `tools/rollback.sh --echo-voice` retira su montaje temporal; `--voice-stt` devuelve la transcripción a Whisper local. Ningún comando de esta guía debe usarse para desemparejar HomeKit.
