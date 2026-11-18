
"""
Pruebas de la exportación de la capa oro.

Ejecutar:
    python -m pytest tests/test_exportar_oro.py -v
"""

import duckdb
import pandas as pd

from src.exportar_oro import exportar, resumen_markdown


def base_de_ejemplo(tmp_path):
    """Crea una base DuckDB temporal con dos tablas."""
    ruta_db = tmp_path / "ejemplo.duckdb"

    con = duckdb.connect(str(ruta_db))
    con.execute(
        "CREATE TABLE dim_hora AS SELECT * FROM range(3) t(hora)"
    )
    con.execute(
        "CREATE TABLE dim_segmento AS "
        "SELECT 'Residencial' AS segmento "
        "UNION ALL SELECT 'Industrial'"
    )
    con.close()

    return ruta_db


def test_exporta_un_parquet_por_tabla(tmp_path):
    ruta_db = base_de_ejemplo(tmp_path)

    filas = exportar(
        ruta_db,
        tmp_path / "gold",
        ["dim_hora", "dim_segmento"],
    )

    assert [archivo.name for archivo in filas] == [
        "dim_hora.parquet",
        "dim_segmento.parquet",
    ]
    assert list(filas.values()) == [3, 2]

    assert len(
        pd.read_parquet(tmp_path / "gold" / "dim_hora.parquet")
    ) == 3

    assert len(
        pd.read_parquet(tmp_path / "gold" / "dim_segmento.parquet")
    ) == 2


def test_el_resumen_de_actions_trae_cada_tabla(tmp_path):
    ruta_db = base_de_ejemplo(tmp_path)

    filas = exportar(
        ruta_db,
        tmp_path / "gold",
        ["dim_hora", "dim_segmento"],
    )

    texto = resumen_markdown(filas)

    assert "| `dim_hora` | 3 |" in texto
    assert "| `dim_segmento` | 2 |" in texto
