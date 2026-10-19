# Contrato del ejemplo

Los YAML y la tarjeta usan un conjunto de entidades de demostración coherente con `test/docker/stubs.yaml`. Los nombres de habitaciones describen el ejemplo, no una instalación que se descubra automáticamente. Adapta las referencias de todo `config/` y `tools/voice_setup.py` antes de desplegar.

| Función | Entidades de ejemplo |
| --- | --- |
| Modo | `input_select.modo_casa`, scripts `modo_dia`, `modo_tarde`, `modo_noche`, `modo_cine`, `modo_dormir`, `modo_fuera` |
| Presencia | `person.residente`, `notify.mobile_app_telefono_residente` |
| Luces | `light.lampara_sofa`, `light.lampara_comedor`, `light.lampara_pie`, `light.lampara_recibidor`, `light.led_cocina`, `light.lampara_dormitorio`, `light.led_tv` |
| Televisión | `media_player.tv_salon`, `button.tv_salon_encender` |
| Música | `media_player.spotify`, destino Spotify Connect `Echo Salón`, `script.spotify_favoritos` |
| Tiempo | `weather.aemet` y sensores AEMET referenciados en los paquetes |
| Echo | Entidades con prefijo `echo_salon`; confirma los nombres registrados en tu HA |
| Cámara | `camera.echo_salon_camera`, secreto `echo_camera_rtsp`; comprueba el ID concreto en los paquetes |

Los modos cambian iluminación y ambiente. La llegada puede encender el recibidor y sacar la casa de Fuera al detectar presencia o apertura manual de la cerradura. La salida puede pasar a Fuera. Los avisos notifican una cerradura sin cerrar, baterías bajas o copias atrasadas. Revisa disparadores y condiciones: son decisiones domésticas que debes adaptar a tu caso.

La tarjeta muestra salón y recibidor primero, seguidos por otras estancias mediante scroll horizontal. Las luces regulables abren una hoja de intensidad con pulsación larga en navegadores compatibles y con el botón de ajuste táctil como alternativa para TECHO5 Streamed. La música inicia biblioteca guardada en aleatorio o la playlist configurada en la tarjeta, únicamente si el destino está disponible.

No hay apertura automática ni control de apertura desde pantalla o agente. HomeKit se configura por separado: reutiliza bridges existentes y evita exponer dos veces un mismo accesorio. La cámara requiere alta manual en Casa; este proyecto no implementa HomeKit Secure Video.

La lista exacta de entidades de voz está en `tools/voice_setup.py`. Su configuración desactiva exposición automática y retira de Assist cualquier entidad fuera de esa lista. Revisa el impacto si ya utilizas otro asistente en la misma instancia.
