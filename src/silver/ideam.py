"""
Capa PLATA: clima del IDEAM (precipitacion y temperatura por estacion y dia).

En bronce todo viene como texto y la fecha con hora ('2025-01-01T00:00:00.000').
Aqui: la fecha queda como fecha, los valores como numeros, cada estacion con su
municipio (y su codigo DIVIPOLA cuando es un municipio de EnerAndes), y los dias con
valores imposibles van a cuarentena.

Tablas que guarda en data/silver/:
  - ideam_precipitacion_diaria   lluvia por estacion y dia
  - ideam_temperatura_diaria     temperatura media, minima y maxima por estacion y dia
  - ideam_estaciones             una fila por estacion (nombre, municipio, cuenca, coordenadas)

Uso:
    python -m src.silver.ideam
"""
import pandas as pd

from src import config
from src.quality.esquemas_ideam import ESQUEMA_IDEAM_ESTACIONES, ESQUEMA_IDEAM_PRECIPITACION, ESQUEMA_IDEAM_TEMPERATURA
from src.silver.comun import LINAJE, Medidor, guardar_plata
from src.silver.enerandes import MUNICIPIOS, clave_municipio
from src.utils import log

MINUTOS_DIA = 1440          # una estacion no puede medir mas de una vez por minuto
LLUVIA_MAXIMA_MM = 500      # mas de 500 mm en un dia es imposible en Antioquia
TEMP_MINIMA_C = 2           # por debajo de 2 °C es un sensor en cero (Medellin, Rionegro...)
TEMP_MAXIMA_C = 42          # por encima de 42 °C es un error del sensor
ESTACION = ["codigoestacion", "nombreestacion", "municipio", "zonahidrografica", "latitud", "longitud"]


def comunes(df: pd.DataFrame, m: Medidor, valores: list[str]) -> pd.DataFrame:
    """Reglas que comparten los dos datasets: fecha, numeros y estacion-dia repetida."""
    df = df.drop(columns=LINAJE, errors="ignore").copy()
    df["fecha"] = pd.to_datetime(df["fecha"]).dt.date
    m.medir("Fecha como texto con hora ('2025-01-01T00:00:00.000')", "Convertir a fecha", len(df), 0)
    for col in valores + ["n_obs"]:
        df[col] = pd.to_numeric(df[col], errors="coerce")
    m.medir("Valores guardados como texto", "Convertir a número", len(df), 0)
    antes = int(df.duplicated(["codigoestacion", "fecha"]).sum())
    df = df.drop_duplicates(["codigoestacion", "fecha"])
    m.medir("Estación y día repetidos", "Dejar uno solo", antes, 0)
    return df


def limpiar_precipitacion(bronce: pd.DataFrame):
    m = Medidor()
    df = comunes(bronce, m, ["precipitacion_mm"])
    cuarentenas = []
    # Cada regla es una funcion (lambda d: ...) que se evalua sobre lo que queda despues
    # de la regla anterior: asi una fila mala se cuenta una sola vez
    reglas = [
        (lambda d: d["n_obs"] > MINUTOS_DIA, "Más observaciones que minutos del día (datos repetidos en la fuente)"),
        (lambda d: d["precipitacion_mm"] > LLUVIA_MAXIMA_MM, f"Lluvia imposible (más de {LLUVIA_MAXIMA_MM} mm en un día)"),
        (lambda d: d["precipitacion_mm"].isna() | (d["precipitacion_mm"] < 0), "Lluvia vacía o negativa"),
    ]
    for regla, motivo in reglas:
        malas = regla(df)
        cuarentenas.append(df[malas].assign(motivo_cuarentena=motivo))
        m.medir(motivo, "Pasar a cuarentena", int(malas.sum()), 0)
        df = df[~malas]
    limpias = df[["codigoestacion", "fecha", "precipitacion_mm", "n_obs"]].rename(
        columns={"codigoestacion": "estacion_id"})
    limpias["n_obs"] = limpias["n_obs"].astype(int)
    return limpias.reset_index(drop=True), pd.concat(cuarentenas), m.metricas


def limpiar_temperatura(bronce: pd.DataFrame):
    m = Medidor()
    df = comunes(bronce, m, ["temp_media_c", "temp_min_c", "temp_max_c"])
    cuarentenas = []
    reglas = [
        (lambda d: d["n_obs"] > MINUTOS_DIA, "Más observaciones que minutos del día (datos repetidos en la fuente)"),
        (lambda d: d["temp_min_c"] < TEMP_MINIMA_C, f"Temperatura mínima menor a {TEMP_MINIMA_C} °C (sensor en cero)"),
        (lambda d: d["temp_max_c"] > TEMP_MAXIMA_C, f"Temperatura máxima mayor a {TEMP_MAXIMA_C} °C (error del sensor)"),
        (lambda d: (d["temp_min_c"] > d["temp_media_c"]) | (d["temp_media_c"] > d["temp_max_c"]),
         "Mínima mayor que la media o media mayor que la máxima"),
    ]
    for regla, motivo in reglas:
        malas = regla(df)
        cuarentenas.append(df[malas].assign(motivo_cuarentena=motivo))
        m.medir(motivo, "Pasar a cuarentena", int(malas.sum()), 0)
        df = df[~malas]
    df["temp_media_c"] = df["temp_media_c"].round(2)
    m.medir("Temperatura media con 16 decimales", "Redondear a 2 decimales", len(df), 0)
    limpias = df[["codigoestacion", "fecha", "temp_media_c", "temp_min_c", "temp_max_c", "n_obs"]].rename(
        columns={"codigoestacion": "estacion_id"})
    limpias["n_obs"] = limpias["n_obs"].astype(int)
    return limpias.reset_index(drop=True), pd.concat(cuarentenas), m.metricas


def limpiar_estaciones(*bronces: pd.DataFrame):
    """Una fila por estacion, con el municipio escrito bien y su DIVIPOLA si es de EnerAndes."""
    m = Medidor()
    # Cada estacion aparece una vez por dia en cada dataset: se dejan sus datos una sola vez
    df = pd.concat([b[ESTACION] for b in bronces])
    antes = int(df.duplicated("codigoestacion").sum())
    df = df.drop_duplicates("codigoestacion")
    m.medir("Datos de la estación repetidos en cada fila de los dos datasets", "Dejar una fila por estación",
            antes, 0)
    antes = int((df["municipio"] == df["municipio"].str.upper()).sum())
    df["municipio"] = df["municipio"].str.strip().str.title()
    m.medir("Municipio en MAYÚSCULAS ('MEDELLÍN')", "Escribirlo como nombre propio ('Medellín')", antes, 0)
    claves = df["municipio"].map(clave_municipio)
    df["divipola"] = claves.map(lambda c: MUNICIPIOS[c][0] if c in MUNICIPIOS else None)
    m.medir("Estaciones sin código de municipio", "Asignar DIVIPOLA a las de municipios de EnerAndes",
            len(df), int(df["divipola"].isna().sum()))
    for col in ["latitud", "longitud"]:
        df[col] = pd.to_numeric(df[col], errors="coerce")
    limpias = df.rename(columns={"codigoestacion": "estacion_id", "nombreestacion": "nombre",
                                 "zonahidrografica": "zona_hidrografica"})
    limpias = limpias[["estacion_id", "nombre", "municipio", "divipola", "zona_hidrografica", "latitud", "longitud"]]
    return limpias.sort_values("estacion_id").reset_index(drop=True), None, m.metricas


def main() -> None:
    lluvia = pd.read_parquet(config.DIR_BRONZE / "ideam_precipitacion_diaria.parquet")
    temp = pd.read_parquet(config.DIR_BRONZE / "ideam_temperatura_diaria.parquet")
    limpias, cuarentena, metricas = limpiar_precipitacion(lluvia)
    guardar_plata(limpias, "ideam_precipitacion_diaria", ESQUEMA_IDEAM_PRECIPITACION, "IDEAM", metricas,
                  len(lluvia), cuarentena)
    limpias, cuarentena, metricas = limpiar_temperatura(temp)
    guardar_plata(limpias, "ideam_temperatura_diaria", ESQUEMA_IDEAM_TEMPERATURA, "IDEAM", metricas,
                  len(temp), cuarentena)
    limpias, cuarentena, metricas = limpiar_estaciones(lluvia, temp)
    guardar_plata(limpias, "ideam_estaciones", ESQUEMA_IDEAM_ESTACIONES, "IDEAM", metricas,
                  len(lluvia) + len(temp), cuarentena)


if __name__ == "__main__":
    main()
