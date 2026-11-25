"""
Dashboard del Observatorio Energia y Clima (Streamlit).

Responde las 6 preguntas de negocio del reto con las tablas de la capa oro que crea dbt
(dbt/models/dashboard/). Lee los Parquet de data/gold/ (los deja python -m src.exportar_oro
o el artefacto capa-oro de GitHub Actions); si no existen, usa la copia de dashboard/datos/,
que es la que lee la version publicada en Streamlit Community Cloud.

Uso, desde la raiz del proyecto:
    streamlit run dashboard/app.py
"""
from pathlib import Path

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
from plotly.subplots import make_subplots

import kpis   # los calculos, en dashboard/kpis.py (Streamlit agrega esta carpeta al path)

# ---------------------------------------------------------------------------
# CONFIGURACION
# ---------------------------------------------------------------------------
RAIZ = Path(__file__).resolve().parents[1]
CARPETAS_DATOS = [RAIZ / "data" / "gold", RAIZ / "dashboard" / "datos"]

# Colores: cada cosa tiene siempre el mismo color en todas las graficas
AZUL, NARANJA, AQUA, AMARILLO, MAGENTA, ROJO = "#2a78d6", "#eb6834", "#1baf7a", "#eda100", "#e87ba4", "#e34948"
GRIS = "#898781"
COLOR_FASE = {"El Niño": ROJO, "La Niña": AZUL, "Neutral": GRIS, "Sin dato": "#c3c2b7"}
COLOR_TIPO = {"HIDRAULICA": AZUL, "TERMICA": NARANJA, "SOLAR": AQUA, "EOLICA": AMARILLO, "OTRAS": MAGENTA}
NOMBRE_TIPO = {"HIDRAULICA": "Hidráulica", "TERMICA": "Térmica", "SOLAR": "Solar", "EOLICA": "Eólica",
               "OTRAS": "Otras"}
DIAS = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]

st.set_page_config(page_title="Observatorio Energía y Clima", page_icon="⚡", layout="wide")


def estilo(fig: go.Figure, alto: int = 360) -> go.Figure:
    """Mismo estilo para todas las graficas: fondo claro, rejilla suave y lineas delgadas."""
    fig.update_layout(template="plotly_white", height=alto, margin=dict(l=10, r=10, t=80, b=10),
                      title=dict(y=0.98, yref="container", yanchor="top", font=dict(size=15)),
                      paper_bgcolor="#fcfcfb", plot_bgcolor="#fcfcfb", font=dict(color="#0b0b0b", size=13),
                      legend=dict(orientation="h", yanchor="bottom", y=1.02, x=0, title_text=""),
                      hoverlabel=dict(bgcolor="white"))
    fig.update_xaxes(showgrid=False, linecolor="#c3c2b7", tickfont=dict(color="#52514e"))
    fig.update_yaxes(gridcolor="#e1e0d9", zeroline=False, tickfont=dict(color="#52514e"))
    fig.update_traces(selector=dict(type="scatter"), line_width=2)
    return fig


def num(valor: float, decimales: int = 0) -> str:
    """Numero con punto de miles y coma decimal, como se escribe en Colombia."""
    return f"{valor:,.{decimales}f}".replace(",", "X").replace(".", ",").replace("X", ".")


def miles_de_millones(cop: float) -> str:
    """Pesos a miles de millones: 1.234.000.000 -> '$1,2'."""
    return "$" + num(cop / 1e9, 1)


# ---------------------------------------------------------------------------
# DATOS
# ---------------------------------------------------------------------------
@st.cache_data
def leer(tabla: str) -> pd.DataFrame:
    """Lee una tabla de la capa oro: primero data/gold/, si no esta, dashboard/datos/."""
    for carpeta in CARPETAS_DATOS:
        archivo = carpeta / f"{tabla}.parquet"
        if archivo.exists():
            return pd.read_parquet(archivo)
    st.error(f"No encontré {tabla}.parquet. Ejecuta el pipeline y `python -m src.exportar_oro`.")
    st.stop()


mensual = leer("mart_hidroclima_mensual")
generacion = leer("mart_generacion_tipo_diaria")
mercado = leer("mart_mercado_horario")
ventas = leer("mart_ventas_costo_mensual")

# COGENERADOR y DESCONOCIDO pesan menos del 1 %: se juntan en "OTRAS"
generacion["tipo"] = generacion["tipo"].where(generacion["tipo"].isin(COLOR_TIPO), "OTRAS")

# ---------------------------------------------------------------------------
# FILTROS (barra lateral)
# ---------------------------------------------------------------------------
periodos = mensual["periodo"].tolist()
st.sidebar.title("Filtros")
desde, hasta = st.sidebar.select_slider("Rango de meses", options=periodos,
                                        value=(periodos[0], periodos[-1]))
fases = st.sidebar.multiselect("Fase ENSO (El Niño / La Niña)", kpis.FASES_ENSO, default=kpis.FASES_ENSO,
                               help="Deja solo los meses de esas fases. Aplica a todas las pestañas.")
st.sidebar.markdown("**Ventas de EnerAndes** (pestaña 5)")
municipios = st.sidebar.multiselect("Municipio", sorted(ventas["municipio"].unique()), placeholder="Todos")
segmentos = st.sidebar.multiselect("Segmento", sorted(ventas["segmento"].unique()), placeholder="Todos")
compras = st.sidebar.multiselect("Tipo de compra", ["Contrato", "Bolsa"], placeholder="Todos")

m = kpis.filtrar(mensual, desde, hasta, fases)
g = kpis.filtrar(generacion, desde, hasta, fases)
h = kpis.filtrar(mercado, desde, hasta, fases)
v = kpis.filtrar(ventas, desde, hasta, fases)
if municipios:
    v = v[v["municipio"].isin(municipios)]
if segmentos:
    v = v[v["segmento"].isin(segmentos)]
if compras:
    v = v[v["tipo_compra"].isin(compras)]

# ---------------------------------------------------------------------------
# ENCABEZADO Y KPIs
# ---------------------------------------------------------------------------
st.title("⚡ Observatorio Energía y Clima")
st.caption("EnerAndes · Grupo 1 · Datos de XM, IDEAM, NOAA, NASA POWER y ventas de EnerAndes · "
           "capa oro construida con dbt y actualizada todos los días con GitHub Actions")

ultimo = mensual.dropna(subset=["volumen_util_pct"]).iloc[-1]
ultimo_oni = mensual.dropna(subset=["oni"]).iloc[-1]
c1, c2, c3, c4 = st.columns(4)
c1.metric(f"Embalses ({ultimo['periodo']})", f"{num(ultimo['volumen_util_pct'], 1)} %",
          help="Volumen útil promedio de los embalses del país en el último mes con datos (XM).")
c2.metric(f"Precio de bolsa ({ultimo['periodo']})", f"${num(ultimo['precio_bolsa_cop_kwh'])}/kWh",
          f"{num(ultimo['precio_bolsa_cop_kwh'] - ultimo['precio_contrato_cop_kwh'])} frente al contrato",
          delta_color="inverse", help="Precio de bolsa del mes ponderado por la demanda, y diferencia con el "
                                      "precio promedio de los contratos (XM).")
c3.metric(f"ONI ({ultimo_oni['periodo']})", num(ultimo_oni["oni"], 2), ultimo_oni["fase_enso"],
          delta_color="off", help="Índice Oceánico El Niño de la NOAA. 0,5 o más = El Niño.")
pct_bolsa = 100 * v.loc[v["tipo_compra"] == "Bolsa", "energia_kwh"].sum() / max(v["energia_kwh"].sum(), 1)
c4.metric("Compra en bolsa (EnerAndes)", f"{num(pct_bolsa, 1)} %",
          help="Parte de la energía vendida que se compró en bolsa, con los filtros elegidos.")

tabs = st.tabs(["1 · Riesgo hídrico", "2 · Clima y precio", "3 · Matriz de generación",
                "4 · Demanda", "5 · Impacto en el negocio", "6 · La solar en El Niño"])

# ---------------------------------------------------------------------------
# 1. RIESGO HIDRICO
# ---------------------------------------------------------------------------
with tabs[0]:
    st.subheader("¿Cómo han evolucionado los embalses y en qué se parece hoy a El Niño 2015-2016 y 2023-2024?")
    episodios = kpis.episodios_nino(mensual)
    fig = go.Figure()
    for _, e in episodios.iterrows():          # sombra en cada episodio de El Nino
        fig.add_vrect(x0=e["desde"], x1=e["hasta"], fillcolor=ROJO, opacity=0.08, line_width=0)
    fig.add_scatter(x=m["periodo"], y=m["volumen_util_pct"], name="Promedio del mes", mode="lines",
                    line_color=AZUL, hovertemplate="%{x}: %{y:.1f} %<extra>Promedio</extra>")
    fig.add_scatter(x=m["periodo"], y=m["volumen_util_min_pct"], name="Día más bajo del mes", mode="lines",
                    line=dict(color=AZUL, dash="dot"), hovertemplate="%{x}: %{y:.1f} %<extra>Mínimo</extra>")
    fig.update_yaxes(title="Volumen útil de los embalses (%)", range=[0, 100])
    fig.update_xaxes(type="category", nticks=12)
    st.plotly_chart(estilo(fig, 400), width="stretch")
    st.caption("Las franjas rojas son los episodios de El Niño (5 meses seguidos o más con ONI ≥ 0,5).")

    col_a, col_b = st.columns([3, 2])
    actual = mensual.dropna(subset=["volumen_util_min_pct"]).tail(12)
    peor_actual = actual.loc[actual["volumen_util_min_pct"].idxmin()]
    tabla = pd.concat([episodios, pd.DataFrame([{
        "episodio": "Últimos 12 meses", "desde": actual["periodo"].iloc[0], "hasta": actual["periodo"].iloc[-1],
        "meses": 12, "periodo_minimo": peor_actual["periodo"],
        "volumen_util_min_pct": peor_actual["volumen_util_min_pct"]}])], ignore_index=True)
    tabla["volumen_util_min_pct"] = tabla["volumen_util_min_pct"].astype(float)
    col_a.dataframe(tabla.rename(columns={"episodio": "Episodio", "desde": "Desde", "hasta": "Hasta",
                                          "meses": "Meses", "periodo_minimo": "Mes más crítico",
                                          "volumen_util_min_pct": "Embalses mínimo (%)"}).round(1),
                    hide_index=True, width="stretch")
    with col_b:
        st.markdown("**Lo que dicen los datos**")
        st.markdown(
            f"- Hoy ({ultimo['periodo']}) los embalses están en **{num(ultimo['volumen_util_pct'], 1)} %** "
            f"con un ONI de {num(ultimo_oni['oni'], 2)} en {ultimo_oni['periodo']} "
            f"(**{ultimo_oni['fase_enso']}**).\n"
            + "\n".join(f"- En **{r.episodio}** bajaron hasta **{num(r.volumen_util_min_pct, 1)} %** "
                        f"({r.periodo_minimo})." for r in episodios.itertuples() if pd.notna(r.volumen_util_min_pct)))

# ---------------------------------------------------------------------------
# 2. CLIMA -> PRECIO
# ---------------------------------------------------------------------------
with tabs[1]:
    st.subheader("¿Qué relación hay entre El Niño, la lluvia y el precio de bolsa? ¿Con cuánto rezago?")
    fig = make_subplots(rows=3, cols=1, shared_xaxes=True, vertical_spacing=0.06,
                        subplot_titles=("ONI (NOAA): sobre 0,5 es El Niño",
                                        "Aportes de los ríos a los embalses (GWh/mes, XM)",
                                        "Precio de bolsa ponderado (COP/kWh, XM)"))
    fig.add_bar(x=m["periodo"], y=m["oni"], marker_color=[COLOR_FASE.get(f, GRIS) for f in m["fase_enso"]],
                name="ONI", showlegend=False, hovertemplate="%{x}: ONI %{y:.2f}<extra></extra>", row=1, col=1)
    fig.add_scatter(x=m["periodo"], y=m["aportes_gwh"], line_color=AZUL, showlegend=False,
                    hovertemplate="%{x}: %{y:,.0f} GWh<extra></extra>", row=2, col=1)
    fig.add_scatter(x=m["periodo"], y=m["precio_bolsa_cop_kwh"], line_color=NARANJA, showlegend=False,
                    hovertemplate="%{x}: $%{y:,.0f}/kWh<extra></extra>", row=3, col=1)
    fig.update_xaxes(type="category", nticks=12)
    st.plotly_chart(estilo(fig, 560).update_layout(margin=dict(t=40)), width="stretch")

    # El rezago se calcula sobre los meses seguidos del rango (sin el filtro de fase, que dejaria huecos)
    continuo = kpis.filtrar(mensual, desde, hasta).dropna(subset=["oni", "precio_bolsa_cop_kwh"])
    col_a, col_b = st.columns([3, 2])
    if len(continuo) >= 24:
        rezagos = kpis.correlacion_rezago(continuo, max_rezago=12)
        rezagos_aportes = kpis.correlacion_rezago(continuo, x="aportes_gwh", max_rezago=12)
        mejor = kpis.mejor_rezago(rezagos)
        fig = go.Figure(go.Bar(x=rezagos["rezago_meses"], y=rezagos["correlacion"],
                               marker_color=[NARANJA if k == mejor["rezago_meses"] else "#c3c2b7"
                                             for k in rezagos["rezago_meses"]],
                               hovertemplate="ONI de hace %{x} meses: r = %{y:.2f}<extra></extra>"))
        fig.update_layout(title="Correlación del ONI de hace k meses con el precio de este mes")
        fig.update_xaxes(title="Rezago (meses)", dtick=1)
        fig.update_yaxes(title="Correlación (r)", range=[-1, 1])
        col_a.plotly_chart(estilo(fig, 330), width="stretch")
        peor_aporte = rezagos_aportes.loc[rezagos_aportes["correlacion"].idxmin()]
        with col_b:
            st.markdown("**Lo que dicen los datos**")
            st.markdown(
                f"- El ONI se nota más en el precio **{int(mejor['rezago_meses'])} meses después** "
                f"(r = {num(mejor['correlacion'], 2)}).\n"
                f"- Los aportes de los ríos van en contra del precio: con un rezago de "
                f"{int(peor_aporte['rezago_meses'])} meses, r = {num(peor_aporte['correlacion'], 2)} "
                f"(menos agua, precio más alto).\n"
                f"- Precio promedio por fase: " + ", ".join(
                    f"{r.fase_enso} **${num(r.precio_bolsa_cop_kwh)}/kWh**"
                    for r in kpis.promedio_por_fase(continuo, ["precio_bolsa_cop_kwh"]).itertuples()) + ".")
            st.caption(f"Calculado con {len(continuo)} meses seguidos del rango elegido. Correlación no es "
                       "causa: el precio también depende de la demanda, los combustibles y la regulación.")
    else:
        col_a.info("Elige un rango de al menos 24 meses para calcular el rezago.")

# ---------------------------------------------------------------------------
# 3. MATRIZ DE GENERACION
# ---------------------------------------------------------------------------
with tabs[2]:
    st.subheader("¿Qué proporción de la energía viene de cada fuente y cómo cambia en épocas secas?")
    if g.empty:
        st.info("La generación por planta empieza en 2024: amplía el rango de meses.")
    else:
        part = kpis.participacion(g)
        part["Fuente"] = part["tipo"].map(NOMBRE_TIPO)
        orden = [NOMBRE_TIPO[t] for t in COLOR_TIPO]
        colores = {NOMBRE_TIPO[k]: c for k, c in COLOR_TIPO.items()}
        fig = px.bar(part, x="periodo", y="participacion_pct", color="Fuente", category_orders={"Fuente": orden},
                     color_discrete_map=colores, custom_data=["generacion_gwh"])
        fig.update_traces(marker_line_color="#fcfcfb", marker_line_width=1,
                          hovertemplate="%{x}: %{y:.1f} % (%{customdata[0]:,.0f} GWh)<extra></extra>")
        fig.update_layout(bargap=0.15, title="Participación de cada fuente en la generación del mes")
        fig.update_yaxes(title="% de la generación", range=[0, 100])
        fig.update_xaxes(title=None)
        st.plotly_chart(estilo(fig, 400), width="stretch")

        g2 = g.assign(temporada=g["es_temporada_seca"].map({True: "Temporada seca", False: "Temporada de lluvias"}))
        temporada = kpis.participacion(g2, por="temporada")
        por_fase = kpis.participacion(g2, por="fase_enso")
        col_a, col_b = st.columns(2)
        for col, tabla_p, por, titulo in [(col_a, temporada, "temporada", "Seca (dic-mar, jul-ago) frente a lluvias"),
                                          (col_b, por_fase, "fase_enso", "Según la fase de El Niño")]:
            tabla_p["Fuente"] = tabla_p["tipo"].map(NOMBRE_TIPO)
            fig = px.bar(tabla_p, x=por, y="participacion_pct", color="Fuente", barmode="group",
                         category_orders={"Fuente": orden}, color_discrete_map=colores)
            fig.update_traces(hovertemplate="%{x}: %{y:.1f} %<extra></extra>")
            fig.update_layout(title=titulo)
            fig.update_yaxes(title="% de la generación")
            fig.update_xaxes(title=None)
            col.plotly_chart(estilo(fig, 330), width="stretch")
        hidro = temporada[temporada["tipo"] == "HIDRAULICA"].set_index("temporada")["participacion_pct"]
        termo = temporada[temporada["tipo"] == "TERMICA"].set_index("temporada")["participacion_pct"]
        if len(hidro) == 2:
            st.markdown(f"**Lo que dicen los datos:** la hidráulica aporta **{num(hidro['Temporada seca'], 1)} %** "
                        f"de la energía en temporada seca y {num(hidro['Temporada de lluvias'], 1)} % en lluvias; "
                        f"la térmica, **{num(termo['Temporada seca'], 1)} %** en seca y "
                        f"{num(termo['Temporada de lluvias'], 1)} % en lluvias.")
            nino_h = por_fase[(por_fase["fase_enso"] == "El Niño") & (por_fase["tipo"] == "HIDRAULICA")]
            nina_h = por_fase[(por_fase["fase_enso"] == "La Niña") & (por_fase["tipo"] == "HIDRAULICA")]
            if not nino_h.empty and not nina_h.empty:
                st.markdown(f"El cambio grande lo marca El Niño: con El Niño la hidráulica cae a "
                            f"**{num(nino_h['participacion_pct'].iloc[0], 1)} %**, frente a "
                            f"{num(nina_h['participacion_pct'].iloc[0], 1)} % con La Niña.")

# ---------------------------------------------------------------------------
# 4. DEMANDA
# ---------------------------------------------------------------------------
with tabs[3]:
    st.subheader("¿Cuáles son los patrones de demanda por hora, día de la semana y mes? ¿Cuál es la hora pico?")
    if h.empty:
        st.info("No hay datos en el rango elegido.")
    else:
        pico = kpis.hora_pico(h)
        calor = kpis.demanda_hora_dia(h)
        calor.columns = [DIAS[d - 1] for d in calor.columns]
        col_a, col_b = st.columns([3, 2])
        fig = px.imshow(calor.T, color_continuous_scale=["#cde2fb", "#86b6ef", "#3987e5", "#1c5cab", "#0d366b"],
                        aspect="auto", labels=dict(x="Hora del día", y="", color="MWh"))
        fig.update_traces(hovertemplate="%{y} %{x}:00 · %{z:,.0f} MWh<extra></extra>")
        fig.update_layout(title="Demanda promedio de cada hora (MWh)")
        fig.update_xaxes(dtick=2)
        col_a.plotly_chart(estilo(fig, 360), width="stretch")
        por_hora = (h.assign(dia=h["es_fin_de_semana"].map({True: "Fin de semana", False: "Entre semana"}))
                    .groupby(["dia", "hora"], as_index=False)["demanda_mwh"].mean())
        fig = px.line(por_hora, x="hora", y="demanda_mwh", color="dia",
                      color_discrete_map={"Entre semana": AZUL, "Fin de semana": NARANJA})
        fig.add_vrect(x0=16.5, x1=21.5, fillcolor=GRIS, opacity=0.12, line_width=0)
        fig.update_traces(hovertemplate="%{x}:00 · %{y:,.0f} MWh<extra></extra>")
        fig.update_layout(title="Curva diaria (franja pico 17 a 21 h sombreada)")
        fig.update_xaxes(title="Hora", dtick=3)
        fig.update_yaxes(title="MWh")
        col_b.plotly_chart(estilo(fig, 360), width="stretch")

        por_mes = h.groupby(["mes", "nombre_mes"], as_index=False)["demanda_mwh"].mean()
        fig = px.bar(por_mes, x="nombre_mes", y="demanda_mwh", color_discrete_sequence=[AZUL])
        fig.update_traces(hovertemplate="%{x}: %{y:,.0f} MWh por hora<extra></extra>")
        fig.update_layout(title="Demanda promedio por hora según el mes")
        fig.update_xaxes(title=None)
        fig.update_yaxes(title="MWh por hora")
        st.plotly_chart(estilo(fig, 300), width="stretch")
        dia_alto = calor.mean().idxmax()
        dia_bajo = calor.mean().idxmin()
        st.markdown(f"**Lo que dicen los datos:** la hora pico es a las **{pico}:00** "
                    f"({num(h[h['hora'] == pico]['demanda_mwh'].mean())} MWh en promedio). "
                    f"El día de más consumo es el **{dia_alto}** y el de menos el **{dia_bajo}**; "
                    f"el mes más alto es **{por_mes.loc[por_mes['demanda_mwh'].idxmax(), 'nombre_mes']}**.")

# ---------------------------------------------------------------------------
# 5. IMPACTO EN EL NEGOCIO
# ---------------------------------------------------------------------------
with tabs[4]:
    st.subheader("¿Cuánto le habría costado a EnerAndes comprar en bolsa en vez de por contrato? "
                 "¿Dónde se concentra el riesgo?")
    if v.empty:
        st.info("No hay ventas con los filtros elegidos.")
    else:
        costos = kpis.costo_por_mes(v)
        sobrecosto = costos["sobrecosto_bolsa_cop"].sum()
        k1, k2, k3 = st.columns(3)
        k1.metric("Costo real de compra (miles de millones)", miles_de_millones(costos["costo_compra_cop"].sum()))
        k2.metric("Todo en bolsa (miles de millones)", miles_de_millones(costos["costo_si_bolsa_cop"].sum()))
        k3.metric("Bolsa menos contrato (miles de millones)", miles_de_millones(sobrecosto),
                  "la bolsa salió más cara" if sobrecosto > 0 else "la bolsa salió más barata", delta_color="off")
        largo = costos.melt(id_vars="periodo", value_vars=["costo_si_bolsa_cop", "costo_si_contrato_cop",
                                                           "costo_compra_cop"],
                            var_name="escenario", value_name="cop")
        largo["escenario"] = largo["escenario"].map({"costo_si_bolsa_cop": "Todo en bolsa",
                                                     "costo_si_contrato_cop": "Todo por contrato",
                                                     "costo_compra_cop": "Real (mezcla actual)"})
        largo["miles_millones"] = largo["cop"] / 1e9
        fig = px.line(largo, x="periodo", y="miles_millones", color="escenario",
                      color_discrete_map={"Todo en bolsa": NARANJA, "Todo por contrato": AZUL,
                                          "Real (mezcla actual)": "#0b0b0b"})
        fig.update_traces(hovertemplate="%{x}: $%{y:,.1f} mil millones<extra></extra>")
        fig.update_layout(title="Costo de comprar la energía vendida cada mes")
        fig.update_xaxes(title=None, type="category", nticks=12)
        fig.update_yaxes(title="Miles de millones de COP")
        st.plotly_chart(estilo(fig, 380), width="stretch")

        col_a, col_b = st.columns(2)
        for col, por, titulo in [(col_a, "municipio", "Energía comprada en bolsa por municipio"),
                                 (col_b, "segmento", "Energía comprada en bolsa por segmento")]:
            tabla_e = kpis.exposicion_bolsa(v, por=por).head(10).sort_values("energia_bolsa_gwh")
            fig = px.bar(tabla_e, x="energia_bolsa_gwh", y=por, orientation="h", color_discrete_sequence=[NARANJA],
                         custom_data=["participacion_bolsa_pct"])
            fig.update_traces(hovertemplate="%{y}: %{x:,.1f} GWh en bolsa (%{customdata[0]:.1f} % de su energía)"
                                            "<extra></extra>")
            fig.update_layout(title=titulo)
            fig.update_xaxes(title="GWh comprados en bolsa")
            fig.update_yaxes(title=None)
            col.plotly_chart(estilo(fig, 360), width="stretch")
        top = kpis.exposicion_bolsa(v, por="municipio")
        top_seg = kpis.exposicion_bolsa(v, por="segmento")
        meses_caros = (costos["sobrecosto_bolsa_cop"] > 0).sum()
        st.markdown(
            f"**Lo que dicen los datos:** en **{meses_caros} de {len(costos)} meses** la bolsa salió más cara que "
            f"el contrato. **{top.iloc[0]['municipio']}** concentra la mayor energía expuesta a la bolsa "
            f"({num(top.iloc[0]['energia_bolsa_gwh'], 1)} GWh, "
            f"{num(100 * top.iloc[0]['energia_bolsa_gwh'] / top['energia_bolsa_gwh'].sum(), 1)} % del total en bolsa), "
            f"y el segmento **{top_seg.iloc[0]['segmento']}** es el de más energía en bolsa.")
        st.caption("Supuesto: EnerAndes compra al precio promedio del mercado (contratos: PrecPromCont de XM; "
                   "bolsa: precio de bolsa del mes ponderado por la demanda).")

# ---------------------------------------------------------------------------
# 6. PREGUNTA PROPIA: LA SOLAR EN EL NINO
# ---------------------------------------------------------------------------
with tabs[5]:
    st.subheader("Durante El Niño, ¿cuánto aumenta la radiación solar y cuánto compensa la solar la caída "
                 "de la hidráulica?")
    sol = kpis.solar_vs_hidraulica(g, m).dropna(subset=["solar_gwh"])
    if sol.empty:
        st.info("La generación por planta y la radiación empiezan en 2024: amplía el rango de meses.")
    else:
        col_a, col_b = st.columns(2)
        fig = px.bar(sol, x="periodo", y="solar_gwh", color="fase_enso", color_discrete_map=COLOR_FASE,
                     category_orders={"fase_enso": kpis.FASES_ENSO})
        fig.update_traces(hovertemplate="%{x}: %{y:,.0f} GWh<extra></extra>")
        fig.update_layout(title="Generación solar del mes (GWh), color = fase ENSO")
        fig.update_xaxes(title=None, type="category", categoryorder="category ascending")
        fig.update_yaxes(title="GWh")
        col_a.plotly_chart(estilo(fig, 340), width="stretch")
        fig = px.bar(sol, x="periodo", y="radiacion_guajira_kwh_m2", color="fase_enso",
                     color_discrete_map=COLOR_FASE, category_orders={"fase_enso": kpis.FASES_ENSO})
        fig.update_traces(hovertemplate="%{x}: %{y:.2f} kWh/m² por día<extra></extra>")
        fig.update_layout(title="Radiación solar en La Guajira (kWh/m² por día, NASA POWER)")
        fig.update_xaxes(title=None, type="category", categoryorder="category ascending")
        fig.update_yaxes(title="kWh/m² por día")
        col_b.plotly_chart(estilo(fig, 340), width="stretch")

        fase = kpis.promedio_por_fase(sol, ["solar_gwh", "hidraulica_gwh", "radiacion_guajira_kwh_m2"])
        st.dataframe(fase.rename(columns={"fase_enso": "Fase", "solar_gwh": "Solar (GWh/mes)",
                                          "hidraulica_gwh": "Hidráulica (GWh/mes)",
                                          "radiacion_guajira_kwh_m2": "Radiación La Guajira (kWh/m²/día)"})
                     .round(2), hide_index=True, width="stretch")
        f = fase.set_index("fase_enso")
        otras = [x for x in f.index if x not in ("El Niño", "Sin dato")]
        if "El Niño" in f.index and otras:
            base = f.loc[otras].mean()
            nino = f.loc["El Niño"]
            caida = base["hidraulica_gwh"] - nino["hidraulica_gwh"]
            extra = nino["solar_gwh"] - base["solar_gwh"]
            cambio = 100 * (nino["radiacion_guajira_kwh_m2"] / base["radiacion_guajira_kwh_m2"] - 1)
            texto = (f"**Lo que dicen los datos:** en los meses de El Niño la radiación en La Guajira es "
                     f"**{num(abs(cambio), 1)} % {'más alta' if cambio >= 0 else 'más baja'}** que en los demás "
                     f"meses; la solar genera {num(abs(extra))} GWh/mes {'más' if extra >= 0 else 'menos'} y la "
                     f"hidráulica {num(abs(caida))} GWh/mes {'menos' if caida >= 0 else 'más'}")
            if caida > 0 and extra > 0:
                texto += f": la solar compensa el **{num(100 * extra / caida, 1)} %** de esa caída"
            st.markdown(texto + ".")
            st.caption("La solar crece por las plantas nuevas que entran cada mes, no solo por el clima: "
                       "comparar fases mezcla los dos efectos.")
