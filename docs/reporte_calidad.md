# Reporte de calidad de la capa plata

> Generado con `python -m src.transformar` el 2026-10-28 19:14. No se edita a mano: se reemplaza cada vez que se construye la capa plata.

## Resumen

| Fuente | Tabla de plata | Filas en bronce | Filas en plata | Filas en cuarentena | Reglas |
|---|---|---:|---:|---:|---:|
| EnerAndes | `enerandes_ventas` | 1,114 | 1,064 | 16 | 9 |

**Total: 9 reglas de calidad y 16 filas en cuarentena.**

## EnerAndes – `enerandes_ventas`

Filas en bronce: 1,114 · Filas en plata: 1,064 · Filas en cuarentena: 16

| # | Problema | Regla aplicada | Antes | Después |
|---|---|---|---:|---:|
| 1 | Encabezado guardado como una fila | Usarlo como nombres de columna | 1 | 0 |
| 2 | Filas de totales | Eliminarlas | 1 | 0 |
| 3 | Filas duplicadas | Dejar una sola copia | 32 | 0 |
| 4 | Segmento escrito de varias formas | Unificar a 3 valores | 6 | 3 |
| 5 | Segmento vacio | Marcarlo como 'No informado' | 14 | 0 |
| 6 | Tipo de compra escrito de varias formas | Unificar a Bolsa y Contrato | 4 | 2 |
| 7 | Municipio escrito de varias formas | Unificar con el codigo DIVIPOLA | 31 | 15 |
| 8 | Energia vacia o negativa | Pasar la fila a cuarentena | 16 | 0 |
| 9 | Valor facturado vacio | Dejarlo vacio y documentarlo | 7 | 7 |

**Filas en cuarentena y por qué** (archivo `data/silver/enerandes_ventas_cuarentena.parquet`):

- Energia vacia o negativa: 16 filas
