# Tarjeta con datos sintéticos

`index.html` carga la tarjeta real con entidades y servicios simulados. No conecta con HA. Usa Chrome headless a 1280×800, sin GPU, con puerto de depuración 19328 y `--allow-file-access-from-files`; ejecuta `node test/echo-v5/verificar.mjs`. El verificador cierra ese navegador al terminar. Las capturas y `checks.json` se regeneran desde estos datos anónimos.

Comprueba controles táctiles, luces, brillo por pulsación larga y botón alternativo, confirmación de cierre, ausencia de apertura, scroll, otras estancias, errores de servicio, destino Spotify y ausencia de mutaciones/repintados en reposo. Los tiempos del navegador no miden latencia física del Echo.
