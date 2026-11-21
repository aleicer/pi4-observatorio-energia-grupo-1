
"""Pruebas EA3: historia de XM y precio promedio de contratos."""

from datetime import date

import pandas as pd

from src import config
from src.extract import xm
from src.silver.xm import limpiar_contratos


def test_sistema_consulta_historia_desde_2015(monkeypatch):
    """Las metricas del Sistema deben comenzar el 1 de enero de 2015."""
    solicitudes = []

    def simular_ventanas(inicio, fin, max_dias):
        solicitudes.append((inicio, fin, max_dias))
        return [(inicio, inicio)]

    def simular_http(metodo, url, json):
        return {"Items": []}

    monkeypatch.setattr(xm, "ya_existe", lambda nombre, forzar: False)
    monkeypatch.setattr(xm, "ventanas", simular_ventanas)
    monkeypatch.setattr(xm, "http_json", simular_http)
    monkeypatch.setattr(xm, "guardar_bronce", lambda *args, **kwargs: None)

    xm.extraer_metrica(
        "PrecPromCont",
        "Sistema",
        "daily",
        "xm_precio_contratos",
        False,
    )

    assert len(solicitudes) == 1
    assert solicitudes[0][0] == date(2015, 1, 1)
    assert solicitudes[0][1] == config.FECHA_FIN


def test_generacion_conserva_fecha_inicial(monkeypatch):
    """La generacion por recurso mantiene la fecha inicial original."""
    solicitudes = []

    def simular_ventanas(inicio, fin, max_dias):
        solicitudes.append((inicio, fin, max_dias))
        return [(inicio, inicio)]

    monkeypatch.setattr(xm, "ya_existe", lambda nombre, forzar: False)
    monkeypatch.setattr(xm, "ventanas", simular_ventanas)
    monkeypatch.setattr(
        xm,
        "http_json",
        lambda metodo, url, json: {"Items": []},
    )
    monkeypatch.setattr(xm, "guardar_bronce", lambda *args, **kwargs: None)

    xm.extraer_metrica(
        "Gene",
        "Recurso",
        "hourly",
        "xm_generacion_recurso",
        False,
    )

    assert len(solicitudes) == 1
    assert solicitudes[0][0] == config.FECHA_INICIO
    assert solicitudes[0][1] == config.FECHA_FIN


def test_contratos_limpia_duplicados_y_precios_invalidos():
    """Conserva precios validos y separa registros invalidos."""
    contratos = pd.DataFrame({
        "Date": [
            "2026-01-01",
            "2026-01-01",
            "2026-01-02",
            "2026-01-03",
            "2026-01-04",
        ],
        "Value": [
            "250.5",
            "251.0",
            "-10",
            "0",
            "300.0",
        ],
    })

    limpias, cuarentena, metricas = limpiar_contratos(contratos)

    assert len(limpias) == 2
    assert len(cuarentena) == 2
    assert not limpias["fecha"].duplicated().any()
    assert (limpias["precio_contrato_cop_kwh"] > 0).all()

    assert set(limpias["fecha"]) == {
        date(2026, 1, 1),
        date(2026, 1, 4),
    }

    assert metricas is not None
