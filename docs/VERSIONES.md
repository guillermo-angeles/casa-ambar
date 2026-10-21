# Versiones y releases

`VERSION` contiene la versión del proyecto, sin el prefijo `v`. Su etiqueta Git es `vX.Y.Z` y apunta al commit exacto que se publica. La misma versión figura en el changelog y en los registros de despliegue. Una etiqueta publicada no se mueve ni se reutiliza: una corrección requiere otra versión.

## Política de versiones

Seguimos [SemVer](https://semver.org/lang/es/) para comunicar cambios en el contrato documentado: opciones de herramientas, configuración y comportamiento de los paquetes. A partir de `1.0.0`, un cambio incompatible incrementará MAYOR, una función compatible MENOR y una corrección compatible PARCHE. Durante `0.x`, los cambios incompatibles incrementan MENOR y se explican en el changelog; no se garantiza todavía estabilidad del contrato.

Las versiones privadas pueden añadir un sufijo, como `0.1.0-casa.1`. Los despliegues aceptan números sin ceros iniciales y sufijos de prerelease; no se usan metadatos `+build` para identificar releases desplegables.

| Nivel | Ejemplo en v0.1.0 | Finalidad |
| --- | --- | --- |
| Proyecto | `VERSION`: `0.1.0`, tag `v0.1.0` | Identificar el conjunto de fuentes, configuración y herramientas |
| Tarjeta | `2.1.2` | Caché del JS; debe coincidir con el `?v=` del snippet |
| Casa Dashcast | `0.2.0` | Actualización o reconstrucción de la app HA |
| Casa Groq STT | `0.1.0` | Versión de la integración personalizada |

La versión del proyecto no sustituye las versiones de HA o TECHO5 ni las cambia automáticamente. Un despliegue parcial solo actualiza el alcance registrado. Los servicios externos, modelos y dependencias descargadas siguen sujetos a disponibilidad: un tag fija nuestras fuentes y referencias declaradas, no promete que todo proveedor externo sea inmutable.

## Preparar la siguiente release

1. Integra las pull requests y reúne sus cambios en «Sin publicar» de `CHANGELOG.md`. Decide la nueva versión, actualiza `VERSION` y traslada esas notas a `## [X.Y.Z] - AAAA-MM-DD`, conservando una sección vacía para lo siguiente.
2. Revisa las versiones internas que realmente hayan cambiado. Ejecuta las pruebas apropiadas de [CONTRIBUTING.md](../CONTRIBUTING.md), incluida `test/docker/run.sh` con `FALLOS: []` para la release, y revisa privacidad y licencias. Describe los límites de validación física en las notas.
3. Confirma e integra la preparación en `main`. Antes de publicar, exige un checkout limpio, sin credenciales ni cambios privados. Obtén autorización del responsable para publicar; crear una release no autoriza desplegarla en dispositivos.

## Etiquetar y publicar

Ejemplo de la primera release, después de integrar y validar su commit:

```sh
git switch main
git pull --ff-only
git tag -a v0.1.0 -m 'Casa Ámbar v0.1.0'
```

Genera el manifiesto y las notas fuera del repositorio para mantenerlo limpio:

```sh
release_output_dir="$(mktemp -d)"
/usr/bin/python3 -I tools/release.py verify v0.1.0 > "$release_output_dir/release.json"
/usr/bin/python3 -I tools/release.py notes v0.1.0 > "$release_output_dir/notes.md"
```

Tras revisar las notas, publica el tag existente y usa exactamente su changelog. `--verify-tag` evita que GitHub cree una etiqueta sobre otro commit por defecto:

```sh
git push origin refs/tags/v0.1.0
gh release create v0.1.0 "$release_output_dir/release.json" \
  --verify-tag --title 'Casa Ámbar v0.1.0' \
  --notes-file "$release_output_dir/notes.md" --prerelease
```

La primera release se marca como prerelease por su estado experimental. En versiones futuras revisa si sigue siendo apropiado. GitHub proporciona los archivos de fuentes asociados al tag; el despliegue actual requiere un clon Git para comprobar commit, etiqueta y cambios locales. No adjuntes `.env.local`, registros de despliegue, configuración doméstica ni un binario local del Echo como artefactos de la release.

Comprueba después la release publicada, su tag, el commit y el manifiesto adjunto. Mantén el tag intacto aunque haya que corregir una nota; publica otra versión si cambia el código. Fuente del procedimiento: [gestión de releases de GitHub](https://docs.github.com/en/repositories/releasing-projects-on-github/managing-releases-in-a-repository).

## Instalar y volver atrás

Sigue [DESPLIEGUE.md](DESPLIEGUE.md) para seleccionar una etiqueta, adaptar una instalación mediante una versión privada y desplegar con copia previa. `tools/deploy.sh --version v0.1.0 --check` comprueba únicamente la identidad local, sin leer credenciales ni conectar con HA.

Los registros por despliegue relacionan versión, commit, alcance, copia y estado anterior. No son lecturas continuas del dispositivo: una intervención manual o un reinicio del Echo puede cambiar el estado real. La restauración exige escoger el registro exacto y confirmar su impacto; no basta con cambiar el checkout a un tag anterior ni con reducir `VERSION`.
