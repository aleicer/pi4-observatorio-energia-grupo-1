"""
Ejecuta las consultas SQL de consultas/oro/ sobre la capa oro
(data/observatorio.duckdb) y escribe sus resultados en
docs/resultados_consultas.md.

Uso:
    python -m src.consultar_oro
"""

import duckdb

from src import config
from src.utils import log


BASE = config.RAIZ / "data" / "observatorio.duckdb"
CARPETA = config.RAIZ / "consultas" / "oro"
SALIDA = config.DIR_DOCS / "resultados_consultas.md"


def tabla_markdown(df) -> str:
    """Convierte una tabla de pandas en una tabla Markdown."""
    columnas = [str(columna) for columna in df.columns]
    lineas = [
        "| " + " | ".join(columnas) + " |",
        "|" + "---|" * len(columnas),
    ]

    for fila in df.itertuples(index=False):
        lineas.append("| " + " | ".join(str(valor) for valor in fila) + " |")

    return "\n".join(lineas)


def main() -> None:
    if not BASE.exists():
        raise FileNotFoundError(
            f"No existe la base de datos: {BASE}\n"
            "Primero ejecuta: python -m src.transformar"
        )

    archivos = sorted(CARPETA.glob("*.sql"))
    if not archivos:
        raise FileNotFoundError(
            f"No hay consultas SQL en: {CARPETA}"
        )

    con = duckdb.connect(str(BASE), read_only=True)
    texto = ["# Resultados de las consultas sobre la capa oro", ""]

    try:
        for archivo in archivos:
            sql = archivo.read_text(encoding="utf-8")
            pregunta = sql.splitlines()[0].lstrip("- ").strip()
            df = con.sql(sql).df()

            log(f"{archivo.name}: {len(df)} filas")
            print(df.to_string(index=False), "\n")

            texto += [
                f"## {pregunta}",
                "",
                f"Consulta: `consultas/oro/{archivo.name}`",
                "",
                tabla_markdown(df),
                "",
            ]
    finally:
        con.close()

    SALIDA.write_text("\n".join(texto), encoding="utf-8")
    log(f"Resultados en {SALIDA.relative_to(config.RAIZ)}")


if __name__ == "__main__":
    main()