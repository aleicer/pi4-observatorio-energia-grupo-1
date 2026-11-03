
"""Pruebas de las reglas de limpieza de EnerAndes."""

import pytest
import pandas as pd

from src.silver.xm import a_formato_largo
from src.silver.enerandes import a_kwh, leer_periodo


def test_leer_periodo_entiende_los_cuatro_formatos():
    assert leer_periodo("2024-03") == "2024-03"
    assert leer_periodo("mar-24") == "2024-03"
    assert leer_periodo("03/2024") == "2024-03"
    assert leer_periodo("01/03/2026") == "2026-03"
    assert leer_periodo("aug-24") == "2024-08"
    assert leer_periodo("TOTAL") is None


def test_a_kwh_convierte_mwh_y_deja_kwh_igual():
    assert a_kwh(479.907, "MWh") == pytest.approx(479907)
    assert a_kwh(1000, "kWh") == 1000

def test_xm_pasa_de_24_columnas_a_una_fila_por_hora():
    ancho = pd.DataFrame({
        "Date": ["2026-09-01"],
        "Id": ["Sistema"],
        "Hour01": ["250.5"],
        "Hour24": ["300"],
    })

    largo = a_formato_largo(ancho, "precio")

    assert len(largo) == 2
    assert list(largo["hora"]) == [0, 23]
    assert largo["precio"].tolist() == [250.5, 300.0]