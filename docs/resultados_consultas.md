# Resultados de las consultas sobre la capa oro

## ¿Cómo cambia el precio de bolsa según la fase de El Niño?

Consulta: `consultas/oro/01_precio_por_fase_enso.sql`

| anio | fase_enso | dias | precio_promedio_cop_kwh | precio_maximo_cop_kwh |
|---|---|---|---|---|
| 2024 | El Niño | 121 | 624.6 | 1267.6 |
| 2024 | Neutral | 245 | 701.5 | 2675.6 |
| 2025 | La Niña | 92 | 222.8 | 1079.2 |
| 2025 | Neutral | 273 | 246.1 | 2224.0 |
| 2026 | El Niño | 153 | 693.4 | 1846.7 |
| 2026 | Neutral | 120 | 208.0 | 1175.4 |

## ¿Qué proporción de la energía viene de cada tipo de planta, por año?

Consulta: `consultas/oro/02_mezcla_generacion.sql`

| anio | tipo | generacion_twh | porcentaje |
|---|---|---|---|
| 2024 | HIDRAULICA | 54.49 | 65.4 |
| 2024 | TERMICA | 24.44 | 29.4 |
| 2024 | SOLAR | 3.3 | 4.0 |
| 2024 | COGENERADOR | 0.84 | 1.0 |
| 2024 | EOLICA | 0.15 | 0.2 |
| 2024 | DESCONOCIDO | 0.05 | 0.1 |
| 2025 | HIDRAULICA | 68.1 | 80.7 |
| 2025 | TERMICA | 10.81 | 12.8 |
| 2025 | SOLAR | 4.47 | 5.3 |
| 2025 | COGENERADOR | 0.85 | 1.0 |
| 2025 | EOLICA | 0.15 | 0.2 |
| 2025 | DESCONOCIDO | 0.02 | 0.0 |
| 2026 | HIDRAULICA | 47.53 | 71.5 |
| 2026 | TERMICA | 12.94 | 19.5 |
| 2026 | SOLAR | 5.23 | 7.9 |
| 2026 | COGENERADOR | 0.65 | 1.0 |
| 2026 | EOLICA | 0.16 | 0.2 |
| 2026 | DESCONOCIDO | 0.0 | 0.0 |

## ¿Cuánto le habría costado a EnerAndes comprar en bolsa la energía de cada año?

Consulta: `consultas/oro/03_costo_bolsa_enerandes.sql`

| anio | energia_gwh | costo_en_bolsa_mil_millones_cop |
|---|---|---|
| 2024 | 736.6 | 493.2 |
| 2025 | 770.6 | 183.6 |
| 2026 | 595.3 | 287.8 |

## Pregunta propia: ¿sube la radiación solar y la generación solar en los meses de El Niño?

Consulta: `consultas/oro/04_radiacion_vs_solar.sql`

| fase_enso | radiacion_promedio_kwh_m2 | solar_gwh_por_mes |
|---|---|---|
| El Niño | 6.05 | 450.7 |
| Neutral | 5.67 | 365.8 |
| La Niña | 4.93 | 420.4 |
