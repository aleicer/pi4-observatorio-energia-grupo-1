# Reporte de calidad de la capa plata

> Generado con `python -m src.transformar` el 2026-10-31 09:17. No se edita a mano: se reemplaza cada vez que se construye la capa plata.

## Resumen

| Fuente | Tabla de plata | Filas en bronce | Filas en plata | Filas en cuarentena | Reglas |
|---|---|---:|---:|---:|---:|
| EnerAndes | `enerandes_ventas` | 4,184 | 4,007 | 43 | 19 |
| IDEAM | `ideam_estaciones` | 47,153 | 73 | 0 | 3 |
| IDEAM | `ideam_precipitacion_diaria` | 29,804 | 29,691 | 113 | 6 |
| IDEAM | `ideam_temperatura_diaria` | 17,349 | 16,720 | 629 | 8 |
| NOAA | `noaa_oni_mensual` | 920 | 920 | 0 | 5 |
| XM | `xm_generacion_recurso` | 350,345 | 5,935,362 | 0 | 4 |
| XM | `xm_hidrologia_diaria` | 2,008 | 1,004 | 0 | 4 |
| XM | `xm_mercado_horario` | 2,008 | 24,096 | 0 | 6 |
| XM | `xm_recursos` | 2,493 | 2,501 | 0 | 4 |

**Total: 59 reglas de calidad y 785 filas en cuarentena.**

## EnerAndes – `enerandes_ventas`

Filas en bronce: 4,184 · Filas en plata: 4,007 · Filas en cuarentena: 43

| # | Problema | Regla aplicada | Antes | Después |
|---|---|---|---:|---:|
| 1 | Encabezados distintos en cada hoja | Traducir cada encabezado a 8 nombres estándar | 4 | 1 |
| 2 | Títulos y notas encima del encabezado | Buscar la fila del encabezado y quitar lo de arriba | 4 | 0 |
| 3 | Filas de totales | Eliminarlas (no son ventas) | 4 | 0 |
| 4 | Filas duplicadas exactas | Dejar una sola copia | 120 | 0 |
| 5 | Fechas en 4 formatos distintos (2024-03, mar-24, 03/2024, 01/03/2026) | Leer cada formato y dejar AAAA-MM | 4 | 1 |
| 6 | Fechas que no estaban en formato AAAA-MM | Convertirlas a AAAA-MM | 2,626 | 0 |
| 7 | Fechas día/mes/año de la hoja 2026 (01/03/2026) | Tomar el MES del segundo número (marzo) | 810 | 0 |
| 8 | Energía en MWh mezclada con kWh (hoja 2024) | Multiplicar por 1.000 y dejar todo en kWh | 337 | 0 |
| 9 | Segmento escrito de varias formas | Unificar a Residencial, Comercial e Industrial | 6 | 3 |
| 10 | Segmento vacío | Marcarlo como 'No informado' | 28 | 0 |
| 11 | Tipo de compra escrito de varias formas | Unificar a Bolsa y Contrato | 4 | 2 |
| 12 | Municipio escrito de varias formas | Unificar con el código DIVIPOLA | 32 | 15 |
| 13 | Ventas repetidas que solo cambiaban en la escritura | Dejar una sola copia después de unificar | 0 | 0 |
| 14 | Energía vacía | Pasar la fila a cuarentena | 25 | 0 |
| 15 | Energía negativa | Pasar la fila a cuarentena | 18 | 0 |
| 16 | Clientes vacíos o negativos | Pasar la fila a cuarentena | 0 | 0 |
| 17 | Valor facturado negativo | Dejarlo vacío (no se inventa un valor) | 0 | 0 |
| 18 | Valor facturado vacío | Dejarlo vacío y documentarlo | 28 | 28 |
| 19 | Misma venta (mes, municipio, segmento y tipo) con valores distintos | Pasar todas sus copias a cuarentena | 0 | 0 |

**Filas en cuarentena y por qué** (archivo `data/silver/enerandes_ventas_cuarentena.parquet`):

- Energía vacía: 25 filas
- Energía negativa: 18 filas

## IDEAM – `ideam_estaciones`

Filas en bronce: 47,153 · Filas en plata: 73 · Filas en cuarentena: 0

| # | Problema | Regla aplicada | Antes | Después |
|---|---|---|---:|---:|
| 1 | Datos de la estación repetidos en cada fila de los dos datasets | Dejar una fila por estación | 47,080 | 0 |
| 2 | Municipio en MAYÚSCULAS ('MEDELLÍN') | Escribirlo como nombre propio ('Medellín') | 73 | 0 |
| 3 | Estaciones sin código de municipio | Asignar DIVIPOLA a las de municipios de EnerAndes | 73 | 58 |

## IDEAM – `ideam_precipitacion_diaria`

Filas en bronce: 29,804 · Filas en plata: 29,691 · Filas en cuarentena: 113

| # | Problema | Regla aplicada | Antes | Después |
|---|---|---|---:|---:|
| 1 | Fecha como texto con hora ('2025-01-01T00:00:00.000') | Convertir a fecha | 29,804 | 0 |
| 2 | Valores guardados como texto | Convertir a número | 29,804 | 0 |
| 3 | Estación y día repetidos | Dejar uno solo | 0 | 0 |
| 4 | Más observaciones que minutos del día (datos repetidos en la fuente) | Pasar a cuarentena | 111 | 0 |
| 5 | Lluvia imposible (más de 500 mm en un día) | Pasar a cuarentena | 2 | 0 |
| 6 | Lluvia vacía o negativa | Pasar a cuarentena | 0 | 0 |

**Filas en cuarentena y por qué** (archivo `data/silver/ideam_precipitacion_diaria_cuarentena.parquet`):

- Más observaciones que minutos del día (datos repetidos en la fuente): 111 filas
- Lluvia imposible (más de 500 mm en un día): 2 filas

## IDEAM – `ideam_temperatura_diaria`

Filas en bronce: 17,349 · Filas en plata: 16,720 · Filas en cuarentena: 629

| # | Problema | Regla aplicada | Antes | Después |
|---|---|---|---:|---:|
| 1 | Fecha como texto con hora ('2025-01-01T00:00:00.000') | Convertir a fecha | 17,349 | 0 |
| 2 | Valores guardados como texto | Convertir a número | 17,349 | 0 |
| 3 | Estación y día repetidos | Dejar uno solo | 0 | 0 |
| 4 | Más observaciones que minutos del día (datos repetidos en la fuente) | Pasar a cuarentena | 15 | 0 |
| 5 | Temperatura mínima menor a 2 °C (sensor en cero) | Pasar a cuarentena | 605 | 0 |
| 6 | Temperatura máxima mayor a 42 °C (error del sensor) | Pasar a cuarentena | 9 | 0 |
| 7 | Mínima mayor que la media o media mayor que la máxima | Pasar a cuarentena | 0 | 0 |
| 8 | Temperatura media con 16 decimales | Redondear a 2 decimales | 16,720 | 0 |

**Filas en cuarentena y por qué** (archivo `data/silver/ideam_temperatura_diaria_cuarentena.parquet`):

- Temperatura mínima menor a 2 °C (sensor en cero): 605 filas
- Más observaciones que minutos del día (datos repetidos en la fuente): 15 filas
- Temperatura máxima mayor a 42 °C (error del sensor): 9 filas

## NOAA – `noaa_oni_mensual`

Filas en bronce: 920 · Filas en plata: 920 · Filas en cuarentena: 0

| # | Problema | Regla aplicada | Antes | Después |
|---|---|---|---:|---:|
| 1 | Numeros guardados como texto (YR, TOTAL, ANOM) | Convertir a numero | 920 | 0 |
| 2 | Filas sin ONI, sin anio o con trimestre desconocido | Pasar a cuarentena | 0 | 0 |
| 3 | Trimestres moviles sin mes asignado | Asignar cada trimestre a su mes central | 920 | 0 |
| 4 | Meses repetidos despues de asignar | Verificar un solo valor por mes | 0 | 0 |
| 5 | Meses sin fase ENSO | Clasificar El Niño, La Niña o Neutral | 920 | 0 |

## XM – `xm_generacion_recurso`

Filas en bronce: 350,345 · Filas en plata: 5,935,362 · Filas en cuarentena: 0

| # | Problema | Regla aplicada | Antes | Después |
|---|---|---|---:|---:|
| 1 | Filas en formato ancho: 24 columnas por hora (generación) | Pasar a una fila por fecha, hora y planta | 350,345 | 0 |
| 2 | Horas sin generación reportada (celda vacía, p. ej. solares de noche) | No guardarlas: no son una medición | 2,472,918 | 0 |
| 3 | Generación repetida (misma planta, fecha y hora) | Dejar una sola | 0 | 0 |
| 4 | Generación negativa | Pasar a cuarentena | 0 | 0 |

## XM – `xm_hidrologia_diaria`

Filas en bronce: 2,008 · Filas en plata: 1,004 · Filas en cuarentena: 0

| # | Problema | Regla aplicada | Antes | Después |
|---|---|---|---:|---:|
| 1 | Fecha y valores diarios guardados como texto | Convertir a fecha y a número | 2,008 | 0 |
| 2 | Volumen útil como fracción (0,70) | Pasarlo a porcentaje (70 %) | 1,004 | 0 |
| 3 | Días repetidos | Dejar uno solo | 0 | 0 |
| 4 | Volumen útil fuera de 0-100 % o aportes negativos | Pasar a cuarentena | 0 | 0 |

## XM – `xm_mercado_horario`

Filas en bronce: 2,008 · Filas en plata: 24,096 · Filas en cuarentena: 0

| # | Problema | Regla aplicada | Antes | Después |
|---|---|---|---:|---:|
| 1 | Filas en formato ancho: 24 columnas por hora (precio y demanda) | Pasar a una fila por fecha y hora | 2,008 | 0 |
| 2 | Valores horarios guardados como texto | Convertirlos a número | 48,192 | 0 |
| 3 | Horas con precio o demanda faltante | Dejar vacío (no se inventa) | 0 | 0 |
| 4 | Horas repetidas | Dejar una sola | 0 | 0 |
| 5 | Precio o demanda cero o negativos | Pasar a cuarentena | 0 | 0 |
| 6 | Días sin sus 24 horas | Verificar que cada día tenga 24 horas | 0 | 0 |

## XM – `xm_recursos`

Filas en bronce: 2,493 · Filas en plata: 2,501 · Filas en cuarentena: 0

| # | Problema | Regla aplicada | Antes | Después |
|---|---|---|---:|---:|
| 1 | Tipo y estado escritos de varias formas ('Solar' / 'SOLAR') | Pasar a mayúsculas sin tildes | 9 | 7 |
| 2 | Plantas repetidas en el catálogo | Dejar una sola | 2 | 0 |
| 3 | Fecha de entrada en operación como texto | Convertir a fecha | 2,491 | 0 |
| 4 | Plantas que generan pero no están en el catálogo | Agregarlas con tipo 'DESCONOCIDO' | 10 | 0 |
