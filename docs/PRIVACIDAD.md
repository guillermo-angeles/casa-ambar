# Revisión de la distribución pública

Revisión local del 19 de octubre de 2026. Esta copia se preparó desde archivos versionados seleccionados y tiene historial Git nuevo. No se copiaron documentos operativos privados, historial previo, backups, bases de datos de HA, `.storage`, claves ni archivos ignorados de la instalación de pruebas.

Los nombres personales, localidad, direcciones de red, identificadores de presencia y notificaciones se sustituyeron por ejemplos. Hosts, servicios del Llavero, clave SSH, pipeline, localidad y hash del ejecutable se configuran por entorno. Las capturas incluidas proceden de pruebas sintéticas regeneradas y fueron revisadas visualmente. Las atribuciones públicas de terceros se conservan.

Validación de esta copia:

- Home Assistant en Docker: comprobación de configuración correcta y `FALLOS: []`; ocho pruebas Groq correctas. Avisos del entorno simulado: integraciones personalizadas, dependencia rich y selector de pantalla sin stub.
- Dieciséis pruebas de herramientas correctas, incluida configuración de red y ausencia de lectura del Llavero con WebSocket sin configurar. Sintaxis Python y shell correcta.
- Dashcast: `go test -race ./...` correcto. Pruebas táctiles de tarjeta y voz correctas; cero errores JS y repintados en reposo durante las ventanas medidas.
- Parche TECHO5: suites seleccionadas de funciones, hardware, configuración y actualización correctas; compilación ARMv7 correcta. No se ejecutó la suite global de TFLite ni se validó hardware en esta revisión.
- Escaneo offline con Gitleaks 8.30.1 y búsqueda adicional de identificadores privados: sin detecciones en los archivos preparados. El commit inicial se comprueba por separado antes de entregar la copia.

No detectar secretos no garantiza su ausencia absoluta. Esta revisión cubre la copia preparada, no futuros cambios. No añadas capturas reales, configuración de HA o datos del entorno de pruebas sin volver a revisarlos. Los patrones de exclusión de Git ayudan a prevenir publicaciones accidentales, pero no sustituyen una revisión.
