"""
Reglas de calidad (pandera) de la capa plata de IDEAM: una por cada tabla que guarda
src/silver/ideam.py. Si una fila no cumple, la limpieza se detiene y no guarda nada.
"""
import pandera.pandas as pa
from pandera.pandas import Check, Column

# ---------------------------------------------------------------------------
# IDEAM (src/silver/ideam.py)
# ---------------------------------------------------------------------------
ESQUEMA_IDEAM_PRECIPITACION = pa.DataFrameSchema(
    {
        "estacion_id": Column(str, Check.str_matches(r"^\d{10}$")),
        "fecha": Column(pa.Date),
        "precipitacion_mm": Column(float, Check.in_range(0, 500)),
        "n_obs": Column(int, Check.in_range(1, 1440)),
    },
    unique=["estacion_id", "fecha"],
    strict=True,
)

ESQUEMA_IDEAM_TEMPERATURA = pa.DataFrameSchema(
    {
        "estacion_id": Column(str, Check.str_matches(r"^\d{10}$")),
        "fecha": Column(pa.Date),
        "temp_media_c": Column(float, Check.in_range(2, 42)),
        "temp_min_c": Column(float, Check.in_range(2, 42)),
        "temp_max_c": Column(float, Check.in_range(2, 42)),
        "n_obs": Column(int, Check.in_range(1, 1440)),
    },
    # Regla de toda la tabla: minima <= media <= maxima en cada fila
    checks=Check(lambda t: (t["temp_min_c"] <= t["temp_media_c"]) & (t["temp_media_c"] <= t["temp_max_c"]),
                 name="minima <= media <= maxima"),
    unique=["estacion_id", "fecha"],
    strict=True,
)

ESQUEMA_IDEAM_ESTACIONES = pa.DataFrameSchema(
    {
        "estacion_id": Column(str, Check.str_matches(r"^\d{10}$"), unique=True),
        "nombre": Column(str),
        "municipio": Column(str),
        "divipola": Column(str, Check.str_matches(r"^\d{5}$"), nullable=True),
        "zona_hidrografica": Column(str, nullable=True),
        "latitud": Column(float, Check.in_range(5, 9)),        # Antioquia
        "longitud": Column(float, Check.in_range(-78, -73)),
    },
    strict=True,
)
