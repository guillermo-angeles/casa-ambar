# Historial de cambios

Las releases del proyecto usan `MAYOR.MENOR.PARCHE`, con etiquetas Git `vX.Y.Z`. Cada entrada publicada corresponde a una release y a un commit concreto. Los componentes mantienen sus propias versiones; la versión del proyecto identifica el conjunto de fuentes y configuración. Durante la serie `0.x` pueden producirse cambios incompatibles, que se indicarán aquí.

## Sin publicar

Los cambios que se incorporen después de `v0.1.0` se anotarán aquí hasta la próxima release.

## [0.1.0] - 2026-10-21

Primera release del proyecto. Distribución experimental con ejemplos anónimos; no equivale a una actualización de una instalación doméstica existente.

### Añadido

- Configuración de ejemplo para Home Assistant, modos de casa y automatizaciones de iluminación, presencia y avisos.
- Panel táctil de 1280 × 800 con estancias mediante scroll horizontal, regulación de brillo, controles de música y capturas de demostración en el README.
- Casa Dashcast, adaptador Groq STT y herramientas de preparación del pipeline de voz con Anthropic y Piper.
- Parche experimental de interfaz de voz sobre TECHO5, con construcción local y pruebas seleccionadas.
- Integración Nuki Bluetooth de terceros, con licencias conservadas.
- Entorno Docker con dispositivos simulados, pruebas de herramientas y demos visuales con datos sintéticos.
- Guía de contribución, documentación de instalación, reversión y privacidad; licencia MIT para el código propio y avisos de terceros.
- `VERSION` para la release del proyecto y manifiesto con versiones de tarjeta, dashcast y Groq STT.
- Despliegue con `--version`, comprobación de etiqueta y árbol limpio, y opción `--check` sin acceso a dispositivos.
- Registro por despliegue con commit, alcance, copia completa de HA y versiones previamente registradas; estado separado por componente y bloqueo tras cambios incompletos.
- Verificación de procedencia y hash del binario nativo antes de desplegarlo.

### Corregido

- La reversión exige seleccionar el identificador de un despliegue y su copia concreta; deja de elegir la copia más antigua por nombre.

### Versiones y validación

Tarjeta `2.1.2`, Casa Dashcast `0.2.0`, Casa Groq STT `0.1.0`. Configuración probada con HA `2026.10.2`; parche nativo basado en el commit TECHO5 fijado en `tools/build_echo_voice.sh`.

El parche de voz sigue siendo experimental. Las pruebas locales no sustituyen la validación física ni constituyen una instalación permanente en el Echo. La restauración de HA no restaura el ejecutable externo del Echo; dashcast tiene además una copia separada de sus fuentes. Consulta [despliegue y reversión](docs/DESPLIEGUE.md).
