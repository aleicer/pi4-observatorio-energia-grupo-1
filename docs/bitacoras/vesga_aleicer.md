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

_Alrededor de 6 horas para el desarrollo_

## Semanas 3 y 4 (26 de octubre – 8 de noviembre de 2026) – EA2

**Rol:** Líder técnico / Data Engineer y Analytics Engineer

### ¿Qué hice?

- **Base de la EA2:** integré el código de la clase del 26 de octubre (`src/silver/`, `src/quality/`, `dbt/`, `tests/test_limpieza.py`) y agregué las herramientas comunes de plata (`src/silver/comun.py`: medir cada regla, cuarentena con motivo y guardar validando con pandera), el reporte de calidad generado por el código (`src/silver/reporte.py`) y el comando único `python -m src.transformar`. → [PR #9](https://github.com/aleicer/pi4-observatorio-energia-grupo-1/pull/9)
- **EnerAndes:** amplié la limpieza de la clase a las 4 hojas del Excel y las uní en una sola tabla: encabezados distintos, títulos encima, totales, fechas en 4 formatos (incluido `01/03/2026` = marzo y meses en inglés como `aug-24`), MWh a kWh, municipios con DIVIPOLA, duplicados y cuarentena. 19 reglas. → [PR #11](https://github.com/aleicer/pi4-observatorio-energia-grupo-1/pull/11)
- **XM e IDEAM:** XM de 24 columnas por hora a una fila por hora (precio, demanda y 5,9 millones de filas de generación por planta), hidrología y catálogo de plantas; IDEAM con fechas, números, estaciones con su municipio y cuarentena de valores imposibles. → [PR #12](https://github.com/aleicer/pi4-observatorio-energia-grupo-1/pull/12)
- **Capa oro:** el esquema estrella en dbt con 6 hechos y 6 dimensiones (`dim_fecha` con fase ENSO), el grano de cada hecho en `schema.yml`, 76 pruebas y `docs/modelo_dimensional.md` con el diagrama. → [PR #17](https://github.com/aleicer/pi4-observatorio-energia-grupo-1/pull/17)
- Revisé y aprobé los PRs de Jaider y Guillermo, actualicé el README y creé la tag `ea2`.

### ¿Qué aprendí?

- Que limpiar no es solo corregir: cada regla se **mide** antes y después, y lo que no se puede corregir se aparta en **cuarentena** con su motivo en vez de borrarlo.
- Que pandera funciona como un contrato: si una tabla no cumple sus reglas, no se guarda, y así ningún dato sucio llega a la capa oro.
- Que el **grano** es la decisión más importante del modelo dimensional: define qué representa cada fila y qué se puede sumar. Por eso cada hecho tiene su prueba de grano en dbt.
- Que las pruebas `relationships` de dbt encuentran problemas reales: 10 plantas generaban energía pero no estaban en el catálogo de XM.

### Bloqueos y cómo los resolví

- **Fechas ambiguas:** `01/03/2026` podía ser el 3 de enero o el 1 de marzo. La hoja 2026 usa día/mes/año, así que se toma el segundo número como mes, y quedó probado con pytest.
- **Sensores en cero en el IDEAM:** 605 días con temperatura mínima de 0 °C en Medellín y Rionegro. En lugar de dejarlos (bajarían el promedio) o inventar un valor, se mandaron a cuarentena.
- **Conflictos en `esquemas.py`:** dos compañeros agregaban su esquema al final del mismo archivo. Los esquemas de XM e IDEAM los separé en archivos propios para evitar más choques.

### Horas dedicadas

_Alrededor de 4 horas_
