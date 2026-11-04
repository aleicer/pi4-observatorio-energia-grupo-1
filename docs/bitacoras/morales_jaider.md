# Bitácora – Jaider Morales

## Semana 2 (19 – 25 de octubre de 2026)

**Rol esta semana:** Data Quality Analyst

### 1. ¿Qué hice?

Durante esta semana me encargué de realizar pruebas automáticas para comprobar el funcionamiento de algunas partes del proyecto del Observatorio de Energía.

Primero tuve que preparar mi computador Mac para trabajar con el proyecto. Instalé Python 3.13, configuré el entorno virtual y las librerías necesarias. También trabajé con Git y GitHub para poder compartir mis avances con mis compañeros.

Después creé tres archivos de pruebas utilizando pytest:

**Pruebas de ventanas()**

En el archivo `tests/test_ventanas.py` hice tres pruebas para comprobar que la función dividiera correctamente los rangos de fechas en grupos de máximo 30 días.

También verifiqué que no se repitieran ni faltaran días y que funcionara correctamente con un rango de un solo día.

**Pruebas de aplanar()**

En el archivo `tests/test_aplanar.py` hice cuatro pruebas para revisar cómo se organizan los datos que llegan de XM.

Comprobé que la función pudiera trabajar con datos horarios, diarios y listas de recursos. También hice una prueba para verificar qué sucede cuando la respuesta está vacía.

Para realizar estas pruebas tuve que actualizar mi rama con los cambios que Aleicer había realizado en el código de XM.

**Pruebas de ya_existe()**

En el archivo `tests/test_idempotencia.py` realicé tres pruebas para comprobar que el programa pudiera reconocer cuándo un archivo ya había sido descargado.

También revisé que se pudiera volver a descargar cuando se utiliza la opción `forzar` y que el programa identificara cuando un archivo todavía no existe.

Al finalizar, ejecuté las pruebas utilizando el comando `python -m pytest -v` para comprobar su funcionamiento.

**Hallazgos de calidad**

También revisé el archivo `docs/perfilamiento.md`, donde encontré algunas situaciones que pueden afectar la calidad de los datos.

Entre ellas están los registros duplicados en los archivos de EnerAndes, fechas que no se reconocen correctamente, datos del IDEAM que no llegan hasta el final del periodo solicitado y valores nulos en algunas horas de generación de XM.

Con esta información preparé los hallazgos de calidad y las posibles acciones para revisarlos en la siguiente etapa del proyecto.

### 2. ¿Qué aprendí?

Durante esta actividad aprendí a utilizar pytest para comprobar el funcionamiento de funciones de Python.

Antes no tenía mucha experiencia haciendo pruebas automáticas, así que este trabajo me permitió entender cómo se pueden utilizar ejemplos de datos para verificar si una función entrega el resultado esperado.

También aprendí más sobre el manejo de Git y GitHub, especialmente sobre la creación de ramas, los commits, los Pull Requests y la integración de cambios realizados por otros compañeros.

Otra cosa que aprendí fue que antes de analizar los datos es importante revisar si tienen registros repetidos, valores vacíos o fechas incorrectas, porque estos problemas pueden afectar los resultados.

### 3. Dificultades y cómo las resolví

Una de las primeras dificultades fue la configuración de Python en mi Mac, porque tenía instalada la versión 3.9.6 y necesitaba una versión más reciente. Para solucionarlo instalé Python 3.13 y creé un entorno virtual para el proyecto.

Después tuve un problema con pytest, porque no estaba instalado. Cuando logré instalarlo, las pruebas no aparecían porque había creado el archivo `test_ventanas.py`, pero todavía estaba vacío. Luego agregué el código y pude ejecutar las primeras tres pruebas.

También tuve dificultades al intentar subir los cambios a GitHub, porque estaba utilizando una cuenta que no tenía permisos para modificar el repositorio. Después pude solucionar el acceso.

Otra dificultad fue entender cómo actualizar mi rama con los cambios que Aleicer estaba haciendo en XM. Al principio la función `aplanar()` no tenía soporte para las listas de recursos. Cuando Aleicer integró sus modificaciones, actualicé mi rama y pude realizar las cuatro pruebas.

Estas situaciones me ayudaron a conocer mejor el funcionamiento de las herramientas que estamos utilizando.

### 4. Horas dedicadas

**Total de horas:** 11 horas

### 5. Enlaces de mi trabajo

**Repositorio del proyecto:**

https://github.com/aleicer/pi4-observatorio-energia-grupo-1

**Commits realizados:**

**Commit 1 – Pruebas de ventanas():**

https://github.com/aleicer/pi4-observatorio-energia-grupo-1/commit/c64ce53

**Commit 2 – Pruebas de aplanar():**

https://github.com/aleicer/pi4-observatorio-energia-grupo-1/commit/798664f

**Commit 3 – Pruebas de idempotencia:**

https://github.com/aleicer/pi4-observatorio-energia-grupo-1/commit/120d7ac

**Pull Request de pruebas automáticas:**

https://github.com/aleicer/pi4-observatorio-energia-grupo-1/pull/2

**Pull Request de hallazgos y bitácora:**

**Pull Request de hallazgos y bitácora:**

https://github.com/aleicer/pi4-observatorio-energia-grupo-1/pull/7

## Semanas 3 y 4 (26 de octubre – 8 de noviembre de 2026)

**Rol:** Data Quality Analyst.

**Actividades realizadas:**

Durante la EA2 trabajé en la limpieza de los datos del índice ONI de NOAA para la capa plata del proyecto.

Primero agregué un esquema de validación utilizando Pandera, con el que se revisan los tipos de datos, los valores permitidos, el formato de los periodos y que no existan meses repetidos.

Después desarrollé el archivo `src/silver/noaa.py`, en el que convertí los trimestres móviles del ONI a su mes central. Por ejemplo, DJF corresponde a enero y JFM a febrero. También agregué una función que clasifica cada registro como El Niño, La Niña o Neutral, dependiendo del valor del ONI.

Al ejecutar la transformación se procesaron 920 registros. Los 920 pasaron la validación de Pandera y ninguno tuvo que enviarse a cuarentena.

Revisé los resultados y encontré que 448 meses quedaron clasificados como Neutral, 238 como La Niña y 234 como El Niño. También comprobé que no había periodos duplicados.

**Qué aprendí:**

Aprendí a utilizar Pandera para validar los datos antes de guardarlos, a transformar los trimestres móviles del ONI en periodos mensuales y a registrar métricas de calidad. También comprendí mejor la diferencia entre guardar los datos originales en bronce y preparar información validada en plata.

**Bloqueos y cómo los resolví:**

Al instalar las dependencias de la EA2 tuve un problema con dbt porque una descarga fallaba durante la verificación del certificado SSL. Lo solucioné instalando versiones compatibles de dbt Core y dbt-duckdb. Después pude instalar Pandera y continuar con el proyecto.

**Horas dedicadas:** 6 horas.

**Evidencias:**

- Esquema de validación de NOAA: https://github.com/aleicer/pi4-observatorio-energia-grupo-1/commit/7f9d0e9

- Limpieza de NOAA: https://github.com/aleicer/pi4-observatorio-energia-grupo-1/commit/80670e7

- Pull Request de NOAA: https://github.com/aleicer/pi4-observatorio-energia-grupo-1/pull/10

### Pruebas automatizadas de calidad de datos

Durante la EA2 desarrollé ocho pruebas automatizadas nuevas para comprobar las reglas de limpieza y transformación de la capa plata.

En `tests/test_noaa.py` elaboré cuatro pruebas para verificar la clasificación de las fases ENSO, la conversión de trimestres móviles a meses centrales, el tratamiento numérico del índice ONI y el rechazo de fases inválidas mediante Pandera.

En `tests/test_reglas_plata.py` desarrollé tres pruebas adicionales. Dos comprueban la interpretación de diferentes formatos de fecha y la conversión de unidades de energía de MWh a kWh en EnerAndes. La tercera verifica la transformación de datos horarios de XM desde columnas a filas.

Finalmente, incorporé una prueba en `tests/test_nasa_power.py` para comprobar que los valores `-999` se conviertan en datos faltantes y que diferentes variables climáticas de una misma fecha se organicen en una sola fila.

Ejecuté `python -m pytest -v` y obtuve como resultado **25 pruebas aprobadas, sin errores**, incluyendo las pruebas existentes del proyecto.

**Evidencia:**

- Pull Request #14 — Pruebas de calidad: https://github.com/aleicer/pi4-observatorio-energia-grupo-1/pull/14
- Commit de pruebas EnerAndes y XM: https://github.com/aleicer/pi4-observatorio-energia-grupo-1/commit/f58c6a2
- Commit de prueba NASA POWER: https://github.com/aleicer/pi4-observatorio-energia-grupo-1/commit/50c1499

### Diccionario de datos de la capa oro

Inicialmente elaboré el diccionario de datos del modelo de cuatro tablas, incorporado mediante el Pull Request #15.

Después actualicé el documento `docs/diccionario_datos.md` para que correspondiera al modelo final construido por el equipo: seis dimensiones y seis tablas de hechos.

Documenté las columnas, los tipos consultados directamente en DuckDB, la granularidad, las claves, las relaciones, la procedencia y las pruebas de calidad de cada tabla.

También actualicé la relación temporal de las ventas: el modelo anterior utilizaba `dim_mes`, mientras que el modelo final utiliza `dim_fecha`. Cada venta mensual se relaciona con el primer día de su mes mediante `fecha_id`.

Para validar el modelo ejecuté `python -m src.transformar`, que construyó doce tablas de oro y diez vistas de staging, y aprobó las 54 pruebas de dbt.

El resultado final fue:

`PASS=76 WARN=0 ERROR=0 SKIP=0 NO-OP=0 TOTAL=76`

Estas 76 operaciones corresponden a 22 modelos y 54 pruebas de calidad.

Además, ejecuté `python -m pytest -v` y obtuve 25 pruebas aprobadas.

La actualización del diccionario fue aprobada y fusionada por Aleicer el 4 de noviembre de 2026 mediante el Pull Request #18.

**Evidencias:**

- Pull Request #15 — Diccionario inicial: https://github.com/aleicer/pi4-observatorio-energia-grupo-1/pull/15
- Pull Request #18 — Diccionario del modelo final: https://github.com/aleicer/pi4-observatorio-energia-grupo-1/pull/18
- Commit de la actualización: https://github.com/aleicer/pi4-observatorio-energia-grupo-1/commit/750ec6e

### Dificultades durante la actualización

Al construir el modelo final encontré que mi archivo local antiguo de precipitación del IDEAM no contenía la columna `zonahidrografica`, necesaria para preparar la dimensión de estaciones.

Conservé ese archivo como respaldo y completé la descarga actualizada, aprovechando las semanas que ya estaban guardadas. Después ejecuté nuevamente la transformación y la construcción terminó sin errores.

También revisé el reporte de calidad de mi ejecución local. En hidrología XM se separaron 731 filas en cuarentena por incumplir las reglas de volumen útil o aportes. Registré esta situación en el diccionario como una observación de esa ejecución local.

Aprendí que una construcción puede aprobar las pruebas configuradas y aun así requerir una revisión de la cobertura y calidad de los datos de origen.

### Revisión del trabajo del equipo

Revisé y aprobé el Pull Request #17, correspondiente al modelo final de la capa oro.

**Evidencia:**

- Pull Request #17 — Modelo dimensional final: https://github.com/aleicer/pi4-observatorio-energia-grupo-1/pull/17

### Estado de las actividades

La limpieza de NOAA, las ocho pruebas automatizadas nuevas, el diccionario inicial y su actualización al modelo final están incorporados a la rama principal.

Los Pull Requests #10, #14, #15, #16 y #18 fueron fusionados.

Para cerrar la documentación de mi entrega queda incorporar el enlace del video de sustentación de la EA2 y verificar el archivo ZIP y las demás evidencias solicitadas por la guía.

**Horas dedicadas:** 8 horas.