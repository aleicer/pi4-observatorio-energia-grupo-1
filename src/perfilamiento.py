"""
Perfilamiento de la capa bronce: genera docs/perfilamiento.md

Por cada archivo de data/bronze/ calcula lo que pide la EA1:
  filas, columnas, tipos de datos, % de nulos por columna, filas duplicadas
  y rango de fechas.

IMPORTANTE: todo lo que este DESPUES de la marca <!-- HALLAZGOS --> en
docs/perfilamiento.md se conserva al volver a ejecutar. Ahi escribe el
Data Quality Analyst los hallazgos, y el script no los borra.

Uso:
    python -m src.perfilamiento
"""
# ---------------------------------------------------------------------------
# IMPORTS
# ---------------------------------------------------------------------------
import re                                   # re: expresiones regulares (reconocer formatos de fecha)
from datetime import datetime

import pandas as pd

from src import config
from src.utils import log

SALIDA = config.RAIZ / "docs" / "perfilamiento.md"
MARCA = "<!-- HALLAZGOS -->"                # desde aqui el archivo lo escribe una persona
LINAJE = ["_fuente", "_origen", "_extraido_en"]

# Columna que trae la fecha en cada archivo (por el inicio del nombre del archivo).
COLUMNA_FECHA = {
    "xm_": "Date",
    "ideam_": "fecha",
    "nasa_power": "fecha",
    "noaa_oni": "YR",            # NOAA solo trae el anio (y el trimestre movil en SEAS)
    "enerandes_": "col_0",       # Excel sin encabezado: la fecha es la primera columna
}

# Meses abreviados para fechas como "jun-24" del Excel de EnerAndes.
# OJO: la hoja 2024 mezcla espanol ("ago-24") con ingles ("aug-24", "jan-24", "dec-24").
MESES = {"ene": 1, "feb": 2, "mar": 3, "abr": 4, "may": 5, "jun": 6,
         "jul": 7, "ago": 8, "sep": 9, "oct": 10, "nov": 11, "dic": 12,
         "jan": 1, "apr": 4, "aug": 8, "dec": 12}        # las que cambian en ingles


# ---------------------------------------------------------------------------
# Funciones pequenas (se pueden probar con pytest)
# ---------------------------------------------------------------------------
def leer_fecha(texto):
    """Intenta leer una fecha escrita de muchas formas. Devuelve datetime o None.

    Formatos: 2024-01-31, 2024-01-31T00:00:00.000, 20240131, 2024-03, 03/2024,
              01/03/2026 (dia/mes/anio), jun-24, y un anio solo (2024).
    """
    if texto is None or pd.isna(texto):
        return None
    t = str(texto).strip().lower()
    formatos = [("%Y-%m-%dT%H:%M:%S.%f", r"\d{4}-\d{2}-\d{2}t"), ("%Y-%m-%d", r"\d{4}-\d{2}-\d{2}$"),
                ("%Y%m%d", r"\d{8}$"), ("%Y-%m", r"\d{4}-\d{2}$"), ("%m/%Y", r"\d{1,2}/\d{4}$"),
                ("%d/%m/%Y", r"\d{1,2}/\d{1,2}/\d{4}$"), ("%Y", r"\d{4}$")]
    for formato, patron in formatos:
        if re.match(patron, t):
            try:
                return datetime.strptime(t.upper() if "T" in formato else t, formato)
            except ValueError:
                return None
    m = re.match(r"([a-z]{3})-(\d{2})$", t)          # jun-24
    if m and m.group(1) in MESES:
        return datetime(2000 + int(m.group(2)), MESES[m.group(1)], 1)
    return None


def tipo_aparente(serie: pd.Series) -> str:
    """Que parece la columna, aunque en bronce todo venga como texto."""
    valores = serie.dropna().astype(str).str.strip()
    valores = valores[valores != ""]
    if valores.empty:
        return "vacía"
    numeros = pd.to_numeric(valores.str.replace(",", ".", regex=False), errors="coerce")
    if numeros.notna().mean() >= 0.95:
        return "número"
    if valores.head(500).map(leer_fecha).notna().mean() >= 0.95:
        return "fecha"
    return "texto"


def porcentaje_nulos(serie: pd.Series) -> float:
    """% de celdas nulas o vacias ("" o solo espacios)."""
    vacias = serie.isna() | (serie.astype(str).str.strip() == "")
    return round(100 * vacias.mean(), 2) if len(serie) else 0.0


def columna_fecha(nombre_archivo: str):
    for prefijo, columna in COLUMNA_FECHA.items():
        if nombre_archivo.startswith(prefijo):
            return columna
    return None


def rango_fechas(df: pd.DataFrame, columna) -> str:
    """'min a max' de la columna de fecha, contando cuantos valores no son fecha."""
    if columna is None or columna not in df.columns:
        return "no aplica"
    fechas = df[columna].map(leer_fecha)
    validas = fechas.dropna()
    if validas.empty:
        return "sin fechas reconocibles"
    texto = f"{validas.min():%Y-%m-%d} a {validas.max():%Y-%m-%d}"
    no_fecha = int(df[columna].notna().sum() - len(validas))
    if no_fecha:
        texto += f" ({no_fecha} valores no son fecha)"
    return texto


def perfilar(df: pd.DataFrame, nombre: str) -> dict:
    """Calcula el perfil de una tabla de bronce."""
    datos = df.drop(columns=[c for c in LINAJE if c in df.columns])   # el linaje no cuenta
    return {
        "nombre": nombre,
        "filas": len(df),
        "columnas": df.shape[1],
        "duplicadas": int(datos.duplicated().sum()),     # filas identicas (sin linaje)
        "rango": rango_fechas(df, columna_fecha(nombre)),
        "detalle": [
            {"columna": c, "tipo": str(df[c].dtype), "aparente": tipo_aparente(df[c]),
             "nulos": porcentaje_nulos(df[c]), "distintos": int(df[c].nunique(dropna=True))}
            for c in datos.columns
        ],
    }


# ---------------------------------------------------------------------------
# Escribir el Markdown
# ---------------------------------------------------------------------------
def a_markdown(perfiles: list) -> str:
    lineas = [
        "# Perfilamiento de la capa bronce",
        "",
        f"> Generado con `python -m src.perfilamiento` el {datetime.now():%Y-%m-%d %H:%M}. "
        "No edite esta parte a mano: se reemplaza cada vez que se ejecuta el script.",
        "",
        "- **Tipo en Parquet:** como quedó guardada la columna (en bronce casi todo es texto, `object`).",
        "- **Parece:** qué tipo de dato contiene en realidad (número, fecha o texto).",
        "- **% nulos:** celdas vacías o nulas. **Duplicadas:** filas idénticas sin contar las columnas de linaje.",
        "",
        "## Resumen",
        "",
        "| Archivo | Filas | Columnas | Filas duplicadas | Rango de fechas |",
        "|---|---:|---:|---:|---|",
    ]
    for p in perfiles:
        lineas.append(f"| `{p['nombre']}` | {p['filas']:,} | {p['columnas']} | {p['duplicadas']:,} | {p['rango']} |")
    for p in perfiles:
        lineas += ["", f"## `{p['nombre']}`", "",
                   f"**Filas:** {p['filas']:,} · **Columnas:** {p['columnas']} (incluye 3 de linaje) · "
                   f"**Filas duplicadas:** {p['duplicadas']:,} · **Rango de fechas:** {p['rango']}", "",
                   "| Columna | Tipo en Parquet | Parece | % nulos | Valores distintos |",
                   "|---|---|---|---:|---:|"]
        for d in p["detalle"]:
            lineas.append(f"| `{d['columna']}` | {d['tipo']} | {d['aparente']} | {d['nulos']} | {d['distintos']:,} |")
    return "\n".join(lineas) + "\n"


def main() -> None:
    log("Perfilamiento de la capa bronce")
    perfiles = []
    for archivo in sorted(config.DIR_BRONZE.glob("*.parquet")):
        log(f"   {archivo.name}")
        perfiles.append(perfilar(pd.read_parquet(archivo), archivo.stem))
    if not perfiles:
        log("   ! data/bronze/ esta vacia: ejecute primero python -m src.pipeline")
        return
    # Conservar los hallazgos escritos a mano (todo lo que va desde la MARCA)
    hallazgos = f"\n{MARCA}\n\n## Hallazgos de calidad\n\n_(Pendiente: mínimo 5 hallazgos con su evidencia numérica.)_\n"
    if SALIDA.exists():
        anterior = SALIDA.read_text(encoding="utf-8")
        if MARCA in anterior:
            hallazgos = "\n" + anterior[anterior.index(MARCA):]
    SALIDA.parent.mkdir(parents=True, exist_ok=True)
    SALIDA.write_text(a_markdown(perfiles) + hallazgos, encoding="utf-8")
    log(f"   + {SALIDA.relative_to(config.RAIZ)} escrito ({len(perfiles)} archivos)")


if __name__ == "__main__":
    main()
