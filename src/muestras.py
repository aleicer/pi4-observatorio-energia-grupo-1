"""
Muestras de la capa bronce para GitHub.

data/bronze/ NO se sube al repositorio (pesa mucho y se regenera con el pipeline).
Para que cualquiera pueda ver como llegan los datos sin descargarlos, se sube a
data/sample/ un CSV con las primeras 200 filas de cada archivo de bronce.

Uso:
    python -m src.muestras
"""
# ---------------------------------------------------------------------------
# IMPORTS
# ---------------------------------------------------------------------------
import pandas as pd     # pandas: leer cada Parquet y escribir el CSV

from src import config  # rutas del proyecto (DIR_BRONZE)
from src.utils import log

FILAS_MUESTRA = 200                                 # lo que pide el enunciado
DIR_SAMPLE = config.RAIZ / "data" / "sample"        # carpeta que SI se sube a GitHub


def generar_muestras(dir_bronze=None, dir_sample=None, filas: int = FILAS_MUESTRA) -> list:
    """Escribe <nombre>.csv con las primeras 'filas' filas de cada Parquet de bronce.

    Devuelve la lista de archivos CSV creados. Los parametros de carpeta existen
    para poder probar la funcion con carpetas temporales.
    """
    dir_bronze = dir_bronze or config.DIR_BRONZE
    dir_sample = dir_sample or DIR_SAMPLE
    dir_sample.mkdir(parents=True, exist_ok=True)
    creados = []
    for archivo in sorted(dir_bronze.glob("*.parquet")):       # cada archivo de bronce, en orden
        df = pd.read_parquet(archivo).head(filas)              # .head(200): las primeras 200 filas
        destino = dir_sample / f"{archivo.stem}.csv"           # .stem = nombre sin la extension
        df.to_csv(destino, index=False, encoding="utf-8")      # tal cual, sin el indice de pandas
        creados.append(destino)
        log(f"   + {destino.name}: {len(df)} filas")
    return creados


if __name__ == "__main__":
    log(f"Muestras de bronce ({FILAS_MUESTRA} filas) -> data/sample/")
    archivos = generar_muestras()
    if not archivos:
        log("   ! data/bronze/ esta vacia: ejecute primero python -m src.pipeline")
