# Diccionario de datos — Capa oro

## 1. Descripción general

El Observatorio de Energía y Clima organiza sus datos en un modelo dimensional construido con dbt sobre DuckDB.

La capa oro contiene **doce tablas: seis dimensiones y seis tablas de hechos**. Estas permiten analizar ventas, mercado eléctrico, generación, hidrología y clima.

Los datos se almacenan en `data/observatorio.duckdb`. Los modelos SQL se encuentran en `dbt/models/marts/` y utilizan diez vistas de staging que leen los archivos Parquet de la capa plata.

Las descripciones y pruebas de calidad están definidas en `dbt/models/marts/schema.yml`.

Las claves y relaciones descritas en este documento representan el diseño lógico del modelo. Las pruebas de dbt comprueban las condiciones configuradas, pero no equivalen a restricciones físicas de clave primaria, clave foránea o `NOT NULL` declaradas en DuckDB.

## 2. Dimensiones

### 2.1. dim_fecha

**Descripción:** calendario diario con información temporal y la clasificación ENSO del mes según NOAA.

**Granularidad:** un día, desde el 1 de enero de 2023 hasta el 30 de septiembre de 2026, según las variables del proyecto dbt.

**Clave lógica:** `fecha_id`.

| Columna | Tipo DuckDB | Descripción |
|---|---|---|
| fecha_id | INTEGER | Identificador del día en formato AAAAMMDD. |
| fecha | DATE | Fecha del calendario. |
| anio | BIGINT | Año de la fecha. |
| mes | BIGINT | Número del mes, entre 1 y 12. |
| nombre_mes | VARCHAR | Nombre del mes en español. |
| periodo | VARCHAR | Mes en formato AAAA-MM. |
| trimestre | BIGINT | Trimestre del año, entre 1 y 4. |
| dia_semana | BIGINT | Día de la semana: 1 corresponde a lunes y 7 a domingo. |
| nombre_dia | VARCHAR | Nombre del día en español. |
| es_fin_de_semana | BOOLEAN | Indica si la fecha corresponde a sábado o domingo. |
| oni | DOUBLE | Índice Oceánico El Niño del mes, expresado como anomalía de temperatura en °C. |
| fase_enso | VARCHAR | Clasificación del mes: El Niño, La Niña, Neutral o Sin dato. |

**Origen:** calendario generado mediante SQL y relacionado con `stg_oni`, que lee `noaa_oni_mensual.parquet` de la capa plata.

**Reglas de calidad:**

- `fecha_id` y `fecha`: valores únicos y no nulos.
- `fase_enso`: no nula y limitada a El Niño, La Niña, Neutral o Sin dato.

Cuando no existe información NOAA para el mes, `oni` queda nulo y `fase_enso` toma el valor `Sin dato`.

### 2.2. dim_hora

**Descripción:** horas del día y su clasificación por franja.

**Granularidad:** una hora, entre 0 y 23.

**Clave lógica:** `hora`.

| Columna | Tipo DuckDB | Descripción |
|---|---|---|
| hora | BIGINT | Hora del día. El valor 0 representa de 00:00 a 01:00 y el valor 23, de 23:00 a 24:00. |
| hora_inicio | VARCHAR | Hora de inicio como texto, por ejemplo 07:00. |
| franja | VARCHAR | Franja asignada: Pico, Media o Valle. |

**Origen:** generada directamente en SQL.

**Reglas de calidad:**

- `hora`: única y no nula.
- `franja`: limitada a Pico, Media o Valle.

La clasificación implementada es Pico entre las horas 17 y 21, Valle entre 0 y 5 y Media para las restantes.

### 2.3. dim_municipio

**Descripción:** municipios de Antioquia con ventas de EnerAndes y cantidad de estaciones IDEAM asociadas.

**Granularidad:** un municipio.

**Clave lógica:** `municipio_id`.

| Columna | Tipo DuckDB | Descripción |
|---|---|---|
| municipio_id | VARCHAR | Código DIVIPOLA de cinco dígitos. |
| municipio | VARCHAR | Nombre del municipio. |
| estaciones_ideam | BIGINT | Cantidad de estaciones IDEAM asociadas al municipio. |

**Origen:** municipios de `stg_ventas`, relacionados con las estaciones de `stg_estaciones`.

**Reglas de calidad:**

- `municipio_id`: único y no nulo.
- `municipio`: no nulo.

El código se almacena como texto para conservar sus ceros iniciales, por ejemplo `05001`.

### 2.4. dim_segmento

**Descripción:** segmentos de clientes de EnerAndes.

**Granularidad:** un segmento.

**Clave lógica:** `segmento_id`.

| Columna | Tipo DuckDB | Descripción |
|---|---|---|
| segmento_id | BIGINT | Identificador generado con `row_number()` sobre los segmentos ordenados alfabéticamente. |
| segmento | VARCHAR | Segmento del cliente: Residencial, Comercial, Industrial o No informado. |

**Origen:** valores distintos de `segmento` presentes en `stg_ventas`.

**Reglas de calidad:**

- `segmento_id`: único y no nulo.
- `segmento`: limitado a Residencial, Comercial, Industrial o No informado.

### 2.5. dim_recurso

**Descripción:** plantas de generación eléctrica registradas en XM.

**Granularidad:** una planta.

**Clave lógica:** `recurso_id`.

| Columna | Tipo DuckDB | Descripción |
|---|---|---|
| recurso_id | VARCHAR | Código SIC de la planta en XM. |
| nombre | VARCHAR | Nombre de la planta. |
| tipo | VARCHAR | Tipo de planta: HIDRAULICA, TERMICA, SOLAR, EOLICA, COGENERADOR o DESCONOCIDO. |
| fuente_energia | VARCHAR | Combustible o recurso energético, por ejemplo AGUA, GAS, CARBON, RAD SOLAR o VIENTO. |
| despacho | VARCHAR | Clasificación del despacho de la planta. |
| clase | VARCHAR | Clase del recurso registrada en el catálogo. |
| agente | VARCHAR | Código de la empresa asociada a la planta. |
| fecha_operacion | DATE | Fecha de entrada en operación. |
| estado | VARCHAR | Estado registrado, por ejemplo OPERACION, PRUEBAS o DESCONOCIDO. |
| es_renovable | BOOLEAN | Indica si la planta es hidráulica, solar o eólica, según la regla implementada. |

**Origen:** `stg_recursos`, que lee `xm_recursos.parquet`, preparado a partir del catálogo `ListadoRecursos` de XM.

Las plantas que reportan generación pero no aparecen en el catálogo se incorporan en plata con tipo `DESCONOCIDO`.

**Reglas de calidad:**

- `recurso_id`: único y no nulo.
- `tipo`: limitado a HIDRAULICA, TERMICA, SOLAR, EOLICA, COGENERADOR o DESCONOCIDO.

### 2.6. dim_estacion

**Descripción:** estaciones meteorológicas del IDEAM en Antioquia.

**Granularidad:** una estación.

**Clave lógica:** `estacion_id`.

| Columna | Tipo DuckDB | Descripción |
|---|---|---|
| estacion_id | VARCHAR | Código de diez dígitos de la estación. |
| nombre | VARCHAR | Nombre de la estación. |
| municipio | VARCHAR | Municipio donde se encuentra la estación. |
| municipio_id | VARCHAR | Código DIVIPOLA asignado cuando el municipio tiene ventas de EnerAndes. |
| zona_hidrografica | VARCHAR | Zona hidrográfica asociada a la estación. |
| latitud | DOUBLE | Latitud de la estación, en grados. |
| longitud | DOUBLE | Longitud de la estación, en grados. |

**Origen:** `stg_estaciones`, que lee `ideam_estaciones.parquet`, elaborado con los datos de precipitación y temperatura del IDEAM.

**Reglas de calidad:**

- `estacion_id`: único y no nulo.
- Los valores no nulos de `municipio_id` deben existir en `dim_municipio`.

`municipio_id` puede quedar nulo cuando la estación pertenece a un municipio que no está incluido en las ventas de EnerAndes.

## 3. Tablas de hechos

### 3.1. fact_ventas_mensual

**Descripción:** ventas mensuales de energía de EnerAndes.

**Granularidad:** una combinación de mes, municipio, segmento y tipo de compra.

| Columna | Tipo DuckDB | Descripción |
|---|---|---|
| fecha_id | INTEGER | Primer día del mes de la venta, en formato AAAAMM01. Referencia a `dim_fecha`. |
| municipio_id | VARCHAR | Código DIVIPOLA. Referencia a `dim_municipio`. |
| segmento_id | BIGINT | Identificador del segmento. Referencia a `dim_segmento`. |
| tipo_compra | VARCHAR | Modalidad de compra: Bolsa o Contrato. |
| energia_kwh | DOUBLE | Energía vendida durante el mes, en kWh. |
| valor_cop | DOUBLE | Valor facturado en pesos colombianos. Puede quedar nulo cuando el Excel no proporciona el dato. |
| clientes | BIGINT | Número de clientes registrado en los datos de ventas. |

**Origen:** `stg_ventas`, relacionado con `dim_segmento` mediante el nombre del segmento. La fuente original es el Excel de EnerAndes.

La energía de la hoja de 2024, originalmente expresada en MWh, se convierte a kWh durante la limpieza de plata.

**Relación temporal:** las ventas son mensuales. Por ejemplo, marzo de 2024 se representa mediante `fecha_id = 20240301`. Para analizarlas por mes se utilizan `anio`, `mes` o `periodo` de `dim_fecha`.

**Reglas de calidad:**

- `fecha_id`, `municipio_id` y `segmento_id`: no nulos y existentes en sus respectivas dimensiones.
- `tipo_compra`: limitado a Bolsa o Contrato.
- `energia_kwh`: no nula.
- Prueba de grano que detecta duplicados en la combinación de fecha, municipio, segmento y tipo de compra.

### 3.2. fact_mercado_horario

**Descripción:** precio de bolsa y demanda eléctrica nacional por hora.

**Granularidad:** una fecha y una hora.

| Columna | Tipo DuckDB | Descripción |
|---|---|---|
| fecha_id | INTEGER | Día en formato AAAAMMDD. Referencia a `dim_fecha`. |
| hora | BIGINT | Hora del día, entre 0 y 23. Referencia a `dim_hora`. |
| precio_bolsa_cop_kwh | DOUBLE | Precio de bolsa nacional en COP/kWh. |
| demanda_kwh | DOUBLE | Demanda real nacional durante la hora, en kWh. |

**Origen:** `stg_mercado`, que lee `xm_mercado_horario.parquet`, preparado con los datos de precio de bolsa y demanda de XM.

**Reglas de calidad:**

- `fecha_id` y `hora`: no nulos y existentes en sus dimensiones.
- Prueba de grano que detecta duplicados por fecha y hora.

### 3.3. fact_generacion_recurso

**Descripción:** energía generada por cada planta durante cada hora.

**Granularidad:** una fecha, una hora y una planta.

| Columna | Tipo DuckDB | Descripción |
|---|---|---|
| fecha_id | INTEGER | Día en formato AAAAMMDD. Referencia a `dim_fecha`. |
| hora | BIGINT | Hora del día. Referencia a `dim_hora`. |
| recurso_id | VARCHAR | Código de la planta. Referencia a `dim_recurso`. |
| generacion_kwh | DOUBLE | Energía generada por la planta durante la hora, en kWh. |

**Origen:** `stg_generacion`, que lee `xm_generacion_recurso.parquet`, preparado con la generación por recurso de XM.

**Reglas de calidad:**

- `fecha_id`, `hora` y `recurso_id`: no nulos y existentes en sus respectivas dimensiones.
- `generacion_kwh`: no nula.
- Prueba de grano que detecta duplicados por fecha, hora y planta.

Las horas sin generación reportada se omiten durante la limpieza de plata. Su ausencia no representa automáticamente una medición de cero.

### 3.4. fact_hidrologia_diaria

**Descripción:** volumen útil de los embalses y aportes hídricos nacionales.

**Granularidad:** una fecha.

| Columna | Tipo DuckDB | Descripción |
|---|---|---|
| fecha_id | INTEGER | Día en formato AAAAMMDD. Referencia a `dim_fecha`. |
| volumen_util_pct | DOUBLE | Porcentaje de volumen útil de los embalses, en escala de 0 a 100. |
| aportes_kwh | DOUBLE | Aportes hídricos expresados como energía, en kWh. |

**Origen:** `stg_hidrologia`, que lee `xm_hidrologia_diaria.parquet`, preparado con los datos de embalses y aportes de XM.

**Reglas de calidad:**

- `fecha_id`: único, no nulo y existente en `dim_fecha`.

La unicidad de `fecha_id` comprueba el grano diario de esta tabla.

### 3.5. fact_clima_diario

**Descripción:** precipitación y temperatura medidas por estaciones del IDEAM.

**Granularidad:** una fecha y una estación.

| Columna | Tipo DuckDB | Descripción |
|---|---|---|
| fecha_id | INTEGER | Día en formato AAAAMMDD. Referencia a `dim_fecha`. |
| estacion_id | VARCHAR | Código de la estación. Referencia a `dim_estacion`. |
| precipitacion_mm | DOUBLE | Precipitación diaria, en milímetros. |
| temp_media_c | DOUBLE | Temperatura media diaria, en °C. |
| temp_min_c | DOUBLE | Temperatura mínima diaria, en °C. |
| temp_max_c | DOUBLE | Temperatura máxima diaria, en °C. |

**Origen:** unión completa, mediante `full outer join`, de `stg_precipitacion` y `stg_temperatura` por estación y fecha.

Estas vistas leen `ideam_precipitacion_diaria.parquet` e `ideam_temperatura_diaria.parquet`.

**Reglas de calidad:**

- `fecha_id` y `estacion_id`: no nulos y existentes en sus dimensiones.
- Prueba de grano que detecta duplicados por fecha y estación.

Una estación puede medir únicamente precipitación o temperatura. Por esta razón, las medidas de la otra variable pueden quedar nulas.

### 3.6. fact_clima_satelital

**Descripción:** radiación solar, temperatura y precipitación diaria obtenidas de NASA POWER, la fuente propia del equipo.

**Granularidad:** una fecha y un punto geográfico.

| Columna | Tipo DuckDB | Descripción |
|---|---|---|
| fecha_id | INTEGER | Día en formato AAAAMMDD. Referencia a `dim_fecha`. |
| punto | VARCHAR | Nombre del punto consultado. |
| latitud | DOUBLE | Latitud del punto, en grados. |
| longitud | DOUBLE | Longitud del punto, en grados. |
| radiacion_kwh_m2 | DOUBLE | Radiación solar diaria que llega al suelo, en kWh/m² por día. |
| temperatura_c | DOUBLE | Temperatura del aire a dos metros, en °C. |
| precipitacion_mm | DOUBLE | Precipitación diaria estimada, en milímetros. |

**Origen:** `stg_nasa`, que lee `nasa_power_diario.parquet`, preparado con las consultas a NASA POWER.

Los puntos corresponden a Medellín, el embalse Peñol-Guatapé, Hidroituango y La Guajira.

**Reglas de calidad:**

- `fecha_id`: no nulo y existente en `dim_fecha`.
- `punto`: no nulo.

Los valores de ausencia de datos representados como `-999` por la fuente se convierten a nulos durante la limpieza de plata.

El grano definido es fecha y punto. La configuración actual de dbt no incluye una prueba específica de unicidad para esta combinación.

## 4. Relaciones del modelo

| Tabla de origen | Campo | Dimensión de destino |
|---|---|---|
| fact_ventas_mensual | fecha_id | dim_fecha |
| fact_ventas_mensual | municipio_id | dim_municipio |
| fact_ventas_mensual | segmento_id | dim_segmento |
| fact_mercado_horario | fecha_id | dim_fecha |
| fact_mercado_horario | hora | dim_hora |
| fact_generacion_recurso | fecha_id | dim_fecha |
| fact_generacion_recurso | hora | dim_hora |
| fact_generacion_recurso | recurso_id | dim_recurso |
| fact_hidrologia_diaria | fecha_id | dim_fecha |
| fact_clima_diario | fecha_id | dim_fecha |
| fact_clima_diario | estacion_id | dim_estacion |
| fact_clima_satelital | fecha_id | dim_fecha |
| dim_estacion | municipio_id | dim_municipio |

Las relaciones se comprueban mediante pruebas `relationships` de dbt.

`dim_fecha` es compartida por las seis tablas de hechos. Para combinar medidas de diferentes hechos, deben respetarse sus distintas granularidades y agregarse al nivel de análisis requerido antes de relacionarlas.

## 5. Construcción y validación

La construcción completa se ejecuta desde la raíz del repositorio con:

`python -m src.transformar`

Este comando limpia y valida los datos de plata mediante Pandera, genera `docs/reporte_calidad.md` y ejecuta la construcción de oro con dbt.

Para construir únicamente oro, cuando la capa plata ya existe, se utiliza:

`dbt build --project-dir dbt --profiles-dir dbt`

En la ejecución local verificada el 3 de noviembre de 2026 se obtuvo:

| Componente | Cantidad | Resultado |
|---|---:|---|
| Tablas de oro | 12 | Construidas |
| Vistas de staging | 10 | Construidas |
| Pruebas de calidad dbt | 54 | Aprobadas |
| Total de operaciones dbt | 76 | Exitosas |

**Resultado final de dbt:** `PASS=76 WARN=0 ERROR=0 SKIP=0 NO-OP=0 TOTAL=76`.

Las 54 pruebas se distribuyen en:

- 50 pruebas genéricas configuradas en `dbt/models/marts/schema.yml`.
- Cuatro pruebas SQL de grano en `dbt/tests/`, para ventas, mercado, generación y clima IDEAM.

Además, la ejecución de `python -m pytest -v` realizada durante esta actualización finalizó con **25 pruebas aprobadas**.

Los tipos de datos de este diccionario se consultaron directamente en las tablas construidas de DuckDB mediante `DESCRIBE`.

## 6. Alcance de los resultados de calidad

La aprobación de las pruebas confirma las reglas configuradas sobre los datos procesados. No garantiza por sí sola que las fuentes tengan cobertura temporal completa.

En la ejecución local verificada, la limpieza de hidrología XM separó 731 filas en cuarentena por volumen fuera del rango de 0 a 100 % o aportes negativos. La tabla limpia resultante contiene 273 filas.

Estos registros no se incorporaron a la capa oro. El detalle de las reglas y sus métricas se encuentra en el reporte generado de calidad de plata.

Las cantidades corresponden a esa ejecución local y pueden cambiar al actualizar las descargas.

## 7. Fuentes y trazabilidad

| Fuente | Información utilizada en oro |
|---|---|
| EnerAndes | Ventas mensuales, municipios y segmentos de clientes. |
| XM | Precio de bolsa, demanda, generación por planta, hidrología y catálogo de recursos. |
| IDEAM | Estaciones, precipitación y temperatura. |
| NOAA | Índice ONI mensual y clasificación ENSO. |
| NASA POWER | Radiación solar, temperatura y precipitación por punto. |

Archivos de referencia:

- `dbt/models/marts/`: definición SQL de las doce tablas de oro.
- `dbt/models/marts/schema.yml`: descripciones y pruebas de calidad.
- `dbt/models/staging/`: vistas de lectura de la capa plata.
- `dbt/models/staging/sources.yml`: correspondencia con los archivos Parquet de plata.
- `dbt/tests/`: pruebas SQL de grano.
- `dbt/dbt_project.yml`: materializaciones y rango del calendario.
- `docs/modelo_dimensional.md`: diagrama y explicación del modelo.
- `docs/reporte_calidad.md`: métricas de limpieza y cuarentena de plata.