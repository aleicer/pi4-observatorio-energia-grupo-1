import pytest

from src import config
from src.silver.nasa_power import main

def test_main_indica_como_generar_bronce_si_no_existe(tmp_path, monkeypatch):
    monkeypatch.setattr(config, "DIR_BRONZE", tmp_path)

    with pytest.raises(FileNotFoundError) as error:
        main()

    assert "python -m src.extract.nasa_power" in str(error.value)

def test_nasa_cambia_menos_999_por_vacio_y_pasa_a_ancho():
    import numpy as np
    import pandas as pd
    from src.silver.nasa_power import limpiar

    bronce = pd.DataFrame({
        "punto": ["Medellin"] * 3,
        "latitud": [6.24] * 3,
        "longitud": [-75.58] * 3,
        "variable": [
            "ALLSKY_SFC_SW_DWN",
            "T2M",
            "PRECTOTCORR"
        ],
        "fecha": ["20240101"] * 3,
        "valor": [-999.0, 21.5, 3.2],
    })

    limpias, _, _ = limpiar(bronce)

    assert len(limpias) == 1
    assert np.isnan(limpias.loc[0, "radiacion_kwh_m2"])
    assert limpias.loc[0, "temperatura_c"] == 21.5