"""
Reporte de calidad: junta las metricas de todas las limpiezas en docs/reporte_calidad.md

Cada programa de src/silver/ deja en data/silver/_metricas_<tabla>.json sus reglas con
la metrica antes y despues. Este programa las lee y escribe UNA tabla por fuente.
El reporte se GENERA con el codigo: no se escribe a mano.

Uso:
    python -m src.silver.reporte
"""
import json
from datetime import datetime

from src import config
from src.utils import log

SALIDA = config.DIR_DOCS / "reporte_calidad.md"


def a_markdown(resumenes: list[dict]) -> str:
    """Arma el Markdown del reporte a partir de los resumenes de cada tabla."""
    total_reglas = sum(len(r["metricas"]) for r in resumenes)
    total_cuarentena = sum(r["filas_cuarentena"] for r in resumenes)
    lineas = [
        "# Reporte de calidad de la capa plata",
        "",
        f"> Generado con `python -m src.transformar` el {datetime.now():%Y-%m-%d %H:%M}. "
        "No se edita a mano: se reemplaza cada vez que se construye la capa plata.",
        "",
        "## Resumen",
        "",
        "| Fuente | Tabla de plata | Filas en bronce | Filas en plata | Filas en cuarentena | Reglas |",
        "|---|---|---:|---:|---:|---:|",
    ]
    for r in resumenes:
        lineas.append(f"| {r['fuente']} | `{r['tabla']}` | {r['filas_bronce']:,} | {r['filas_plata']:,} | "
                      f"{r['filas_cuarentena']:,} | {len(r['metricas'])} |")
    lineas += ["", f"**Total: {total_reglas} reglas de calidad y {total_cuarentena:,} filas en cuarentena.**", ""]

    for r in resumenes:
        lineas += [f"## {r['fuente']} – `{r['tabla']}`", "",
                   f"Filas en bronce: {r['filas_bronce']:,} · Filas en plata: {r['filas_plata']:,} · "
                   f"Filas en cuarentena: {r['filas_cuarentena']:,}", "",
                   "| # | Problema | Regla aplicada | Antes | Después |",
                   "|---|---|---|---:|---:|"]
        for n, m in enumerate(r["metricas"], start=1):
            antes = f"{m['antes']:,}" if isinstance(m["antes"], int) else m["antes"]
            despues = f"{m['despues']:,}" if isinstance(m["despues"], int) else m["despues"]
            lineas.append(f"| {n} | {m['problema']} | {m['regla aplicada']} | {antes} | {despues} |")
        if r["motivos_cuarentena"]:
            lineas += ["", "**Filas en cuarentena y por qué** "
                       f"(archivo `data/silver/{r['tabla']}_cuarentena.parquet`):", ""]
            for motivo, n in r["motivos_cuarentena"].items():
                lineas.append(f"- {motivo}: {n:,} filas")
        lineas.append("")
    return "\n".join(lineas)


def main() -> None:
    archivos = sorted(config.DIR_SILVER.glob("_metricas_*.json"))
    if not archivos:
        log("No hay metricas en data/silver/. Primero ejecute: python -m src.transformar")
        return
    resumenes = [json.loads(a.read_text(encoding="utf-8")) for a in archivos]
    resumenes.sort(key=lambda r: (r["fuente"], r["tabla"]))
    config.DIR_DOCS.mkdir(parents=True, exist_ok=True)
    SALIDA.write_text(a_markdown(resumenes), encoding="utf-8")
    log(f"Reporte de calidad: {sum(len(r['metricas']) for r in resumenes)} reglas en "
        f"{SALIDA.relative_to(config.RAIZ)}")


if __name__ == "__main__":
    main()
