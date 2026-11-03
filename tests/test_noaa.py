
"""Pruebas de calidad para la limpieza del índice ONI de NOAA."""

import pandas as pd
import pandera.errors
import pytest

from src.quality.esquemas import ESQUEMA_NOAA
from src.silver.noaa import fase_enso, limpiar as limpiar_noaa


def oni_de_ejemplo():
    """Datos pequeños para comprobar las reglas de NOAA."""
    return pd.DataFrame({
        "SEAS": ["DJF", "JFM", "NDJ"],
        "YR": ["2026", "2026", "2025"],
        "TOTAL": ["26.10", "26.40", "26.00"],
        "ANOM": ["0.50", "-0.49", "-0.50"],
    })


def test_fase_enso_respeta_los_umbrales():
    assert fase_enso(0.5) == "El Niño"
    assert fase_enso(2.16) == "El Niño"
    assert fase_enso(-0.5) == "La Niña"
    assert fase_enso(0.49) == "Neutral"
    assert fase_enso(-0.49) == "Neutral"


def test_trimestre_movil_pasa_a_su_mes_central():
    limpias, _, _ = limpiar_noaa(oni_de_ejemplo())

    por_trimestre = dict(
        zip(limpias["trimestre_movil"], limpias["periodo"])
    )

    assert por_trimestre["DJF"] == "2026-01"
    assert por_trimestre["JFM"] == "2026-02"
    assert por_trimestre["NDJ"] == "2025-12"


def test_oni_queda_como_numero_y_con_fase():
    limpias, _, _ = limpiar_noaa(oni_de_ejemplo())

    fila = limpias[limpias["periodo"] == "2026-01"].iloc[0]

    assert fila["oni"] == 0.5
    assert fila["fase_enso"] == "El Niño"


def test_pandera_rechaza_una_fase_inventada():
    limpias, _, _ = limpiar_noaa(oni_de_ejemplo())

    limpias.loc[0, "fase_enso"] = "Niño fuerte"

    with pytest.raises(pandera.errors.SchemaErrors):
        ESQUEMA_NOAA.validate(limpias, lazy=True)
