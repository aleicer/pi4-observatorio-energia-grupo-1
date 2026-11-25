"""
Prueba de calidad del precio de contratos de XM (EA3).

Al revisar el dashboard con los datos reales se encontro que XM reporto, entre abril y
junio de 2026, un precio promedio de contratos de 0,045 COP/kWh: positivo, pero no es un
precio real (el normal ronda los 300). Esta prueba asegura que esos valores van a la
cuarentena y no llegan a la capa oro.
"""
import pandas as pd

from src.quality.esquemas_xm import ESQUEMA_XM_CONTRATOS
from src.silver.xm import PRECIO_CONTRATO_MINIMO, limpiar_contratos


def test_un_precio_de_contratos_imposiblemente_bajo_va_a_cuarentena():
    bronce = pd.DataFrame({
        "Date": ["2026-03-31", "2026-04-01", "2026-04-02"],
        "Value": ["310.2", "0.04578", "0.04619"],      # como llego de XM en abril de 2026
    })
    limpias, cuarentena, metricas = limpiar_contratos(bronce)
    assert list(limpias["precio_contrato_cop_kwh"]) == [310.2]
    assert len(cuarentena) == 2
    assert cuarentena["motivo_cuarentena"].str.contains(str(PRECIO_CONTRATO_MINIMO)).all()
    # La regla queda en las metricas, para que salga en el reporte de calidad
    assert any(str(PRECIO_CONTRATO_MINIMO) in fila["problema"] and fila["antes"] == 2 for fila in metricas)


def test_pandera_rechaza_un_precio_de_contratos_menor_al_minimo():
    tabla = pd.DataFrame({"fecha": [pd.Timestamp("2026-04-02").date()], "precio_contrato_cop_kwh": [0.046]})
    try:
        ESQUEMA_XM_CONTRATOS.validate(tabla)
        rechazo = False
    except Exception:
        rechazo = True
    assert rechazo
