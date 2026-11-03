
# Diccionario de datos — Capa oro

## 1. Descripción general

El Observatorio de Energía utiliza un modelo dimensional tipo estrella para analizar las ventas mensuales de energía.

La capa oro se construye mediante dbt a partir del modelo `stg_ventas`, utilizando DuckDB.

El modelo está compuesto por tres dimensiones y una tabla de hechos:

- `dim_mes`
- `dim_municipio`
- `dim_segmento`
- `fact_ventas_mensual`

## 2. Tabla dim_mes

**Descripción:** contiene un registro por cada mes con ventas de energía.

**Granularidad:** un mes.

| Columna | Tipo | Descripción |
|---|---|---|
| mes_id | INTEGER | Identificador del mes en formato AAAAMM. Clave de la dimensión. |
| periodo | VARCHAR | Periodo en formato AAAA-MM. |
| anio | INTEGER | Año del periodo. |
| mes | INTEGER | Número del mes, entre 1 y 12. |
| trimestre | INTEGER | Trimestre del año, entre 1 y 4. |

**Origen:** `stg_ventas`.

**Reglas de calidad:** dbt verifica que `mes_id` sea único y no contenga valores nulos.

## 3. Tabla dim_municipio

**Descripción:** contiene los municipios de Antioquia incluidos en los datos de ventas.

**Granularidad:** un municipio.

| Columna | Tipo | Descripción |
|---|---|---|
| municipio_id | VARCHAR | Código DIVIPOLA del municipio. Clave de la dimensión. |
| municipio | VARCHAR | Nombre del municipio. |

**Origen:** `stg_ventas`.

**Reglas de calidad:** dbt verifica que `municipio_id` sea único y no contenga valores nulos.

El identificador se almacena como texto para conservar los ceros iniciales de los códigos DIVIPOLA.

## 4. Tabla dim_segmento

**Descripción:** identifica los segmentos de clientes asociados con las ventas de energía.

**Granularidad:** un segmento.

| Columna | Tipo | Descripción |
|---|---|---|
| segmento_id | BIGINT | Identificador numérico generado mediante `row_number()`. Clave de la dimensión. |
| segmento | VARCHAR | Nombre del segmento de clientes. |

**Origen:** valores distintos de `segmento` presentes en `stg_ventas`.

**Reglas de calidad:** dbt verifica que `segmento_id` sea único y no contenga valores nulos.

## 5. Tabla fact_ventas_mensual

**Descripción:** contiene las medidas de ventas de energía asociadas con cada mes, municipio, segmento y tipo de compra.

**Granularidad:** una combinación de mes, municipio, segmento y tipo de compra, según el modelo SQL.

| Columna | Tipo | Descripción |
|---|---|---|
| mes_id | INTEGER | Identificador del mes. Referencia a `dim_mes`. |
| municipio_id | VARCHAR | Código DIVIPOLA. Referencia a `dim_municipio`. |
| segmento_id | BIGINT | Identificador del segmento. Referencia a `dim_segmento`. |
| tipo_compra | VARCHAR | Modalidad de compra: Bolsa o Contrato. |
| energia_kwh | DOUBLE | Cantidad de energía expresada en kilovatios-hora. |
| valor_cop | DOUBLE | Valor monetario expresado en pesos colombianos. |
| clientes | BIGINT | Número de clientes registrado para la venta. |

**Origen:** `stg_ventas`, relacionado con `dim_segmento` mediante la columna `segmento`.

**Reglas de calidad:** dbt comprueba que las tres claves de referencia no contengan valores nulos y que sus valores existan en las dimensiones correspondientes. También verifica que `tipo_compra` pertenezca a los valores `Bolsa` o `Contrato`.

## 6. Relaciones del modelo dimensional

La tabla de hechos se relaciona con las dimensiones mediante los siguientes campos:

| Tabla de hechos | Tabla de dimensión | Campo |
|---|---|---|
| fact_ventas_mensual | dim_mes | mes_id |
| fact_ventas_mensual | dim_municipio | municipio_id |
| fact_ventas_mensual | dim_segmento | segmento_id |

Estas relaciones se verifican mediante pruebas `relationships` de dbt.

Las pruebas permiten detectar referencias inexistentes, aunque no constituyen restricciones físicas de claves foráneas declaradas en DuckDB.

## 7. Validación del modelo

Se ejecutó el comando:

`dbt build --project-dir dbt --profiles-dir dbt`

Resultado obtenido:

- Cuatro modelos de tablas construidos.
- Una vista de staging construida.
- Trece pruebas de calidad aprobadas.
- Cero errores y cero advertencias.

**Resultado final:** `PASS=18 WARN=0 ERROR=0 SKIP=0`.

Los tipos de las columnas fueron consultados directamente en DuckDB mediante `PRAGMA table_info`.

Las tablas no presentan restricciones físicas `NOT NULL` declaradas. Las condiciones de obligatoriedad descritas en este documento corresponden a las pruebas de calidad configuradas en dbt.

## 8. Fuentes y trazabilidad

Los modelos de la capa oro se encuentran en `dbt/models/marts/`.

El modelo intermedio utilizado para construir las dimensiones y la tabla de hechos es `dbt/models/staging/stg_ventas.sql`.

Las reglas y pruebas de calidad del modelo dimensional están definidas en `dbt/models/marts/schema.yml`.

La fuente de los datos de ventas es EnerAndes, procesada previamente en las capas bronce y plata.
