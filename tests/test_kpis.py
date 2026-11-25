"""
Pruebas de los calculos del dashboard (dashboard/kpis.py) con datos de ejemplo.

Cada prueba arma una tabla pequena cuyo resultado se conoce de antemano, y revisa que
el KPI de el numero esperado. No usan la capa oro real ni Streamlit.

Uso:
    python -m pytest tests/test_kpis.py -v
"""
import pandas as pd
import pytest

from dashboard import kpis


def meses(n, desde="2020-01"):
    """Lista de n periodos AAAA-MM seguidos."""
    return list(pd.period_range(desde, periods=n, freq="M").astype(str))


def test_el_rezago_del_oni_al_precio_se_encuentra():
    # Precio que copia el ONI de hace 3 meses: el mejor rezago tiene que ser 3
    oni = [0.1, 0.8, -0.5, 1.2, 0.3, -1.0, 0.9, 0.0, -0.7, 1.5, 0.4, -0.2, 0.6, -1.1, 1.0, 0.2]
    precio = [None, None, None] + [500 + 100 * v for v in oni[:-3]]
    tabla = pd.DataFrame({"periodo": meses(len(oni)), "oni": oni, "precio_bolsa_cop_kwh": precio})
    rezagos = kpis.correlacion_rezago(tabla, max_rezago=6)
    mejor = kpis.mejor_rezago(rezagos)
    assert mejor["rezago_meses"] == 3
    assert mejor["correlacion"] == pytest.approx(1.0)
    assert list(rezagos["rezago_meses"]) == [0, 1, 2, 3, 4, 5, 6]


def test_la_hora_pico_es_la_de_mayor_demanda_promedio():
    # Dos dias de 24 horas; la hora 19 tiene la demanda mas alta los dos dias
    filas = [{"hora": h, "dia_semana": d, "demanda_mwh": 8000 + (2000 if h == 19 else h * 10)}
             for d in (1, 2) for h in range(24)]
    mercado = pd.DataFrame(filas)
    assert kpis.hora_pico(mercado) == 19
    assert kpis.demanda_hora_dia(mercado).shape == (24, 2)       # 24 horas x 2 dias


def test_costo_por_mes_suma_los_escenarios_y_el_sobrecosto():
    ventas = pd.DataFrame({
        "periodo": ["2024-01", "2024-01", "2024-02"],
        "energia_kwh": [100.0, 50.0, 10.0],
        "costo_compra_cop": [30000.0, 40000.0, 3000.0],
        "costo_si_bolsa_cop": [80000.0, 40000.0, 2000.0],     # bolsa a 800 en enero y 200 en febrero
        "costo_si_contrato_cop": [30000.0, 15000.0, 3000.0],  # contrato a 300 los dos meses
    })
    tabla = kpis.costo_por_mes(ventas).set_index("periodo")
    assert tabla.loc["2024-01", "energia_kwh"] == 150
    assert tabla.loc["2024-01", "sobrecosto_bolsa_cop"] == 120000 - 45000   # la bolsa salio mas cara
    assert tabla.loc["2024-02", "sobrecosto_bolsa_cop"] == -1000            # la bolsa salio mas barata


def test_la_exposicion_a_bolsa_por_municipio():
    ventas = pd.DataFrame({
        "municipio": ["Medellín", "Medellín", "Bello"],
        "tipo_compra": ["Contrato", "Bolsa", "Contrato"],
        "energia_kwh": [3e6, 1e6, 2e6],
    })
    tabla = kpis.exposicion_bolsa(ventas).set_index("municipio")
    assert tabla.loc["Medellín", "participacion_bolsa_pct"] == pytest.approx(25.0)
    assert tabla.loc["Bello", "energia_bolsa_gwh"] == 0                     # sin compras en bolsa


def test_los_episodios_de_el_nino_necesitan_5_meses_seguidos():
    fases = (["El Niño"] * 6 + ["Neutral"] * 3 + ["El Niño"] * 3)   # una racha de 6 y otra de 3
    volumen = [70, 60, 40, 35, 50, 65, 70, 72, 68, 30, 31, 32]
    tabla = pd.DataFrame({"periodo": meses(12, "2015-01"), "fase_enso": fases,
                          "volumen_util_min_pct": volumen})
    episodios = kpis.episodios_nino(tabla)
    assert len(episodios) == 1                            # la racha de 3 meses no cuenta
    assert episodios.loc[0, "episodio"] == "El Niño 2015"
    assert episodios.loc[0, "periodo_minimo"] == "2015-04"
    assert episodios.loc[0, "volumen_util_min_pct"] == 35


def test_la_participacion_de_cada_tipo_suma_100_por_mes():
    gen = pd.DataFrame({"periodo": ["2024-01"] * 3 + ["2024-02"] * 2,
                        "tipo": ["HIDRAULICA", "TERMICA", "SOLAR", "HIDRAULICA", "TERMICA"],
                        "generacion_gwh": [60.0, 30.0, 10.0, 50.0, 50.0]})
    tabla = kpis.participacion(gen)
    assert tabla.groupby("periodo")["participacion_pct"].sum().tolist() == pytest.approx([100, 100])
    fila = tabla[(tabla["periodo"] == "2024-01") & (tabla["tipo"] == "HIDRAULICA")]
    assert fila["participacion_pct"].iloc[0] == pytest.approx(60.0)
