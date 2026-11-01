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

- **Rol:** BI Analyst
- **Qué hice:** Construí el esquema de Pandera y la limpieza de NASA POWER para la capa plata. Cambié los valores `-999` por datos vacíos, convertí las fechas que venían en formato `AAAAMMDD`, eliminé mediciones repetidas y transformé la tabla del formato largo al formato ancho. También agregué una prueba automática y documenté en el README cómo ejecutar la transformación.
- **Resultados verificados:** La limpieza transformó 12.048 filas de bronce en 4.016 filas limpias, con 0 filas en cuarentena. Los 4 valores `-999` se redujeron a 0 y las 17 pruebas automáticas terminaron correctamente.
- **Qué aprendí:** Comprendí que `-999` representa la ausencia de una medición y no debe participar en promedios. También aprendí que `pivot` permite convertir las variables que ocupan filas separadas en columnas de una misma fecha y punto. Pandera comprueba los tipos, rangos y duplicados antes de guardar la capa plata.
- **Bloqueos y cómo los resolví:** Encontré archivos locales incompletos en la limpieza y en la prueba de NASA POWER. Corregí la sintaxis, completé la prueba y generé el archivo de bronce de EnerAndes que faltaba. Al actualizar mi rama con `main` apareció un conflicto en `src/quality/esquemas.py`; lo resolví conservando tanto `ESQUEMA_NASA` como `ESQUEMA_NOAA`.
- **Horas dedicadas:** 8 horas.
- **Commits:**
  - Esquema de Pandera: https://github.com/aleicer/pi4-observatorio-energia-grupo-1/commit/d3d12ba5852def7057c40abbec3c5714cf0d74cb
  - Limpieza y prueba: https://github.com/aleicer/pi4-observatorio-energia-grupo-1/commit/579f2e8
  - Actualización con `main`: https://github.com/aleicer/pi4-observatorio-energia-grupo-1/commit/901272c
- **Pull Request:** Pendiente de crear.