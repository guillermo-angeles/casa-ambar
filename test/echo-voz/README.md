# Prototipo de voz

Sirve el repositorio por HTTP en localhost:18766 y abre `/test/echo-voz/`. Incluye un dashboard con datos sintéticos y estados de escucha, preparación, respuesta, consulta web y error. Los controles de demostración quedan fuera del lienzo 1280×800. No controla HA ni usa un micrófono real.

`verificar.mjs` requiere un Chrome de pruebas con depuración en localhost:19329. Comprueba encaje, cierre táctil, errores y repintados en reposo, y regenera las capturas. La implementación nativa y sus límites están en `firmware/techo5/README.md`.
