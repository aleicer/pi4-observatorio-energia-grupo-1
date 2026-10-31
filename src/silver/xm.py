"""
Capa PLATA: datos de XM (mercado electrico).

En bronce, los datos horarios vienen en formato ANCHO: una fila por dia con 24 columnas
(Hour01 ... Hour24). Aqui se pasan a una fila por FECHA y HORA, con los valores como
numeros, y se limpian tambien los datos diarios y el catalogo de plantas.

Tablas que guarda en data/silver/:
  - xm_mercado_horario       precio de bolsa y demanda, por fecha y hora
  - xm_generacion_recurso    generacion de cada planta, por fecha y hora
  - xm_hidrologia_diaria     % de volumen util de los embalses y aportes hidricos, por dia
  - xm_recursos              catalogo de plantas (ListadoRecursos)

Uso:
    python -m src.silver.xm
"""
# ---------------------------------------------------------------------------
# IMPORTS
# ---------------------------------------------------------------------------
import pandas as pd

from src import config
from src.quality.esquemas_xm import (ESQUEMA_XM_GENERACION, ESQUEMA_XM_HIDROLOGIA,
                                  ESQUEMA_XM_MERCADO, ESQUEMA_XM_RECURSOS)
from src.silver.comun import LINAJE, Medidor, guardar_plata
from src.silver.enerandes import sin_tildes
from src.utils import log


def leer_bronce(nombre: str) -> pd.DataFrame:
    """Lee un archivo de bronce de XM y le quita las columnas de linaje."""
    return pd.read_parquet(config.DIR_BRONZE / f"{nombre}.parquet").drop(columns=LINAJE, errors="ignore")


# ---------------------------------------------------------------------------
# REGLA CLAVE: de 24 columnas por hora a una fila por hora
# ---------------------------------------------------------------------------
def a_formato_largo(ancho: pd.DataFrame, columna_valor: str) -> pd.DataFrame:
    """Pasa una tabla de XM de 24 columnas (Hour01..Hour24) a una fila por fecha y hora.

        Date        Hour01  Hour02 ...          fecha       hora  precio
        2026-09-01  250.5   240.1      ->       2026-09-01  0     250.5
                                                2026-09-01  1     240.1

    - Hour01 es la hora 0 (de 00:00 a 01:00) ... Hour24 es la hora 23.
    - El valor pasa de texto a numero. Las celdas vacias quedan como NaN.
    - Las demas columnas (por ejemplo 'code', la planta) se conservan; 'Id' se quita.
    """
    horas = [c for c in ancho.columns if c.startswith("Hour")]
    otras = [c for c in ancho.columns if c not in horas and c != "Id"]
    # melt: cada columna HourXX se vuelve una fila, con su nombre en 'columna_hora'
    largo = ancho.drop(columns=["Id"], errors="ignore").melt(
        id_vars=otras, value_vars=horas, var_name="columna_hora", value_name=columna_valor)
    largo["hora"] = largo["columna_hora"].str[4:].astype(int) - 1        # 'Hour01' -> 0
    largo["fecha"] = pd.to_datetime(largo["Date"]).dt.date               # texto -> fecha
    largo[columna_valor] = pd.to_numeric(largo[columna_valor], errors="coerce")   # '' -> NaN
    resto = [c for c in otras if c != "Date"]
    return (largo[["fecha", "hora", *resto, columna_valor]]
            .sort_values(["fecha", *resto, "hora"]).reset_index(drop=True))


# ---------------------------------------------------------------------------
# LIMPIEZAS
# ---------------------------------------------------------------------------
def limpiar_mercado(precio: pd.DataFrame, demanda: pd.DataFrame):
    """Precio de bolsa y demanda -> una fila por fecha y hora. Devuelve (limpias, cuarentena, metricas)."""
    m = Medidor()
    p = a_formato_largo(precio, "precio_bolsa_cop_kwh").drop(columns=["code"], errors="ignore")
    d = a_formato_largo(demanda, "demanda_kwh").drop(columns=["code"], errors="ignore")
    m.medir("Filas en formato ancho: 24 columnas por hora (precio y demanda)", "Pasar a una fila por fecha y hora",
            len(precio) + len(demanda), 0)
    m.medir("Valores horarios guardados como texto", "Convertirlos a número",
            (len(p) + len(d)), 0)
    df = p.merge(d, on=["fecha", "hora"], how="outer")       # outer: no se pierde ninguna hora
    m.medir("Horas con precio o demanda faltante", "Dejar vacío (no se inventa)",
            int(df[["precio_bolsa_cop_kwh", "demanda_kwh"]].isna().any(axis=1).sum()), 0)

    antes = int(df.duplicated(["fecha", "hora"]).sum())
    df = df.drop_duplicates(["fecha", "hora"])
    m.medir("Horas repetidas", "Dejar una sola", antes, 0)

    malas = (df["precio_bolsa_cop_kwh"] <= 0) | (df["demanda_kwh"] <= 0)
    cuarentena = df[malas].assign(motivo_cuarentena="Precio o demanda cero o negativos")
    df = df[~malas]
    m.medir("Precio o demanda cero o negativos", "Pasar a cuarentena", int(malas.sum()), 0)

    dias_incompletos = int((df.groupby("fecha").size() != 24).sum())
    m.medir("Días sin sus 24 horas", "Verificar que cada día tenga 24 horas", dias_incompletos, dias_incompletos)
    return df.reset_index(drop=True), cuarentena, m.metricas


def limpiar_generacion(gene: pd.DataFrame):
    """Generacion por planta -> una fila por fecha, hora y planta."""
    m = Medidor()
    df = a_formato_largo(gene, "generacion_kwh").rename(columns={"code": "recurso_id"})
    m.medir("Filas en formato ancho: 24 columnas por hora (generación)", "Pasar a una fila por fecha, hora y planta",
            len(gene), 0)
    # Las celdas vacias son horas en que la planta no reporto (sobre todo solares de noche):
    # no son una medicion, asi que no se guardan
    vacias = df["generacion_kwh"].isna()
    m.medir("Horas sin generación reportada (celda vacía, p. ej. solares de noche)",
            "No guardarlas: no son una medición", int(vacias.sum()), 0)
    df = df[~vacias]

    antes = int(df.duplicated(["fecha", "hora", "recurso_id"]).sum())
    df = df.drop_duplicates(["fecha", "hora", "recurso_id"])
    m.medir("Generación repetida (misma planta, fecha y hora)", "Dejar una sola", antes, 0)

    negativa = df["generacion_kwh"] < 0
    cuarentena = df[negativa].assign(motivo_cuarentena="Generación negativa")
    df = df[~negativa]
    m.medir("Generación negativa", "Pasar a cuarentena", int(negativa.sum()), 0)
    return df.reset_index(drop=True), cuarentena, m.metricas


def limpiar_hidrologia(embalses: pd.DataFrame, aportes: pd.DataFrame):
    """Volumen util de embalses (%) y aportes hidricos (kWh) -> una fila por dia."""
    m = Medidor()
    e = embalses.assign(fecha=pd.to_datetime(embalses["Date"]).dt.date,
                        volumen_util_pct=pd.to_numeric(embalses["Value"], errors="coerce") * 100)
    a = aportes.assign(fecha=pd.to_datetime(aportes["Date"]).dt.date,
                       aportes_kwh=pd.to_numeric(aportes["Value"], errors="coerce"))
    m.medir("Fecha y valores diarios guardados como texto", "Convertir a fecha y a número",
            len(e) + len(a), 0)
    m.medir("Volumen útil como fracción (0,70)", "Pasarlo a porcentaje (70 %)", len(e), 0)
    df = e[["fecha", "volumen_util_pct"]].merge(a[["fecha", "aportes_kwh"]], on="fecha", how="outer")
    antes = int(df.duplicated("fecha").sum())
    df = df.drop_duplicates("fecha")
    m.medir("Días repetidos", "Dejar uno solo", antes, 0)
    malas = ~df["volumen_util_pct"].between(0, 100) | (df["aportes_kwh"] < 0)
    cuarentena = df[malas].assign(motivo_cuarentena="Volumen fuera de 0-100 % o aportes negativos")
    df = df[~malas]
    m.medir("Volumen útil fuera de 0-100 % o aportes negativos", "Pasar a cuarentena", int(malas.sum()), 0)
    return df.sort_values("fecha").reset_index(drop=True), cuarentena, m.metricas


def limpiar_recursos(listado: pd.DataFrame, codigos_con_generacion: set):
    """Catalogo de plantas (ListadoRecursos) -> una fila por planta."""
    m = Medidor()
    df = listado.rename(columns={"Code": "recurso_id", "Name": "nombre", "Type": "tipo",
                                 "Disp": "despacho", "RecType": "clase", "CompanyCode": "agente",
                                 "EnerSource": "fuente_energia", "OperStartdate": "fecha_operacion",
                                 "State": "estado"})
    # Texto escrito de varias formas: 'Solar' y 'SOLAR', 'Operacion' y 'OPERACION'
    antes = df["tipo"].nunique() + df["estado"].nunique()
    for col in ["tipo", "estado", "fuente_energia", "despacho", "clase"]:
        df[col] = df[col].map(lambda t: sin_tildes(t).upper() if pd.notna(t) else None)
    m.medir("Tipo y estado escritos de varias formas ('Solar' / 'SOLAR')", "Pasar a mayúsculas sin tildes",
            antes, df["tipo"].nunique() + df["estado"].nunique())

    antes = int(df.duplicated("recurso_id").sum())
    df = df.drop_duplicates("recurso_id")
    m.medir("Plantas repetidas en el catálogo", "Dejar una sola", antes, 0)

    df["fecha_operacion"] = pd.to_datetime(df["fecha_operacion"], errors="coerce").dt.date
    m.medir("Fecha de entrada en operación como texto", "Convertir a fecha", len(df), 0)

    # Plantas que generan energia pero no estan en el catalogo: sin ellas, la
    # generacion de esas plantas no se podria unir con la dimension de plantas
    faltan = sorted(codigos_con_generacion - set(df["recurso_id"]))
    if faltan:
        nuevas = pd.DataFrame({"recurso_id": faltan, "nombre": "SIN INFORMACION", "tipo": "DESCONOCIDO",
                               "despacho": None, "clase": None, "agente": None, "fuente_energia": None,
                               "fecha_operacion": None, "estado": "DESCONOCIDO"})
        df = pd.concat([df, nuevas], ignore_index=True)
    m.medir("Plantas que generan pero no están en el catálogo", "Agregarlas con tipo 'DESCONOCIDO'",
            len(faltan), 0)
    columnas = ["recurso_id", "nombre", "tipo", "fuente_energia", "despacho", "clase",
                "agente", "fecha_operacion", "estado"]
    return df[columnas].sort_values("recurso_id").reset_index(drop=True), None, m.metricas


# ---------------------------------------------------------------------------
# PROGRAMA PRINCIPAL
# ---------------------------------------------------------------------------
def main() -> None:
    precio, demanda = leer_bronce("xm_precio_bolsa"), leer_bronce("xm_demanda")
    limpias, cuarentena, metricas = limpiar_mercado(precio, demanda)
    guardar_plata(limpias, "xm_mercado_horario", ESQUEMA_XM_MERCADO, "XM", metricas,
                  len(precio) + len(demanda), cuarentena)

    gene = leer_bronce("xm_generacion_recurso")
    limpias, cuarentena, metricas = limpiar_generacion(gene)
    codigos = set(limpias["recurso_id"])
    guardar_plata(limpias, "xm_generacion_recurso", ESQUEMA_XM_GENERACION, "XM", metricas, len(gene), cuarentena)

    embalses, aportes = leer_bronce("xm_embalses"), leer_bronce("xm_aportes_hidricos")
    limpias, cuarentena, metricas = limpiar_hidrologia(embalses, aportes)
    guardar_plata(limpias, "xm_hidrologia_diaria", ESQUEMA_XM_HIDROLOGIA, "XM", metricas,
                  len(embalses) + len(aportes), cuarentena)

    listado = leer_bronce("xm_listado_recursos")
    limpias, cuarentena, metricas = limpiar_recursos(listado, codigos)
    guardar_plata(limpias, "xm_recursos", ESQUEMA_XM_RECURSOS, "XM", metricas, len(listado), cuarentena)


if __name__ == "__main__":
    main()
