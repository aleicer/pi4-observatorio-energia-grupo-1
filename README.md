# Observatorio Energía y Clima – Equipo <nombre>

> Proyecto Integrado IV – Integración de Información · IU Digital de Antioquia · 2026-2

## 👥 Integrantes

| Nombre | Usuario GitHub | Rol |
|---|---|---|
| Aleicer Vesga | aleicer | Líder técnico / Data Engineer |
| Jaider Morales | JaiderMoraless | Data Quality Analyst |
| Aleicer Vesga | aleicer | Analytics Engineer |
| Guillermo Leon | memo-iud | BI Analyst / Storyteller |

## 🎯 Objetivo

Integrar datos del mercado eléctrico (XM), del clima (IDEAM y NOAA) y de ventas internas (EnerAndes) para analizar el riesgo energético de Colombia ante El Niño 2026.

## 📦 Fuentes de datos (capa bronce)

| Fuente | Tipo | Archivo en `data/bronze/` |
|---|---|---|
| XM – API Sinergox | API REST (POST, JSON) | `xm_precio_bolsa`, `xm_demanda`, `xm_embalses` |
| IDEAM – datos.gov.co | API Socrata (SoQL) | `ideam_precipitacion_diaria` |
| NOAA – índice ONI | Archivo de texto | `noaa_oni` |
| EnerAndes | Excel interno | `enerandes_ventas_2023` … `enerandes_ventas_2026` |

## ⚙️ Cómo ejecutar

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
# copiar ventas_enerandes_2023_2026.xlsx en data/insumos/
python -m src.pipeline          # descarga las 4 fuentes a data/bronze/ (unos 3 minutos)
python -m src.consultar         # consultas SQL de BI con DuckDB
```

Para volver a descargar todo: `python -m src.pipeline --forzar`. El rango de fechas se cambia en `src/config.py`.

## 🏗️ Arquitectura

```
Fuentes -> BRONCE (dato tal cual + linaje) -> PLATA (limpio) -> ORO (modelo estrella) -> Dashboard
```

## 🤖 Uso de IA

(Declarar aquí qué herramientas de IA se usaron y para qué.)

## 🛰️ Fuente propia: NASA POWER
**Qué es:** servicio gratuito de la NASA con datos diarios de clima y energía solar,
calculados con satélites y modelos, para cualquier punto del planeta.
**De dónde viene:** API REST https://power.larc.nasa.gov/api/temporal/daily/point
(sin usuario ni clave). Script: `src/extract/nasa_power.py` →
`data/bronze/nasa_power_diario.parquet`.
**Qué descargamos:** radiación solar (ALLSKY_SFC_SW_DWN), temperatura (T2M) y lluvia (PRECTOTCORR),
del 1-ene-2024 al 30-sep-2026, en Medellín, el embalse Peñol-Guatapé, Hidroituango y La Guajira.
**Para qué la usaremos:** responder la pregunta propia del equipo: durante El Niño 2026,
¿cuánto aumentó la radiación solar y cuánto compensó la generación solar la caída de la hidráulica?
Se cruza con XM (generación por planta + catálogo de plantas) y NOAA (ONI).
Además cubre los meses recientes que el IDEAM todavía no publica.

