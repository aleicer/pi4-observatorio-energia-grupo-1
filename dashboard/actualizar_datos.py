"""
Copia las tablas del dashboard de data/gold/ a dashboard/datos/.

Streamlit Community Cloud solo ve lo que esta en GitHub, y data/gold/ no se sube (la
regenera el pipeline). Por eso la version publicada lee una copia de las 4 tablas del
dashboard (menos de 2 MB) que si se sube. Se actualiza asi, despues del pipeline:

    python -m src.exportar_oro
    python dashboard/actualizar_datos.py
"""
import shutil
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
ORIGEN = RAIZ / "data" / "gold"
DESTINO = RAIZ / "dashboard" / "datos"
TABLAS = ["mart_hidroclima_mensual", "mart_generacion_tipo_diaria", "mart_mercado_horario",
          "mart_ventas_costo_mensual"]

DESTINO.mkdir(exist_ok=True)
for tabla in TABLAS:
    shutil.copy2(ORIGEN / f"{tabla}.parquet", DESTINO / f"{tabla}.parquet")
    print(f"Copiada {tabla}.parquet")
print(f"Listo: {len(TABLAS)} tablas en dashboard/datos/")
