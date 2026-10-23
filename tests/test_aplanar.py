
"""Pruebas de aplanar(): JSON anidado de XM a filas planas, sin cambiar valores."""

from src.extract.xm import aplanar


def test_aplanar_horario():
    """Verifica que los datos horarios se conviertan en filas planas."""
    respuesta = {
        "Items": [{
            "Date": "2026-09-01",
            "HourlyEntities": [{
                "Id": "Sistema",
                "Values": {
                    "code": "Sistema",
                    "Hour01": "250.5",
                    "Hour02": "240.1"
                }
            }]
        }]
    }

    filas = aplanar(respuesta, "hourly")

    assert filas == [{
        "Date": "2026-09-01",
        "Id": "Sistema",
        "code": "Sistema",
        "Hour01": "250.5",
        "Hour02": "240.1"
    }]


def test_aplanar_diario():
    """Comprueba que los valores diarios se conserven sin cambios."""
    respuesta = {
        "Items": [
            {
                "Date": "2026-09-01",
                "DailyEntities": [
                    {"Id": "Sistema", "Value": "65.3"}
                ]
            },
            {
                "Date": "2026-09-02",
                "DailyEntities": [
                    {"Id": "Sistema", "Value": "64.9"}
                ]
            }
        ]
    }

    filas = aplanar(respuesta, "daily")

    assert len(filas) == 2
    assert filas[1]["Value"] == "64.9"


def test_aplanar_lista_de_recursos():
    """Verifica la extracción del catálogo de plantas de XM."""
    respuesta = {
        "Items": [{
            "Date": "2026-10-20",
            "ListEntities": [
                {
                    "Id": "Sistema",
                    "Values": {
                        "Code": "GUA1",
                        "Name": "GUATAPE",
                        "Type": "HIDRAULICA"
                    }
                },
                {
                    "Id": "Sistema",
                    "Values": {
                        "Code": "SOL1",
                        "Name": "PARQUE SOLAR",
                        "Type": "SOLAR"
                    }
                }
            ]
        }]
    }

    filas = aplanar(respuesta, "lists")

    assert [f["Code"] for f in filas] == ["GUA1", "SOL1"]
    assert filas[0]["Type"] == "HIDRAULICA"


def test_aplanar_respuesta_vacia():
    """Comprueba que una respuesta vacía no genere errores."""
    assert aplanar({}, "hourly") == []
