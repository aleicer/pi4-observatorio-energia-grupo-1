# Bitácora – Aleicer Vesga Rueda

## Semana 2 (19 – 25 de octubre de 2026)

**Rol esta semana:** Líder técnico / Data Engineer (y Analytics Engineer)

### ¿Qué hice?

- Creé el repositorio a partir del código de la clase, protegí la rama `main`, invité a Jaider y a Guillermo y armé el tablero de GitHub Projects con las tareas.
- **XM:** amplié el rango a 2024-2026 y agregué la generación por planta (`Gene`/`Recurso`), los aportes hídricos (`AporEner`) y el catálogo de plantas (`ListadoRecursos`). El catálogo va por el endpoint `lists`, sin fechas y con otra estructura (`ListEntities`), así que extendí `aplanar()` y agregué `extraer_lista()`. → [PR #1](https://github.com/aleicer/pi4-observatorio-energia-grupo-1/pull/1)
- **IDEAM:** amplié la precipitación desde 2025 y agregué la temperatura del aire (media, mínima y máxima por estación y día), con la agregación hecha en el servidor con SoQL. Agregué un guardado parcial por semana para poder continuar si la descarga se corta. → [PR #4](https://github.com/aleicer/pi4-observatorio-energia-grupo-1/pull/4)
- **Muestras y perfilamiento:** scripts `src/muestras.py` (200 filas por archivo en `data/sample/`) y `src/perfilamiento.py` (genera `docs/perfilamiento.md`). → [PR #5](https://github.com/aleicer/pi4-observatorio-energia-grupo-1/pull/5)
- Revisé y aprobé los PRs de mis compañeros (#2, #3, #6 y #7), escribí el README final y creé la tag `ea1`.

### ¿Qué aprendí?

- Que la documentación de una API puede fallar: el catálogo de XM dice `.../list`, pero el endpoint que funciona es `.../lists`. Probar a mano antes de programar ahorra tiempo.
- La diferencia entre ejecutar un archivo (`python src/extract/xm.py`) y ejecutarlo como módulo (`python -m src.extract.xm`): solo la segunda encuentra el paquete `src`.
- Cómo funciona la protección de ramas en GitHub: el autor de un PR no puede aprobarlo, y un comentario no es lo mismo que una aprobación (*Approve*).

### Bloqueos y cómo los resolví

- **El IDEAM es muy lento** (92 semanas por dataset): lo resolví guardando cada semana en una carpeta temporal, así un corte no obliga a empezar de cero.
- **No veía la opción de aprobar los PRs:** estaba dejando comentarios. La aprobación está en *Files changed → Submit review → Approve*.

### Horas dedicadas

_(completar)_
