
"""
Capa PLATA: datos de XM (mercado electrico).

En bronce, los datos horarios vienen en formato ANCHO: una fila por dia
con 24 columnas (Hour01 ... Hour24). Aqui se pasan a una fila por
FECHA y HORA, con los valores como numeros.

Tablas que guarda en data/silver/:
  - xm_mercado_horario: precio de bolsa y demanda, por fecha y hora
  - xm_generacion_recurso: generacion de cada planta, por fecha y hora
  - xm_hidrologia_diaria: volumen util y aportes hidricos, por dia
  - xm_precio_contratos: precio promedio diario de contratos (EA3)
  - xm_recursos: catalogo de plantas

Uso:
    python -m src.silver.xm
"""

import pandas as pd

from src import config
from src.quality.esquemas_xm import (
    ESQUEMA_XM_CONTRATOS,
    ESQUEMA_XM_GENERACION,
    ESQUEMA_XM_HIDROLOGIA,
    ESQUEMA_XM_MERCADO,
    ESQUEMA_XM_RECURSOS,
)
from src.silver.comun import LINAJE, Medidor, guardar_plata
from src.silver.enerandes import sin_tildes
from src.utils import log


# ------------------------------------------------------------
# LECTURA DE DATOS BRONCE
# ------------------------------------------------------------

def leer_bronce(nombre: str) -> pd.DataFrame:
    """Lee un archivo de bronce y elimina las columnas de linaje."""
    return pd.read_parquet(
        config.DIR_BRONZE / f"{nombre}.parquet"
    ).drop(columns=LINAJE, errors="ignore")


# ------------------------------------------------------------
# CONVERSION DE DATOS HORARIOS
# ------------------------------------------------------------

def a_formato_largo(
    ancho: pd.DataFrame,
    columna_valor: str,
) -> pd.DataFrame:
    """
    Convierte 24 columnas horarias en una fila por fecha y hora.

    Hour01 corresponde a la hora 0.
    Hour24 corresponde a la hora 23.
    """
    horas = [c for c in ancho.columns if c.startswith("Hour")]
    otras = [c for c in ancho.columns if c not in horas and c != "Id"]

    largo = ancho.drop(
        columns=["Id"], errors="ignore"
    ).melt(
        id_vars=otras,
        value_vars=horas,
        var_name="columna_hora",
        value_name=columna_valor,
    )

    largo["hora"] = (
        largo["columna_hora"].str[4:].astype(int) - 1
    )

    largo["fecha"] = pd.to_datetime(
        largo["Date"]
    ).dt.date

    largo[columna_valor] = pd.to_numeric(
        largo[columna_valor], errors="coerce"
    )

    resto = [c for c in otras if c != "Date"]

    return (
        largo[["fecha", "hora", *resto, columna_valor]]
        .sort_values(["fecha", *resto, "hora"])
        .reset_index(drop=True)
    )


# ------------------------------------------------------------
# LIMPIEZA DEL MERCADO HORARIO
# ------------------------------------------------------------

def limpiar_mercado(
    precio: pd.DataFrame,
    demanda: pd.DataFrame,
):
    """Limpia precio de bolsa y demanda por fecha y hora."""
    m = Medidor()

    p = a_formato_largo(
        precio, "precio_bolsa_cop_kwh"
    ).drop(columns=["code"], errors="ignore")

    d = a_formato_largo(
        demanda, "demanda_kwh"
    ).drop(columns=["code"], errors="ignore")

    m.medir(
        "Filas en formato ancho: 24 columnas por hora (precio y demanda)",
        "Pasar a una fila por fecha y hora",
        len(precio) + len(demanda),
        0,
    )

    m.medir(
        "Valores horarios guardados como texto",
        "Convertirlos a numero",
        len(p) + len(d),
        0,
    )

    df = p.merge(
        d,
        on=["fecha", "hora"],
        how="outer",
    )

    m.medir(
        "Horas con precio o demanda faltante",
        "Dejar vacio (no se inventa)",
        int(
            df[
                ["precio_bolsa_cop_kwh", "demanda_kwh"]
            ].isna().any(axis=1).sum()
        ),
        0,
    )

    antes = int(
        df.duplicated(["fecha", "hora"]).sum()
    )

    df = df.drop_duplicates(["fecha", "hora"])

    m.medir(
        "Horas repetidas",
        "Dejar una sola",
        antes,
        0,
    )

    malas = (
        (df["precio_bolsa_cop_kwh"] <= 0)
        | (df["demanda_kwh"] <= 0)
    )

    cuarentena = df[malas].assign(
        motivo_cuarentena="Precio o demanda cero o negativos"
    )

    df = df[~malas]

    m.medir(
        "Precio o demanda cero o negativos",
        "Pasar a cuarentena",
        int(malas.sum()),
        0,
    )

    dias_incompletos = int(
        (df.groupby("fecha").size() != 24).sum()
    )

    m.medir(
        "Dias sin sus 24 horas",
        "Verificar que cada dia tenga 24 horas",
        dias_incompletos,
        dias_incompletos,
    )

    return (
        df.reset_index(drop=True),
        cuarentena,
        m.metricas,
    )


# ------------------------------------------------------------
# LIMPIEZA DE GENERACION POR RECURSO
# ------------------------------------------------------------

def limpiar_generacion(gene: pd.DataFrame):
    """Limpia la generacion por planta, fecha y hora."""
    m = Medidor()

    df = a_formato_largo(
        gene, "generacion_kwh"
    ).rename(columns={"code": "recurso_id"})

    m.medir(
        "Filas en formato ancho: 24 columnas por hora (generacion)",
        "Pasar a una fila por fecha, hora y planta",
        len(gene),
        0,
    )

    vacias = df["generacion_kwh"].isna()

    m.medir(
        "Horas sin generacion reportada",
        "No guardarlas: no son una medicion",
        int(vacias.sum()),
        0,
    )

    df = df[~vacias]

    antes = int(
        df.duplicated(
            ["fecha", "hora", "recurso_id"]
        ).sum()
    )

    df = df.drop_duplicates(
        ["fecha", "hora", "recurso_id"]
    )

    m.medir(
        "Generacion repetida (misma planta, fecha y hora)",
        "Dejar una sola",
        antes,
        0,
    )

    negativa = df["generacion_kwh"] < 0

    cuarentena = df[negativa].assign(
        motivo_cuarentena="Generacion negativa"
    )

    df = df[~negativa]

    m.medir(
        "Generacion negativa",
        "Pasar a cuarentena",
        int(negativa.sum()),
        0,
    )

    return (
        df.reset_index(drop=True),
        cuarentena,
        m.metricas,
    )


# ------------------------------------------------------------
# LIMPIEZA DE HIDROLOGIA
# ------------------------------------------------------------

def limpiar_hidrologia(
    embalses: pd.DataFrame,
    aportes: pd.DataFrame,
):
    """Limpia volumen util de embalses y aportes hidricos."""
    m = Medidor()

    e = embalses.assign(
        fecha=pd.to_datetime(
            embalses["Date"]
        ).dt.date,
        volumen_util_pct=pd.to_numeric(
            embalses["Value"], errors="coerce"
        ) * 100,
    )

    a = aportes.assign(
        fecha=pd.to_datetime(
            aportes["Date"]
        ).dt.date,
        aportes_kwh=pd.to_numeric(
            aportes["Value"], errors="coerce"
        ),
    )

    m.medir(
        "Fecha y valores diarios guardados como texto",
        "Convertir a fecha y numero",
        len(e) + len(a),
        0,
    )

    m.medir(
        "Volumen util como fraccion (0,70)",
        "Pasarlo a porcentaje (70 %)",
        len(e),
        0,
    )

    df = e[
        ["fecha", "volumen_util_pct"]
    ].merge(
        a[["fecha", "aportes_kwh"]],
        on="fecha",
        how="outer",
    )

    antes = int(df.duplicated("fecha").sum())
    df = df.drop_duplicates("fecha")

    m.medir(
        "Dias repetidos",
        "Dejar uno solo",
        antes,
        0,
    )

    malas = (
        ~df["volumen_util_pct"].between(0, 100)
        | (df["aportes_kwh"] < 0)
    )

    cuarentena = df[malas].assign(
        motivo_cuarentena="Volumen fuera de 0-100 % o aportes negativos"
    )

    df = df[~malas]

    m.medir(
        "Volumen util fuera de 0-100 % o aportes negativos",
        "Pasar a cuarentena",
        int(malas.sum()),
        0,
    )

    return (
        df.sort_values("fecha").reset_index(drop=True),
        cuarentena,
        m.metricas,
    )


# ------------------------------------------------------------
# EA3: LIMPIEZA DEL PRECIO PROMEDIO DE CONTRATOS
# ------------------------------------------------------------

def limpiar_contratos(contratos: pd.DataFrame):
    """Limpia el precio promedio diario de contratos de XM."""
    m = Medidor()

    df = pd.DataFrame({
        "fecha": pd.to_datetime(
            contratos["Date"], errors="coerce"
        ).dt.date,
        "precio_contrato_cop_kwh": pd.to_numeric(
            contratos["Value"], errors="coerce"
        ),
    })

    m.medir(
        "Fecha y precio de contratos guardados como texto",
        "Convertir a fecha y a numero",
        len(df),
        0,
    )

    antes = int(df.duplicated("fecha").sum())

    df = df.drop_duplicates("fecha")

    m.medir(
        "Dias repetidos (precio de contratos)",
        "Dejar uno solo",
        antes,
        0,
    )

    malas = (
        df["fecha"].isna()
        | df["precio_contrato_cop_kwh"].isna()
        | (df["precio_contrato_cop_kwh"] <= 0)
        | (df["precio_contrato_cop_kwh"] > 2000)
    )

    cuarentena = df[malas].copy()

    cuarentena["motivo_cuarentena"] = (
        "Fecha invalida o precio de contratos fuera del rango permitido"
    )

    df = df[~malas].copy()

    m.medir(
        "Fecha invalida o precio fuera del rango permitido",
        "Pasar a cuarentena",
        int(malas.sum()),
        0,
    )

    return (
        df.sort_values("fecha").reset_index(drop=True),
        cuarentena,
        m.metricas,
    )


# ------------------------------------------------------------
# LIMPIEZA DEL CATALOGO DE RECURSOS
# ------------------------------------------------------------

def limpiar_recursos(
    listado: pd.DataFrame,
    codigos_con_generacion: set,
):
    """Limpia el catalogo de plantas de generacion."""
    m = Medidor()

    df = listado.rename(
        columns={
            "Code": "recurso_id",
            "Name": "nombre",
            "Type": "tipo",
            "Disp": "despacho",
            "RecType": "clase",
            "CompanyCode": "agente",
            "EnerSource": "fuente_energia",
            "OperStartdate": "fecha_operacion",
            "State": "estado",
        }
    )

    antes = (
        df["tipo"].nunique()
        + df["estado"].nunique()
    )

    for col in [
        "tipo",
        "estado",
        "fuente_energia",
        "despacho",
        "clase",
    ]:
        df[col] = df[col].map(
            lambda t: sin_tildes(t).upper()
            if pd.notna(t)
            else None
        )

    m.medir(
        "Tipo y estado escritos de varias formas",
        "Pasar a mayusculas sin tildes",
        antes,
        df["tipo"].nunique() + df["estado"].nunique(),
    )

    antes = int(df.duplicated("recurso_id").sum())

    df = df.drop_duplicates("recurso_id")

    m.medir(
        "Plantas repetidas en el catalogo",
        "Dejar una sola",
        antes,
        0,
    )

    df["fecha_operacion"] = pd.to_datetime(
        df["fecha_operacion"], errors="coerce"
    ).dt.date

    m.medir(
        "Fecha de entrada en operacion como texto",
        "Convertir a fecha",
        len(df),
        0,
    )

    faltan = sorted(
        codigos_con_generacion - set(df["recurso_id"])
    )

    if faltan:
        nuevas = pd.DataFrame({
            "recurso_id": faltan,
            "nombre": "SIN INFORMACION",
            "tipo": "DESCONOCIDO",
            "despacho": None,
            "clase": None,
            "agente": None,
            "fuente_energia": None,
            "fecha_operacion": None,
            "estado": "DESCONOCIDO",
        })

        df = pd.concat(
            [df, nuevas], ignore_index=True
        )

    m.medir(
        "Plantas que generan pero no estan en el catalogo",
        "Agregarlas con tipo DESCONOCIDO",
        len(faltan),
        0,
    )

    columnas = [
        "recurso_id",
        "nombre",
        "tipo",
        "fuente_energia",
        "despacho",
        "clase",
        "agente",
        "fecha_operacion",
        "estado",
    ]

    return (
        df[columnas]
        .sort_values("recurso_id")
        .reset_index(drop=True),
        None,
        m.metricas,
    )


# ------------------------------------------------------------
# PROGRAMA PRINCIPAL
# ------------------------------------------------------------

def main() -> None:
    log("XM - limpieza y validacion de la capa plata")

    # Mercado horario
    precio = leer_bronce("xm_precio_bolsa")
    demanda = leer_bronce("xm_demanda")

    limpias, cuarentena, metricas = limpiar_mercado(
        precio, demanda
    )

    guardar_plata(
        limpias,
        "xm_mercado_horario",
        ESQUEMA_XM_MERCADO,
        "XM",
        metricas,
        len(precio) + len(demanda),
        cuarentena,
    )

    # Generacion por recurso
    gene = leer_bronce("xm_generacion_recurso")

    limpias, cuarentena, metricas = limpiar_generacion(gene)

    codigos = set(limpias["recurso_id"])

    guardar_plata(
        limpias,
        "xm_generacion_recurso",
        ESQUEMA_XM_GENERACION,
        "XM",
        metricas,
        len(gene),
        cuarentena,
    )

    # Hidrologia
    embalses = leer_bronce("xm_embalses")
    aportes = leer_bronce("xm_aportes_hidricos")

    limpias, cuarentena, metricas = limpiar_hidrologia(
        embalses, aportes
    )

    guardar_plata(
        limpias,
        "xm_hidrologia_diaria",
        ESQUEMA_XM_HIDROLOGIA,
        "XM",
        metricas,
        len(embalses) + len(aportes),
        cuarentena,
    )

    # EA3: precio promedio de contratos
    contratos = leer_bronce("xm_precio_contratos")

    limpias, cuarentena, metricas = limpiar_contratos(
        contratos
    )

    guardar_plata(
        limpias,
        "xm_precio_contratos",
        ESQUEMA_XM_CONTRATOS,
        "XM",
        metricas,
        len(contratos),
        cuarentena,
    )

    # Catalogo de plantas
    listado = leer_bronce("xm_listado_recursos")

    limpias, cuarentena, metricas = limpiar_recursos(
        listado, codigos
    )

    guardar_plata(
        limpias,
        "xm_recursos",
        ESQUEMA_XM_RECURSOS,
        "XM",
        metricas,
        len(listado),
        cuarentena,
    )

    log("XM - capa plata completada")


if __name__ == "__main__":
    main()
