"""
Construye las capas PLATA y ORO con un solo comando.

  1. Ejecuta la limpieza de cada fuente (src/silver/*.py): bronce -> plata,
     validando cada tabla con pandera antes de guardarla
  2. Escribe el reporte de calidad (docs/reporte_calidad.md)
  3. Ejecuta dbt build: crea el esquema estrella (capa oro) en data/observatorio.duckdb
     y corre todas las pruebas de dbt

Requisito: la capa bronce ya descargada (python -m src.pipeline).

Uso:
    python -m src.transformar              # plata + reporte + oro
    python -m src.transformar --solo-plata # sin dbt
"""
import importlib
import os
import sys
import time

from src import config
from src.silver import reporte
from src.utils import log

# Archivos de src/silver/ que NO son limpiezas (son herramientas)
NO_SON_LIMPIEZAS = {"__init__", "comun", "reporte"}


def limpiezas() -> list:
    """Busca las limpiezas en src/silver/: cada archivo .py con una funcion main().

    Asi, para agregar una fuente nueva basta con crear src/silver/<fuente>.py:
    no hay que tocar este archivo.
    """
    carpeta = config.RAIZ / "src" / "silver"
    nombres = sorted(a.stem for a in carpeta.glob("*.py") if a.stem not in NO_SON_LIMPIEZAS)
    # importlib.import_module("src.silver.xm") hace lo mismo que "from src.silver import xm"
    modulos = [importlib.import_module(f"src.silver.{n}") for n in nombres]
    return [m for m in modulos if hasattr(m, "main")]


def construir_oro() -> None:
    """Ejecuta 'dbt build' (modelos + pruebas) desde la raiz del proyecto."""
    from dbt.cli.main import dbtRunner          # se importa aqui: tarda unos segundos en cargar
    os.chdir(config.RAIZ)                       # profiles.yml usa rutas desde la raiz
    resultado = dbtRunner().invoke(["build", "--project-dir", "dbt", "--profiles-dir", "dbt"])
    if not resultado.success:
        raise SystemExit("dbt build termino con errores: revise la salida de arriba")


def main() -> None:
    inicio = time.time()
    log("CAPA PLATA: limpieza y validacion de cada fuente")
    for limpieza in limpiezas():
        log(f"-- {limpieza.__name__.split('.')[-1]}")
        limpieza.main()
    reporte.main()
    if "--solo-plata" not in sys.argv:
        log("CAPA ORO: dbt build (esquema estrella y pruebas)")
        construir_oro()
    log(f"Listo en {time.time() - inicio:.0f} s")


if __name__ == "__main__":
    main()
