# Perfilamiento de la capa bronce

> Generado con `python -m src.perfilamiento` el 2026-10-23 17:39. No edite esta parte a mano: se reemplaza cada vez que se ejecuta el script.

- **Tipo en Parquet:** como quedó guardada la columna (en bronce casi todo es texto, `object`).
- **Parece:** qué tipo de dato contiene en realidad (número, fecha o texto).
- **% nulos:** celdas vacías o nulas. **Duplicadas:** filas idénticas sin contar las columnas de linaje.

## Resumen

| Archivo | Filas | Columnas | Filas duplicadas | Rango de fechas |
|---|---:|---:|---:|---|
| `enerandes_ventas_2023` | 1,114 | 10 | 32 | 2023-01-01 a 2023-12-01 (2 valores no son fecha) |
| `enerandes_ventas_2024` | 1,114 | 11 | 32 | 2024-01-01 a 2024-12-01 (2 valores no son fecha) |
| `enerandes_ventas_2025` | 1,117 | 10 | 32 | 2025-01-01 a 2025-12-01 (4 valores no son fecha) |
| `enerandes_ventas_2026` | 839 | 10 | 24 | 2026-01-01 a 2026-09-01 (4 valores no son fecha) |
| `ideam_precipitacion_diaria` | 29,804 | 12 | 0 | 2025-01-01 a 2026-07-24 |
| `ideam_temperatura_diaria` | 17,349 | 14 | 0 | 2025-01-01 a 2026-07-24 |
| `nasa_power_diario` | 12,048 | 9 | 0 | 2024-01-01 a 2026-09-30 |
| `noaa_oni` | 920 | 7 | 0 | 1950-01-01 a 2026-01-01 |
| `xm_aportes_hidricos` | 1,004 | 6 | 0 | 2024-01-01 a 2026-09-30 |
| `xm_demanda` | 1,004 | 30 | 0 | 2024-01-01 a 2026-09-30 |
| `xm_embalses` | 1,004 | 6 | 0 | 2024-01-01 a 2026-09-30 |
| `xm_generacion_recurso` | 350,345 | 30 | 0 | 2024-01-01 a 2026-09-30 |
| `xm_listado_recursos` | 2,494 | 14 | 2 | 2026-10-22 a 2026-10-22 |
| `xm_precio_bolsa` | 1,004 | 30 | 0 | 2024-01-01 a 2026-09-30 |

## `enerandes_ventas_2023`

**Filas:** 1,114 · **Columnas:** 10 (incluye 3 de linaje) · **Filas duplicadas:** 32 · **Rango de fechas:** 2023-01-01 a 2023-12-01 (2 valores no son fecha)

| Columna | Tipo en Parquet | Parece | % nulos | Valores distintos |
|---|---|---|---:|---:|
| `col_0` | str | fecha | 0.0 | 14 |
| `col_1` | str | texto | 0.09 | 32 |
| `col_2` | str | texto | 1.44 | 7 |
| `col_3` | str | texto | 0.09 | 5 |
| `col_4` | str | número | 0.9 | 1,070 |
| `col_5` | str | número | 0.72 | 1,074 |
| `col_6` | str | número | 0.09 | 587 |

## `enerandes_ventas_2024`

**Filas:** 1,114 · **Columnas:** 11 (incluye 3 de linaje) · **Filas duplicadas:** 32 · **Rango de fechas:** 2024-01-01 a 2024-12-01 (2 valores no son fecha)

| Columna | Tipo en Parquet | Parece | % nulos | Valores distintos |
|---|---|---|---:|---:|
| `col_0` | str | fecha | 0.0 | 38 |
| `col_1` | str | texto | 0.09 | 33 |
| `col_2` | str | texto | 0.36 | 7 |
| `col_3` | str | texto | 0.09 | 5 |
| `col_4` | str | número | 0.72 | 1,075 |
| `col_5` | str | texto | 0.09 | 3 |
| `col_6` | str | número | 1.08 | 1,070 |
| `col_7` | str | número | 0.09 | 583 |

## `enerandes_ventas_2025`

**Filas:** 1,117 · **Columnas:** 10 (incluye 3 de linaje) · **Filas duplicadas:** 32 · **Rango de fechas:** 2025-01-01 a 2025-12-01 (4 valores no son fecha)

| Columna | Tipo en Parquet | Parece | % nulos | Valores distintos |
|---|---|---|---:|---:|
| `col_0` | str | fecha | 0.09 | 16 |
| `col_1` | str | texto | 0.36 | 31 |
| `col_2` | str | texto | 0.9 | 7 |
| `col_3` | str | texto | 0.36 | 5 |
| `col_4` | str | número | 0.9 | 1,076 |
| `col_5` | str | número | 0.72 | 1,077 |
| `col_6` | str | número | 0.36 | 602 |

## `enerandes_ventas_2026`

**Filas:** 839 · **Columnas:** 10 (incluye 3 de linaje) · **Filas duplicadas:** 24 · **Rango de fechas:** 2026-01-01 a 2026-09-01 (4 valores no son fecha)

| Columna | Tipo en Parquet | Parece | % nulos | Valores distintos |
|---|---|---|---:|---:|
| `col_0` | str | fecha | 0.12 | 13 |
| `col_1` | str | texto | 0.48 | 30 |
| `col_2` | str | texto | 1.07 | 7 |
| `col_3` | str | texto | 0.48 | 5 |
| `col_4` | str | número | 1.07 | 806 |
| `col_5` | str | número | 1.31 | 805 |
| `col_6` | str | número | 0.48 | 473 |

## `ideam_precipitacion_diaria`

**Filas:** 29,804 · **Columnas:** 12 (incluye 3 de linaje) · **Filas duplicadas:** 0 · **Rango de fechas:** 2025-01-01 a 2026-07-24

| Columna | Tipo en Parquet | Parece | % nulos | Valores distintos |
|---|---|---|---:|---:|
| `codigoestacion` | str | número | 0.0 | 72 |
| `nombreestacion` | str | texto | 0.0 | 72 |
| `municipio` | str | texto | 0.0 | 50 |
| `zonahidrografica` | str | texto | 0.0 | 6 |
| `latitud` | str | número | 0.0 | 72 |
| `longitud` | str | número | 0.0 | 72 |
| `fecha` | str | fecha | 0.0 | 537 |
| `precipitacion_mm` | str | número | 0.0 | 1,125 |
| `n_obs` | str | número | 0.0 | 322 |

## `ideam_temperatura_diaria`

**Filas:** 17,349 · **Columnas:** 14 (incluye 3 de linaje) · **Filas duplicadas:** 0 · **Rango de fechas:** 2025-01-01 a 2026-07-24

| Columna | Tipo en Parquet | Parece | % nulos | Valores distintos |
|---|---|---|---:|---:|
| `codigoestacion` | str | número | 0.0 | 44 |
| `nombreestacion` | str | texto | 0.0 | 44 |
| `municipio` | str | texto | 0.0 | 37 |
| `zonahidrografica` | str | texto | 0.0 | 5 |
| `latitud` | str | número | 0.0 | 44 |
| `longitud` | str | número | 0.0 | 44 |
| `fecha` | str | fecha | 0.0 | 528 |
| `temp_media_c` | str | número | 0.0 | 7,608 |
| `temp_min_c` | str | número | 0.0 | 293 |
| `temp_max_c` | str | número | 0.0 | 291 |
| `n_obs` | str | número | 0.0 | 205 |

## `nasa_power_diario`

**Filas:** 12,048 · **Columnas:** 9 (incluye 3 de linaje) · **Filas duplicadas:** 0 · **Rango de fechas:** 2024-01-01 a 2026-09-30

| Columna | Tipo en Parquet | Parece | % nulos | Valores distintos |
|---|---|---|---:|---:|
| `punto` | str | texto | 0.0 | 4 |
| `latitud` | float64 | número | 0.0 | 4 |
| `longitud` | float64 | número | 0.0 | 4 |
| `variable` | str | texto | 0.0 | 3 |
| `fecha` | str | número | 0.0 | 1,004 |
| `valor` | float64 | número | 0.0 | 5,080 |

## `noaa_oni`

**Filas:** 920 · **Columnas:** 7 (incluye 3 de linaje) · **Filas duplicadas:** 0 · **Rango de fechas:** 1950-01-01 a 2026-01-01

| Columna | Tipo en Parquet | Parece | % nulos | Valores distintos |
|---|---|---|---:|---:|
| `SEAS` | str | texto | 0.0 | 12 |
| `YR` | str | número | 0.0 | 77 |
| `TOTAL` | str | número | 0.0 | 339 |
| `ANOM` | str | número | 0.0 | 308 |

## `xm_aportes_hidricos`

**Filas:** 1,004 · **Columnas:** 6 (incluye 3 de linaje) · **Filas duplicadas:** 0 · **Rango de fechas:** 2024-01-01 a 2026-09-30

| Columna | Tipo en Parquet | Parece | % nulos | Valores distintos |
|---|---|---|---:|---:|
| `Date` | str | fecha | 0.0 | 1,004 |
| `Id` | str | texto | 0.0 | 1 |
| `Value` | str | número | 0.0 | 1,004 |

## `xm_demanda`

**Filas:** 1,004 · **Columnas:** 30 (incluye 3 de linaje) · **Filas duplicadas:** 0 · **Rango de fechas:** 2024-01-01 a 2026-09-30

| Columna | Tipo en Parquet | Parece | % nulos | Valores distintos |
|---|---|---|---:|---:|
| `Date` | str | fecha | 0.0 | 1,004 |
| `Id` | str | texto | 0.0 | 1 |
| `code` | str | texto | 0.0 | 1 |
| `Hour01` | str | número | 0.0 | 1,004 |
| `Hour02` | str | número | 0.0 | 1,004 |
| `Hour03` | str | número | 0.0 | 1,004 |
| `Hour04` | str | número | 0.0 | 1,004 |
| `Hour05` | str | número | 0.0 | 1,004 |
| `Hour06` | str | número | 0.0 | 1,004 |
| `Hour07` | str | número | 0.0 | 1,004 |
| `Hour08` | str | número | 0.0 | 1,004 |
| `Hour09` | str | número | 0.0 | 1,004 |
| `Hour10` | str | número | 0.0 | 1,004 |
| `Hour11` | str | número | 0.0 | 1,004 |
| `Hour12` | str | número | 0.0 | 1,004 |
| `Hour13` | str | número | 0.0 | 1,004 |
| `Hour14` | str | número | 0.0 | 1,004 |
| `Hour15` | str | número | 0.0 | 1,004 |
| `Hour16` | str | número | 0.0 | 1,004 |
| `Hour17` | str | número | 0.0 | 1,004 |
| `Hour18` | str | número | 0.0 | 1,004 |
| `Hour19` | str | número | 0.0 | 1,004 |
| `Hour20` | str | número | 0.0 | 1,004 |
| `Hour21` | str | número | 0.0 | 1,004 |
| `Hour22` | str | número | 0.0 | 1,004 |
| `Hour23` | str | número | 0.0 | 1,004 |
| `Hour24` | str | número | 0.0 | 1,004 |

## `xm_embalses`

**Filas:** 1,004 · **Columnas:** 6 (incluye 3 de linaje) · **Filas duplicadas:** 0 · **Rango de fechas:** 2024-01-01 a 2026-09-30

| Columna | Tipo en Parquet | Parece | % nulos | Valores distintos |
|---|---|---|---:|---:|
| `Date` | str | fecha | 0.0 | 1,004 |
| `Id` | str | texto | 0.0 | 1 |
| `Value` | str | número | 0.0 | 989 |

## `xm_generacion_recurso`

**Filas:** 350,345 · **Columnas:** 30 (incluye 3 de linaje) · **Filas duplicadas:** 0 · **Rango de fechas:** 2024-01-01 a 2026-09-30

| Columna | Tipo en Parquet | Parece | % nulos | Valores distintos |
|---|---|---|---:|---:|
| `Date` | str | fecha | 0.0 | 1,004 |
| `Id` | str | texto | 0.0 | 1 |
| `code` | str | texto | 0.0 | 632 |
| `Hour01` | str | número | 51.95 | 128,393 |
| `Hour02` | str | número | 52.52 | 126,572 |
| `Hour03` | str | número | 52.69 | 125,991 |
| `Hour04` | str | número | 52.75 | 125,464 |
| `Hour05` | str | número | 52.41 | 126,486 |
| `Hour06` | str | número | 44.54 | 133,140 |
| `Hour07` | str | número | 14.92 | 176,597 |
| `Hour08` | str | número | 10.61 | 197,403 |
| `Hour09` | str | número | 8.68 | 207,868 |
| `Hour10` | str | número | 7.65 | 212,015 |
| `Hour11` | str | número | 7.08 | 213,563 |
| `Hour12` | str | número | 6.88 | 214,134 |
| `Hour13` | str | número | 6.86 | 214,268 |
| `Hour14` | str | número | 6.77 | 214,552 |
| `Hour15` | str | número | 6.87 | 214,122 |
| `Hour16` | str | número | 7.56 | 209,988 |
| `Hour17` | str | número | 8.97 | 200,266 |
| `Hour18` | str | número | 11.46 | 180,084 |
| `Hour19` | str | número | 40.37 | 139,648 |
| `Hour20` | str | número | 50.22 | 133,312 |
| `Hour21` | str | número | 50.54 | 132,930 |
| `Hour22` | str | número | 50.77 | 132,270 |
| `Hour23` | str | número | 51.32 | 130,247 |
| `Hour24` | str | número | 51.45 | 130,336 |

## `xm_listado_recursos`

**Filas:** 2,494 · **Columnas:** 14 (incluye 3 de linaje) · **Filas duplicadas:** 2 · **Rango de fechas:** 2026-10-22 a 2026-10-22

| Columna | Tipo en Parquet | Parece | % nulos | Valores distintos |
|---|---|---|---:|---:|
| `Date` | str | fecha | 0.0 | 1 |
| `Id` | str | texto | 0.0 | 1 |
| `Code` | str | texto | 0.0 | 2,492 |
| `Name` | str | texto | 0.0 | 2,492 |
| `Type` | str | texto | 0.0 | 6 |
| `Disp` | str | texto | 0.0 | 2 |
| `RecType` | str | texto | 0.0 | 9 |
| `CompanyCode` | str | texto | 0.0 | 149 |
| `EnerSource` | str | texto | 0.0 | 12 |
| `OperStartdate` | str | fecha | 0.0 | 732 |
| `State` | str | texto | 0.0 | 3 |

## `xm_precio_bolsa`

**Filas:** 1,004 · **Columnas:** 30 (incluye 3 de linaje) · **Filas duplicadas:** 0 · **Rango de fechas:** 2024-01-01 a 2026-09-30

| Columna | Tipo en Parquet | Parece | % nulos | Valores distintos |
|---|---|---|---:|---:|
| `Date` | str | fecha | 0.0 | 1,004 |
| `Id` | str | texto | 0.0 | 1 |
| `code` | str | texto | 0.0 | 1 |
| `Hour01` | str | número | 0.0 | 1,000 |
| `Hour02` | str | número | 0.0 | 1,001 |
| `Hour03` | str | número | 0.0 | 1,000 |
| `Hour04` | str | número | 0.0 | 1,001 |
| `Hour05` | str | número | 0.0 | 1,001 |
| `Hour06` | str | número | 0.0 | 1,002 |
| `Hour07` | str | número | 0.0 | 1,002 |
| `Hour08` | str | número | 0.0 | 1,001 |
| `Hour09` | str | número | 0.0 | 1,002 |
| `Hour10` | str | número | 0.0 | 1,002 |
| `Hour11` | str | número | 0.0 | 1,002 |
| `Hour12` | str | número | 0.0 | 1,002 |
| `Hour13` | str | número | 0.0 | 1,002 |
| `Hour14` | str | número | 0.0 | 1,001 |
| `Hour15` | str | número | 0.0 | 1,000 |
| `Hour16` | str | número | 0.0 | 1,001 |
| `Hour17` | str | número | 0.0 | 1,001 |
| `Hour18` | str | número | 0.0 | 998 |
| `Hour19` | str | número | 0.0 | 999 |
| `Hour20` | str | número | 0.0 | 999 |
| `Hour21` | str | número | 0.0 | 1,000 |
| `Hour22` | str | número | 0.0 | 1,000 |
| `Hour23` | str | número | 0.0 | 1,000 |
| `Hour24` | str | número | 0.0 | 999 |

<!-- HALLAZGOS -->

## Hallazgos de calidad

_(Pendiente: mínimo 5 hallazgos con su evidencia numérica.)_
