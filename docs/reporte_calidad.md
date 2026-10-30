# Reporte de calidad de la capa plata

> Generado con `python -m src.transformar` el 2026-10-30 07:20. No se edita a mano: se reemplaza cada vez que se construye la capa plata.

## Resumen

| Fuente | Tabla de plata | Filas en bronce | Filas en plata | Filas en cuarentena | Reglas |
|---|---|---:|---:|---:|---:|
| EnerAndes | `enerandes_ventas` | 4,184 | 4,007 | 43 | 19 |
| NOAA | `noaa_oni_mensual` | 920 | 920 | 0 | 5 |

**Total: 24 reglas de calidad y 43 filas en cuarentena.**

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

## NOAA – `noaa_oni_mensual`

Filas en bronce: 920 · Filas en plata: 920 · Filas en cuarentena: 0

| # | Problema | Regla aplicada | Antes | Después |
|---|---|---|---:|---:|
| 1 | Numeros guardados como texto (YR, TOTAL, ANOM) | Convertir a numero | 920 | 0 |
| 2 | Filas sin ONI, sin anio o con trimestre desconocido | Pasar a cuarentena | 0 | 0 |
| 3 | Trimestres moviles sin mes asignado | Asignar cada trimestre a su mes central | 920 | 0 |
| 4 | Meses repetidos despues de asignar | Verificar un solo valor por mes | 0 | 0 |
| 5 | Meses sin fase ENSO | Clasificar El Niño, La Niña o Neutral | 920 | 0 |
