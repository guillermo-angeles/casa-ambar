# Cómo colaborar en Casa Ámbar

Puedes contribuir con correcciones, mejoras táctiles, rendimiento, integraciones, pruebas o documentación. Para cambios grandes, abre primero una issue explicando el problema y el resultado esperado, para acordar el alcance antes de implementarlos.

## Preparar una contribución

1. Crea un fork del repositorio y una rama descriptiva, por ejemplo `fix/brillo-tactil` o `feat/nueva-estancia`.
2. Haz un cambio acotado y pruébalo con datos simulados. Mantén la configuración particular de tu vivienda fuera del repositorio.
3. Abre una pull request contra `main` con el problema, el comportamiento resultante y las comprobaciones realizadas. Si cambia la interfaz, adjunta capturas anónimas e indica si has probado un Echo físico o solo el navegador.

## Comunicar un problema

Incluye versiones de HA, TECHO5 y componente afectado, pasos para reproducirlo y resultado esperado frente al observado. Añade únicamente el fragmento de log necesario, revisado y anonimizado. Si no tienes hardware para verificar algo, indícalo; una prueba de navegador no demuestra latencia física ni funcionamiento del micrófono.

No adjuntes tokens, contraseñas, archivos `.env.local`, `secrets.yaml`, `.storage`, backups ni imágenes de cámaras reales. Sustituye nombres personales, ubicación, hosts e identificadores de dispositivos por ejemplos antes de compartir una captura o un log. Las exclusiones de Git no protegen el contenido pegado en una issue o pull request.

## Criterios del proyecto

- Interfaz táctil a 1280 × 800, con controles amplios para el dedo. Conserva el repintado incremental y evita animaciones, transiciones, desenfoques y trabajo continuo en reposo. Prioriza salón y recibidor; las demás estancias se recorren con scroll horizontal.
- No añadas apertura o desbloqueo de cerraduras por voz, automatización o pantalla. El cierre desde la tarjeta exige confirmación. No expongas cerraduras o cámaras al agente, ni crees accesorios HomeKit duplicados o procedimientos que publiquen HA en internet.
- Verifica opciones, entidades y servicios en documentación oficial o en un entorno de pruebas real. Evita cambios ajenos al objetivo de la pull request, conserva licencias de terceros y escribe comentarios solo cuando expliquen un motivo que el código no permita deducir.

## Qué pruebas ejecutar

Elige las comprobaciones según el cambio; para documentación basta con revisar texto, enlaces, imágenes y privacidad, sin arrancar dispositivos ni desplegar.

| Cambio | Comprobaciones |
| --- | --- |
| Paquetes YAML, automatizaciones o integración Groq | `test/docker/run.sh`: configuración válida y `FALLOS: []`; incluye las pruebas Groq |
| Herramientas Python | `/usr/bin/python3 -I -m unittest discover -s test/tools` |
| Dashcast | Con Go 1.26, `cd apps/dashcast/src && go test -race ./...` |
| Tarjeta táctil | Demo y verificador de [test/echo-v5](test/echo-v5/README.md) |
| Prototipo de voz | Demo y verificador de [test/echo-voz](test/echo-voz/README.md) |
| Parche nativo de voz | Construcción y suites seleccionadas con `tools/build_echo_voice.sh`; detalles en [firmware/techo5](firmware/techo5/README.md) |

Docker genera su configuración de pruebas ignorada por Git y usa dispositivos simulados. No incluyas esos archivos en un commit. Las pruebas de navegador requieren un Chrome aislado con los puertos que indican sus instrucciones; los verificadores cierran ese navegador al terminar.

Si modificas `config/www/casa-ambar/casa-ambar-card.js`, aumenta `VERSION` y el `?v=` de `config/configuration.snippet.yaml`. Regenera las capturas afectadas desde las demos anónimas y documenta cualquier límite de validación. Para cambios visibles de comportamiento, añade una entrada en la sección «Sin versión» de [CHANGELOG.md](CHANGELOG.md).

## Commits, despliegue y licencia

Usa mensajes descriptivos, preferiblemente con prefijos como `fix:`, `feat:`, `docs:` o `test:`. La pull request debe explicar por qué hace falta el cambio y qué lo valida; no incluyas datos personales de una instalación ni identificadores privados de sesiones de trabajo.

Las contribuciones se revisan mediante pull requests. No ejecutes herramientas de despliegue como parte de las pruebas ni sobre una instalación ajena. Los despliegues requieren autorización del propietario y siguen [el procedimiento con copia y reversión](docs/DESPLIEGUE.md); desemparejar HomeKit puede romper accesorios y automatizaciones.

Las aportaciones propias se distribuyen bajo [MIT](LICENSE). Conserva los avisos originales si modificas código de terceros; consulta [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md). No es necesario disponer de un Echo para contribuir a documentación o pruebas locales.
