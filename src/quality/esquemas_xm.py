"""
Reglas de calidad (pandera) de la capa plata de XM: una por cada tabla que guarda
src/silver/xm.py. Si una fila no cumple, la limpieza se detiene y no guarda nada.
"""
import pandera.pandas as pa
from pandera.pandas import Check, Column

# ---------------------------------------------------------------------------
# XM (src/silver/xm.py)
# ---------------------------------------------------------------------------
ESQUEMA_XM_MERCADO = pa.DataFrameSchema(
    {
        "fecha": Column(pa.Date),
        "hora": Column(int, Check.in_range(0, 23)),
        # Precio de bolsa en COP/kWh: positivo y por debajo del maximo historico con margen
        "precio_bolsa_cop_kwh": Column(float, Check.in_range(0, 5000, include_min=False), nullable=True),
        # Demanda horaria del pais en kWh: entre 1 y 20 millones
        "demanda_kwh": Column(float, Check.in_range(1e6, 2e7), nullable=True),
    },
    unique=["fecha", "hora"],
    strict=True,
)

ESQUEMA_XM_GENERACION = pa.DataFrameSchema(
    {
        "fecha": Column(pa.Date),
        "hora": Column(int, Check.in_range(0, 23)),
        "recurso_id": Column(str, Check.str_length(1, 10)),
        # La planta mas grande del pais genera unos 1,3 millones de kWh en una hora
        "generacion_kwh": Column(float, Check.in_range(0, 3e6)),
    },
    unique=["fecha", "hora", "recurso_id"],
    strict=True,
)

ESQUEMA_XM_HIDROLOGIA = pa.DataFrameSchema(
    {
        "fecha": Column(pa.Date),
        "volumen_util_pct": Column(float, Check.in_range(0, 100), nullable=True),
        "aportes_kwh": Column(float, Check.ge(0), nullable=True),
    },
    unique=["fecha"],
    strict=True,
)

ESQUEMA_XM_RECURSOS = pa.DataFrameSchema(
    {
        "recurso_id": Column(str, unique=True),
        "nombre": Column(str),
        "tipo": Column(str, Check.isin(["HIDRAULICA", "TERMICA", "SOLAR", "EOLICA",
                                        "COGENERADOR", "DESCONOCIDO"])),
        "fuente_energia": Column(str, nullable=True),
        "despacho": Column(str, nullable=True),
        "clase": Column(str, nullable=True),
        "agente": Column(str, nullable=True),
        "fecha_operacion": Column(pa.Date, nullable=True),
        "estado": Column(str, Check.isin(["OPERACION", "PRUEBAS", "DESCONOCIDO"])),
    },
    strict=True,
)
