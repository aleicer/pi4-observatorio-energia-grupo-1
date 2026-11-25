"""
Calculos (KPIs) del dashboard del Observatorio Energia y Clima.

Aqui solo hay funciones de pandas, sin nada de Streamlit: reciben una tabla de la capa
oro y devuelven numeros o tablas listas para graficar. Asi se pueden probar con pytest
y datos de ejemplo (tests/test_kpis.py), y app.py queda solo para dibujar.
"""
import pandas as pd

# Las fases de El Nino en el orden en que se muestran en las graficas y los filtros
FASES_ENSO = ["El Niño", "Neutral", "La Niña", "Sin dato"]


# ---------------------------------------------------------------------------
# FILTROS
# ---------------------------------------------------------------------------
def filtrar(df: pd.DataFrame, desde: str, hasta: str, fases: list[str] | None = None) -> pd.DataFrame:
    """Deja los meses entre desde y hasta ('AAAA-MM', incluidos) y, si se dan, solo esas fases ENSO."""
    filas = df["periodo"].between(desde, hasta)
    if fases:
        filas &= df["fase_enso"].isin(fases)
    return df[filas]


# ---------------------------------------------------------------------------
# PREGUNTA 1: RIESGO HIDRICO
# ---------------------------------------------------------------------------
def episodios_nino(mensual: pd.DataFrame, meses_minimos: int = 5) -> pd.DataFrame:
    """Los episodios de El Nino: rachas de al menos 5 meses seguidos en fase El Nino.

    Es la regla de la NOAA (ONI >= 0,5 durante 5 trimestres seguidos), aplicada a la fase
    de cada mes. Devuelve una fila por episodio con su primer y su ultimo mes, y el mes con
    los embalses mas bajos dentro del episodio.
    """
    serie = mensual.sort_values("periodo").reset_index(drop=True)
    es_nino = serie["fase_enso"].eq("El Niño")
    # Cada vez que cambia la fase empieza un bloque nuevo: cumsum le pone un numero a cada bloque
    bloque = es_nino.ne(es_nino.shift()).cumsum()
    filas = []
    for _, tramo in serie[es_nino].groupby(bloque[es_nino]):
        if len(tramo) < meses_minimos:
            continue
        inicio, fin = tramo["periodo"].iloc[0], tramo["periodo"].iloc[-1]
        con_dato = tramo.dropna(subset=["volumen_util_min_pct"])
        peor = con_dato.loc[con_dato["volumen_util_min_pct"].idxmin()] if not con_dato.empty else None
        filas.append({
            "episodio": f"El Niño {inicio[:4]}-{fin[:4]}" if inicio[:4] != fin[:4] else f"El Niño {inicio[:4]}",
            "desde": inicio, "hasta": fin, "meses": len(tramo),
            "periodo_minimo": None if peor is None else peor["periodo"],
            "volumen_util_min_pct": None if peor is None else float(peor["volumen_util_min_pct"]),
        })
    return pd.DataFrame(filas, columns=["episodio", "desde", "hasta", "meses",
                                        "periodo_minimo", "volumen_util_min_pct"])


# ---------------------------------------------------------------------------
# PREGUNTA 2: CLIMA -> PRECIO
# ---------------------------------------------------------------------------
def correlacion_rezago(mensual: pd.DataFrame, x: str = "oni", y: str = "precio_bolsa_cop_kwh",
                       max_rezago: int = 12) -> pd.DataFrame:
    """Correlacion entre x de hace k meses y y de este mes, para k = 0 ... max_rezago.

    Un rezago de 4 con correlacion alta quiere decir: lo que marca el ONI hoy se nota en
    el precio unos 4 meses despues. Los meses deben estar completos y en orden.
    """
    serie = mensual.sort_values("periodo")
    filas = []
    for k in range(max_rezago + 1):
        # shift(k) corre x k meses hacia abajo: en cada mes queda el valor de hace k meses
        filas.append({"rezago_meses": k, "correlacion": serie[x].shift(k).corr(serie[y])})
    return pd.DataFrame(filas)


def mejor_rezago(rezagos: pd.DataFrame) -> pd.Series:
    """La fila con la correlacion mas alta (el rezago al que mas se nota el efecto)."""
    return rezagos.loc[rezagos["correlacion"].idxmax()]


# ---------------------------------------------------------------------------
# PREGUNTA 3: MATRIZ DE GENERACION
# ---------------------------------------------------------------------------
def participacion(generacion: pd.DataFrame, por: str = "periodo") -> pd.DataFrame:
    """Participacion (%) de cada tipo de planta dentro de cada grupo (por mes, por temporada...)."""
    tabla = generacion.groupby([por, "tipo"], as_index=False)["generacion_gwh"].sum()
    tabla["participacion_pct"] = 100 * tabla["generacion_gwh"] / tabla.groupby(por)["generacion_gwh"].transform("sum")
    return tabla


# ---------------------------------------------------------------------------
# PREGUNTA 4: DEMANDA
# ---------------------------------------------------------------------------
def demanda_hora_dia(mercado: pd.DataFrame) -> pd.DataFrame:
    """Demanda promedio (MWh) de cada hora en cada dia de la semana: la tabla del mapa de calor."""
    return mercado.pivot_table(index="hora", columns="dia_semana", values="demanda_mwh", aggfunc="mean")


def hora_pico(mercado: pd.DataFrame) -> int:
    """La hora del dia con la demanda promedio mas alta."""
    return int(mercado.groupby("hora")["demanda_mwh"].mean().idxmax())


# ---------------------------------------------------------------------------
# PREGUNTA 5: IMPACTO EN EL NEGOCIO
# ---------------------------------------------------------------------------
def costo_por_mes(ventas: pd.DataFrame) -> pd.DataFrame:
    """Por mes: lo que costo comprar la energia y lo que habria costado todo en bolsa o todo por contrato.

    sobrecosto_bolsa_cop = todo en bolsa - todo por contrato: positivo si la bolsa salio mas cara.
    """
    tabla = ventas.groupby("periodo", as_index=False)[
        ["energia_kwh", "costo_compra_cop", "costo_si_bolsa_cop", "costo_si_contrato_cop"]].sum()
    tabla["sobrecosto_bolsa_cop"] = tabla["costo_si_bolsa_cop"] - tabla["costo_si_contrato_cop"]
    return tabla


def exposicion_bolsa(ventas: pd.DataFrame, por: str = "municipio") -> pd.DataFrame:
    """Cuanta energia de cada municipio (o segmento) se compra en bolsa y que parte del total es.

    Es la energia expuesta al precio de bolsa: la que se encarece cuando llega El Nino.
    """
    total = ventas.groupby(por)["energia_kwh"].sum()
    bolsa = ventas[ventas["tipo_compra"] == "Bolsa"].groupby(por)["energia_kwh"].sum()
    tabla = pd.DataFrame({"energia_gwh": total / 1e6,
                          "energia_bolsa_gwh": bolsa.reindex(total.index, fill_value=0) / 1e6})
    tabla["participacion_bolsa_pct"] = 100 * tabla["energia_bolsa_gwh"] / tabla["energia_gwh"]
    return tabla.reset_index().sort_values("energia_bolsa_gwh", ascending=False)


# ---------------------------------------------------------------------------
# PREGUNTA PROPIA: LA SOLAR EN EL NINO
# ---------------------------------------------------------------------------
def solar_vs_hidraulica(generacion: pd.DataFrame, mensual: pd.DataFrame) -> pd.DataFrame:
    """Por mes: generacion solar e hidraulica (GWh), radiacion de La Guajira y fase ENSO."""
    gen = (generacion[generacion["tipo"].isin(["SOLAR", "HIDRAULICA"])]
           .pivot_table(index="periodo", columns="tipo", values="generacion_gwh", aggfunc="sum")
           .rename(columns={"SOLAR": "solar_gwh", "HIDRAULICA": "hidraulica_gwh"})
           .reset_index())
    clima = mensual[["periodo", "fase_enso", "radiacion_guajira_kwh_m2"]]
    return gen.merge(clima, on="periodo", how="left")


def promedio_por_fase(tabla: pd.DataFrame, columnas: list[str]) -> pd.DataFrame:
    """Promedio de las columnas en cada fase ENSO (en el orden de FASES_ENSO)."""
    resumen = tabla.groupby("fase_enso")[columnas].mean()
    return resumen.reindex([f for f in FASES_ENSO if f in resumen.index]).reset_index()
