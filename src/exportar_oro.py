
"""
Exporta las tablas de la capa oro a archivos Parquet.

Ejecutar desde la raíz del proyecto:
    python -m src.exportar_oro
"""

import os
from datetime import datetime, timedelta, timezone
from pathlib import Path

import duckdb

from src import config
from src.utils import log


TABLAS_ORO = [
    "dim_fecha",
    "dim_hora",
    "dim_municipio",
    "dim_segmento",
    "dim_recurso",
    "dim_estacion",
    "fact_ventas_mensual",
    "fact_mercado_horario",
    "fact_generacion_recurso",
    "fact_hidrologia_diaria",
    "fact_clima_diario",
    "fact_clima_satelital",
    "fact_precio_contrato_diario",
    # Tablas resumidas para el dashboard
    "mart_hidroclima_mensual",
    "mart_generacion_tipo_diaria",
    "mart_mercado_horario",
    "mart_ventas_costo_mensual",
]

CARPETA_ORO = config.RAIZ / "data" / "gold"


def exportar(ruta_db: Path, carpeta: Path, tablas: list[str]) -> dict[Path, int]:
    """Exporta las tablas a Parquet y devuelve sus cantidades de filas."""
    carpeta.mkdir(parents=True, exist_ok=True)

    filas_por_archivo = {}

    con = duckdb.connect(str(ruta_db), read_only=True)

    try:
        for tabla in tablas:
            archivo = carpeta / f"{tabla}.parquet"

            con.execute(
                f"COPY {tabla} TO '{archivo.as_posix()}' (FORMAT parquet)"
            )

            filas = con.execute(
                f"SELECT COUNT(*) FROM {tabla}"
            ).fetchone()[0]

            log(f"   {archivo.name:<34}{filas:>12,} filas")
            filas_por_archivo[archivo] = filas
    finally:
        con.close()

    return filas_por_archivo


def resumen_markdown(filas_por_archivo: dict[Path, int]) -> str:
    """Construye el resumen que se muestra en GitHub Actions."""
    hora = datetime.now(timezone(timedelta(hours=-5)))

    lineas = [
        f"### Capa oro actualizada el {hora:%Y-%m-%d %H:%M} (hora Colombia)",
        "",
        "| Tabla | Filas |",
        "|---|---:|",
    ]

    for archivo, filas in filas_por_archivo.items():
        lineas.append(f"| `{archivo.stem}` | {filas:,} |")

    lineas.append("")
    lineas.append(
        "Los Parquet se descargan desde el artefacto **capa-oro** de esta ejecución."
    )

    return "\n".join(lineas) + "\n"


def main() -> None:
    log("Exportando la capa oro a Parquet")

    filas = exportar(
        config.RAIZ / "data" / "observatorio.duckdb",
        CARPETA_ORO,
        TABLAS_ORO,
    )

    log(f"Listo: {len(filas)} archivos en data/gold/")

    ruta_resumen = os.environ.get("GITHUB_STEP_SUMMARY")

    if ruta_resumen:
        with open(ruta_resumen, "a", encoding="utf-8") as archivo:
            archivo.write(resumen_markdown(filas))


if __name__ == "__main__":
    main()
