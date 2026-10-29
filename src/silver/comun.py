"""
Herramientas comunes de la capa PLATA (las usan todos los programas de limpieza).

Cada fuente tiene su archivo en src/silver/ (enerandes.py, xm.py, ideam.py,
noaa.py, nasa_power.py) y todos siguen la misma forma:

    def limpiar(bronce) -> (limpias, cuarentena, metricas)   # reglas, sin leer ni guardar
    def main()                                                # lee bronce, limpia y guarda

Este archivo trae lo que se repite en todas:
  - Medidor:        anota cada regla con su metrica ANTES y DESPUES
  - guardar_plata:  valida con pandera, guarda el Parquet limpio, la cuarentena
                    y las metricas (para el reporte de calidad)
"""
# ---------------------------------------------------------------------------
# IMPORTS
# ---------------------------------------------------------------------------
import json             # json: guardar las metricas en un archivo de texto

import pandas as pd     # pandas: tablas

from src import config  # rutas de las carpetas (DIR_SILVER)
from src.utils import log

LINAJE = ["_fuente", "_origen", "_extraido_en"]   # columnas que agrego guardar_bronce()


class Medidor:
    """Lista de reglas de calidad con su metrica antes y despues.

    Uso:
        m = Medidor()
        m.medir("Filas duplicadas", "Dejar una sola copia", 32, 0)
        m.metricas  ->  [{"problema": ..., "regla aplicada": ..., "antes": 32, "despues": 0}]
    """

    def __init__(self):
        self.metricas = []          # aqui se van guardando las reglas

    def medir(self, problema: str, regla: str, antes, despues) -> None:
        """Agrega una regla al reporte: que problema habia, que se hizo y el antes/despues."""
        self.metricas.append({"problema": problema, "regla aplicada": regla,
                              "antes": antes, "despues": despues})


def a_cuarentena(df: pd.DataFrame, malas: pd.Series, motivo: str) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Separa las filas 'malas' (True) en cuarentena con su motivo. Devuelve (buenas, cuarentena)."""
    cuarentena = df[malas].copy()
    cuarentena["motivo_cuarentena"] = motivo          # por que la fila no se pudo usar
    return df[~malas].copy(), cuarentena


def guardar_plata(limpias: pd.DataFrame, nombre: str, esquema, fuente: str,
                  metricas: list[dict], filas_bronce: int,
                  cuarentena: pd.DataFrame | None = None) -> None:
    """Valida con pandera y guarda la capa plata de una fuente.

    Escribe en data/silver/:
      <nombre>.parquet               la tabla limpia (solo si pasa pandera)
      <nombre>_cuarentena.parquet    las filas que no se pudieron corregir (si hay)
      _metricas_<nombre>.json        las reglas con su antes/despues, para el reporte
    """
    # Si una regla de pandera falla, el programa se detiene aqui y NO se guarda nada.
    # lazy=True: revisa toda la tabla y muestra todos los errores juntos
    esquema.validate(limpias, lazy=True)
    log(f"   {nombre}: validacion con pandera OK")

    config.DIR_SILVER.mkdir(parents=True, exist_ok=True)
    limpias.to_parquet(config.DIR_SILVER / f"{nombre}.parquet", index=False)
    n_cuarentena = 0 if cuarentena is None else len(cuarentena)
    if n_cuarentena:
        # Las columnas de la cuarentena se guardan como texto: ahi hay valores raros
        cuarentena.astype(str).to_parquet(config.DIR_SILVER / f"{nombre}_cuarentena.parquet", index=False)

    motivos = {} if not n_cuarentena else cuarentena["motivo_cuarentena"].value_counts().to_dict()
    resumen = {"fuente": fuente, "tabla": nombre, "filas_bronce": int(filas_bronce),
               "filas_plata": len(limpias), "filas_cuarentena": n_cuarentena,
               "motivos_cuarentena": {k: int(v) for k, v in motivos.items()},
               "metricas": metricas}
    # default=str convierte a texto lo que json no sabe guardar (por ejemplo numeros de numpy)
    (config.DIR_SILVER / f"_metricas_{nombre}.json").write_text(
        json.dumps(resumen, ensure_ascii=False, indent=2, default=str), encoding="utf-8")
    log(f"   + {nombre}.parquet: {len(limpias):,} filas limpias, {n_cuarentena:,} en cuarentena")
