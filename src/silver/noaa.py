
"""
Capa plata: índice ONI de NOAA por mes.

Convierte los trimestres móviles a su mes central
y clasifica la fase ENSO: El Niño, La Niña o Neutral.
"""

import pandas as pd

from src import config
from src.quality.esquemas import ESQUEMA_NOAA
from src.silver.comun import LINAJE, Medidor, guardar_plata
from src.utils import log


# Cada trimestre móvil corresponde a su mes central.
MES_CENTRAL = {
    "DJF": 1, "JFM": 2, "FMA": 3, "MAM": 4,
    "AMJ": 5, "MJJ": 6, "JJA": 7, "JAS": 8,
    "ASO": 9, "SON": 10, "OND": 11, "NDJ": 12,
}


def fase_enso(oni: float) -> str:
    """Clasifica la fase según el valor del ONI."""
    if oni >= 0.5:
        return "El Niño"
    if oni <= -0.5:
        return "La Niña"
    return "Neutral"


def limpiar(bronce: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame, list[dict]]:
    """Limpia NOAA y devuelve datos, cuarentena y métricas."""
    m = Medidor()
    df = bronce.drop(columns=LINAJE, errors="ignore").copy()

    # Regla 1: convertir los números que llegaron como texto.
    antes = int(df["ANOM"].map(lambda v: isinstance(v, str)).sum())
    for col in ["YR", "TOTAL", "ANOM"]:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    m.medir(
        "Numeros guardados como texto (YR, TOTAL, ANOM)",
        "Convertir a numero", antes, 0
    )

    # Regla 2: separar los registros que no se pueden utilizar.
    malas = (
        df["ANOM"].isna()
        | df["YR"].isna()
        | ~df["SEAS"].isin(MES_CENTRAL)
    )
    cuarentena = df[malas].assign(
        motivo_cuarentena="ONI, anio o trimestre invalido"
    )
    df = df[~malas].copy()

    m.medir(
        "Filas sin ONI, sin anio o con trimestre desconocido",
        "Pasar a cuarentena",
        int(malas.sum()), 0
    )

    # Regla 3: asignar el mes central.
    df["anio"] = df["YR"].astype(int)
    df["mes"] = df["SEAS"].map(MES_CENTRAL)
    df["periodo"] = (
        df["anio"].astype(str)
        + "-"
        + df["mes"].astype(str).str.zfill(2)
    )

    m.medir(
        "Trimestres moviles sin mes asignado",
        "Asignar cada trimestre a su mes central",
        len(df),
        int(df["periodo"].isna().sum())
    )

    duplicados = int(df["periodo"].duplicated().sum())
    m.medir(
        "Meses repetidos despues de asignar",
        "Verificar un solo valor por mes",
        duplicados,
        duplicados
    )

    # Regla 4: clasificar la fase ENSO.
    df["fase_enso"] = df["ANOM"].map(fase_enso)
    m.medir(
        "Meses sin fase ENSO",
        "Clasificar El Niño, La Niña o Neutral",
        len(df),
        int(df["fase_enso"].isna().sum())
    )

    limpias = (
        df.rename(columns={
            "SEAS": "trimestre_movil",
            "ANOM": "oni",
            "TOTAL": "temp_mar_c",
        })[
            [
                "periodo", "anio", "mes", "trimestre_movil",
                "oni", "temp_mar_c", "fase_enso"
            ]
        ]
        .sort_values("periodo")
        .reset_index(drop=True)
    )

    return limpias, cuarentena, m.metricas


def main() -> None:
    bronce = pd.read_parquet(
        config.DIR_BRONZE / "noaa_oni.parquet"
    )
    log(f"   Bronce: {len(bronce):,} filas")

    limpias, cuarentena, metricas = limpiar(bronce)

    guardar_plata(
        limpias, "noaa_oni_mensual", ESQUEMA_NOAA,
        "NOAA", metricas, len(bronce), cuarentena
    )


if __name__ == "__main__":
    main()
