# Bitácora de Guillermo León Loaiza

## Semana 2 (19 - 25 de octubre de 2026)

- **Rol:** BI Analyst
- **Qué hice:** Desarrollé el extractor de la fuente propia NASA POWER (`src/extract/nasa_power.py`), actualicé la configuración (`src/config.py`), lo integré al pipeline y redacté su sección en el README.
- **Qué aprendí:** Comprendí el concepto de idempotencia al usar la función `ya_existe`, para que el pipeline omita las descargas que ya están en la capa bronce. También aprendí a consumir una API REST, aplanar estructuras JSON anidadas y guardar la información cruda en Parquet, conservando valores como `-999` para tratarlos posteriormente en la capa plata.

- **Bloqueos y cómo los resolví:** Al principio no era evidente la estructura de la respuesta de la API. Probé el endpoint en el navegador para entender el JSON antes de programar `aplanar_nasa`. También actualicé mi rama desde `main` para evitar conflictos con los cambios realizados por el equipo.
- **Horas dedicadas:** 5 horas.
- **Commits:**
  - https://github.com/aleicer/pi4-observatorio-energia-grupo-1/commit/016d5cf6fca0adfba44f7180c75ae0ca92142b9c
  - https://github.com/aleicer/pi4-observatorio-energia-grupo-1/commit/3a81a1c6a7e52c7e4bc84eb53712f6a8798c4d16
  - https://github.com/aleicer/pi4-observatorio-energia-grupo-1/commit/5f20ae5a212da4cce1795a17d31d7b0e3253eec1

## Semanas 3 y 4 (26 de octubre - 8 de noviembre de 2026)

- **Rol:** BI Analyst.
- **Qué hice:** Construí el esquema de Pandera y la limpieza de NASA POWER para la capa plata. Cambié los valores `-999` por datos vacíos, convertí las fechas `AAAAMMDD`, eliminé mediciones repetidas y transformé la tabla del formato largo al ancho. También desarrollé `src/consultar_oro.py`, cuatro consultas SQL sobre el esquema estrella y la documentación de sus resultados en el README.
- **Resultados verificados:** NASA POWER pasó de 12.048 filas de bronce a 4.016 filas limpias, con 0 filas en cuarentena y los 4 valores `-999` reducidos a 0. La transformación completa terminó con 63 reglas de calidad, dbt finalizó con `PASS=76` y `ERROR=0`, y las 25 pruebas de pytest fueron aprobadas. Las cuatro consultas generaron correctamente sus resultados en `docs/resultados_consultas.md`.
- **Qué aprendí:** Comprendí que `-999` representa ausencia de medición y no debe incluirse en promedios. Aprendí a utilizar `pivot` para convertir variables almacenadas en filas en columnas, validar datos con Pandera y consultar un esquema estrella en DuckDB. También aprendí a relacionar tablas de hechos con dimensiones para analizar precios, generación, ventas y clima.
- **Bloqueos y cómo los resolví:** Encontré archivos locales incompletos en la limpieza y la prueba de NASA POWER, que corregí antes de ejecutar las validaciones. Al actualizar la rama apareció un conflicto en `src/quality/esquemas.py`; conservé tanto `ESQUEMA_NASA` como `ESQUEMA_NOAA`. Para construir la capa oro faltaban los archivos bronce del IDEAM, por lo que ejecuté nuevamente el pipeline y aproveché su comportamiento idempotente. Finalmente, verifiqué los nombres reales de las tablas y columnas en el modelo dbt antes de escribir las consultas.
- **Horas dedicadas:** 13 horas aproximadamente: 8 horas en la limpieza de NASA POWER y 5 horas en las consultas y su documentación.
- **Commits de la Parte A:**
  - Esquema de Pandera: https://github.com/aleicer/pi4-observatorio-energia-grupo-1/commit/d3d12ba5852def7057c40abbec3c5714cf0d74cb
  - Limpieza y prueba: https://github.com/aleicer/pi4-observatorio-energia-grupo-1/commit/579f2e8
  - Bitácora de la limpieza: https://github.com/aleicer/pi4-observatorio-energia-grupo-1/commit/e3facee
- **Commits de la Parte B:**
  - Programa de consultas: https://github.com/aleicer/pi4-observatorio-energia-grupo-1/commit/94c8d12
  - Cuatro consultas SQL: https://github.com/aleicer/pi4-observatorio-energia-grupo-1/commit/e91f3d8
- **Pull Request de NASA POWER:** https://github.com/aleicer/pi4-observatorio-energia-grupo-1/pull/13
- **Pull Request de consultas:** Pendiente de crear.