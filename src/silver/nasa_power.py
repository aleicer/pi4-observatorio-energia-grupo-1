"""
Capa PLATA: NASA POWER (fuente propia), clima y radiacion solar diaria.
En bronce viene en formato LARGO: una fila por punto, variable y dia, con la fecha como texto AAAAMMDD y el valor -999 cuando NASA no tiene el dato.
Aqui:
  - el -999 pasa a vacio (no es una medicion: es "sin dato")
  - la fecha pasa a fecha
  - se pasa a formato ANCHO: una fila por punto y dia, con una columna por variable
Uso:
    python -m src.silver.nasa_power
"""

import numpy as np
import pandas as pd
from src import config
from src.quality.esquemas import ESQUEMA_NASA
from src.silver.comun import LINAJE, Medidor, guardar_plata
from src.utils import log

SIN_DATO = -999           # valor que usa NASA POWER cuando no hay dato

# Codigo de NASA -> nombre de la columna en plata
VARIABLES = {
    "ALLSKY_SFC_SW_DWN": "radiacion_kwh_m2",
    "T2M": "temperatura_c",
    "PRECTOTCORR": "precipitacion_mm"
}

def limpiar(bronce: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame, list[dict]]:
    """Aplica las reglas en orden. Devuelve (limpias, cuarentena, metricas)."""
    m = Medidor()
    df = bronce.drop(columns=LINAJE, errors="ignore").copy()
    # Regla 1. El -999 no es una medicion: significa "sin dato" -> vacio
    df["valor"] = pd.to_numeric(df["valor"], errors="coerce")
    antes = int((df["valor"] == SIN_DATO).sum())
    df["valor"] = df["valor"].replace(SIN_DATO, np.nan)
    m.medir(
        "Valor -999 (sin dato) tratado como numero",
        "Cambiarlo por vacio",
        antes,
        int((df["valor"] == SIN_DATO).sum())
    )
    # Regla 2. La fecha llego como texto AAAAMMDD -> fecha
    fechas = pd.to_datetime(df["fecha"], format="%Y%m%d", errors="coerce")
    m.medir("Fecha como texto AAAAMMDD", "Convertir a fecha", len(df), int(fechas.isna().sum()))
    df["fecha"] = fechas.dt.date
    # Regla 3. Filas repetidas (mismo punto, variable y dia)
    antes = int(df.duplicated(["punto", "variable", "fecha"]).sum())
    df = df.drop_duplicates(["punto", "variable", "fecha"])
    m.medir("Mediciones repetidas", "Dejar una sola", antes, 0)

    # Regla 4. Formato largo -> ancho: una fila por punto y dia
    antes = len(df)
    df["variable"] = df["variable"].map(VARIABLES)

    # pivot: las filas quedan por punto y dia, y cada variable se vuelve una columna
    ancho = df.pivot(
        index=["punto", "latitud", "longitud", "fecha"],
        columns="variable",
        values="valor"
    ).reset_index()
    ancho.columns.name = None
    m.medir(
        "Una fila por variable (formato largo)",
        "Pasar a una fila por punto y dia",
        antes,
        len(ancho)
    )

    limpias = ancho[[
        "punto", "latitud", "longitud", "fecha",
        "radiacion_kwh_m2", "temperatura_c", "precipitacion_mm"
    ]]
    limpias = limpias.sort_values(["punto", "fecha"]).reset_index(drop=True)

    return limpias, None, m.metricas

def main() -> None:
    ruta_bronce = config.DIR_BRONZE / "nasa_power_diario.parquet"
    if not ruta_bronce.exists():
        raise FileNotFoundError(
            f"No existe el archivo de entrada: {ruta_bronce}\n"
            "Primero genera la capa bronce ejecutando desde la raiz del proyecto:\n"
            "  python -m src.extract.nasa_power\n"
            "o ejecuta el pipeline completo con: python -m src.pipeline"
        )

    bronce = pd.read_parquet(ruta_bronce)
    log(f"   Bronce: {len(bronce):,} filas")

    limpias, cuarentena, metricas = limpiar(bronce)

    guardar_plata(
        limpias,
        "nasa_power_diario",
        ESQUEMA_NASA,
        "NASA POWER",
        metricas,
        len(bronce),
        cuarentena,
    )


if __name__ == "__main__":
    main()