"""
Prueba de que la lista de tablas que se exportan (TABLAS_ORO) coincide con los
modelos de dbt. Si alguien crea un modelo nuevo y olvida agregarlo a la lista, el
dashboard no lo veria: esta prueba sale en rojo y avisa cual falta.
"""

from src import config
from src.exportar_oro import TABLAS_ORO


def modelos_de_dbt() -> set[str]:
    """Nombres de los .sql de dbt/models/marts/ y dbt/models/dashboard/ (sin .sql)."""
    carpetas = [
        config.RAIZ / "dbt" / "models" / "marts",
        config.RAIZ / "dbt" / "models" / "dashboard",
    ]
    return {
        archivo.stem
        for carpeta in carpetas
        for archivo in carpeta.glob("*.sql")
    }


def test_cada_modelo_de_dbt_se_exporta():
    faltan = modelos_de_dbt() - set(TABLAS_ORO)
    assert not faltan, f"Modelos de dbt que no estan en TABLAS_ORO: {sorted(faltan)}"


def test_no_se_exporta_una_tabla_que_dbt_no_crea():
    sobran = set(TABLAS_ORO) - modelos_de_dbt()
    assert not sobran, f"Tablas en TABLAS_ORO que no son modelos de dbt: {sorted(sobran)}"


def test_no_hay_tablas_repetidas():
    assert len(TABLAS_ORO) == len(set(TABLAS_ORO))