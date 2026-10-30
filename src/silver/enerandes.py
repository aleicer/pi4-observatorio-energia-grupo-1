"""
Capa PLATA: limpia las 4 hojas del Excel de ventas de EnerAndes (2023 a 2026)
y las une en UNA sola tabla.

Lee data/bronze/enerandes_ventas_2023.parquet ... _2026.parquet (tal cual llegaron),
aplica las reglas de limpieza una por una y MIDE cada problema antes y despues.
Luego valida el resultado con pandera (src/quality/esquemas.py) y guarda:
  - data/silver/enerandes_ventas.parquet             las filas limpias de los 4 anios
  - data/silver/enerandes_ventas_cuarentena.parquet  las filas que no se pueden usar, con su motivo

Problemas que resuelve (cada hoja trae los suyos):
  - encabezados distintos en cada hoja y titulos/notas encima del encabezado (2025, 2026)
  - filas de TOTAL al final de cada hoja
  - fechas en 4 formatos: 2024-03, mar-24 (y aug-24 en ingles), 03/2024 y 01/03/2026
    (esta ultima es dia/mes/anio: es MARZO, no el 3 de enero)
  - energia en kWh y en MWh en la hoja 2024 (columna UNIDAD)
  - municipios, segmentos y tipos de compra escritos de varias formas
  - duplicados, celdas vacias y valores negativos

En bronce no se modifica nada: aqui se trabaja sobre una copia.

Uso:
    python -m src.silver.enerandes
"""
# ---------------------------------------------------------------------------
# IMPORTS
# ---------------------------------------------------------------------------
import re               # re: expresiones regulares (reconocer los formatos de fecha)
import unicodedata      # unicodedata: separa una letra de su tilde (para quitar tildes)

import pandas as pd     # pandas: tablas

from src import config                                 # rutas de las carpetas
from src.quality.esquemas import ESQUEMA_VENTAS        # las reglas que debe cumplir la tabla limpia
from src.silver.comun import LINAJE, Medidor, guardar_plata
from src.utils import log                              # mensajes con hora

HOJAS = ["2023", "2024", "2025", "2026"]               # una hoja del Excel por anio

# Encabezado de cada hoja (escrito sin tildes y en minuscula) -> nombre estandar de plata.
# Cada hoja nombra distinto la misma columna: "Fecha", "PERIODO", "mes", "Fecha corte"...
ENCABEZADOS = {
    # hoja 2023          hoja 2024                 hoja 2025                hoja 2026
    "fecha": "periodo", "periodo": "periodo", "mes": "periodo", "fecha corte": "periodo",
    "municipio": "municipio", "ciudad": "municipio",
    "segmento": "segmento", "segmento cliente": "segmento", "tipo cliente": "segmento",
    "tipo_compra": "tipo_compra", "modalidad": "tipo_compra", "tipo compra": "tipo_compra",
    "compra": "tipo_compra",
    "energia_kwh": "energia", "energia": "energia", "consumo (kwh)": "energia", "kwh": "energia",
    "unidad": "unidad",                                 # solo en 2024: kWh o MWh
    "valor_cop": "valor_cop", "valor ($)": "valor_cop", "facturado": "valor_cop",
    "total facturado cop": "valor_cop",
    "clientes": "clientes", "num clientes": "clientes", "usuarios": "clientes",
    "clientes activos": "clientes",
}

# Meses abreviados para fechas como "mar-24". La hoja 2024 mezcla espanol con ingles
# (jan, apr, aug, dec), asi que se aceptan los dos.
MESES = {"ene": 1, "jan": 1, "feb": 2, "mar": 3, "abr": 4, "apr": 4, "may": 5, "jun": 6,
         "jul": 7, "ago": 8, "aug": 8, "sep": 9, "oct": 10, "nov": 11, "dic": 12, "dec": 12}

# Municipio (escrito sin tildes y en minuscula) -> (codigo DIVIPOLA, nombre oficial)
MUNICIPIOS = {
    "medellin": ("05001", "Medellín"),
    "santa fe de antioquia": ("05042", "Santa Fe de Antioquia"),
    "apartado": ("05045", "Apartadó"),
    "bello": ("05088", "Bello"),
    "caldas": ("05129", "Caldas"),
    "caucasia": ("05154", "Caucasia"),
    "copacabana": ("05212", "Copacabana"),
    "envigado": ("05266", "Envigado"),
    "girardota": ("05308", "Girardota"),
    "itagui": ("05360", "Itagüí"),
    "la estrella": ("05380", "La Estrella"),
    "marinilla": ("05440", "Marinilla"),
    "rionegro": ("05615", "Rionegro"),
    "sabaneta": ("05631", "Sabaneta"),
    "turbo": ("05837", "Turbo"),
}
# Otras formas de escribir el mismo municipio -> la forma de la lista de arriba
ALIAS_MUNICIPIO = {
    "rio negro": "rionegro",
    "rionegro (ant)": "rionegro",
    "medellin d.e.": "medellin",
    "sta fe de antioquia": "santa fe de antioquia",
    "santafe de antioquia": "santa fe de antioquia",
}
# Formas de escribir el segmento y el tipo de compra -> valor estandar
SEGMENTOS = {"residencial": "Residencial", "resid.": "Residencial",
             "comercial": "Comercial", "industrial": "Industrial", "ind": "Industrial"}
TIPOS_COMPRA = {"bolsa": "Bolsa", "contrato": "Contrato", "contratos": "Contrato"}

# Columnas de la capa plata, en orden
COLUMNAS_PLATA = ["periodo", "divipola", "municipio", "segmento", "tipo_compra",
                  "energia_kwh", "valor_cop", "clientes"]
LLAVE = ["periodo", "divipola", "segmento", "tipo_compra"]     # una venta = una llave


# ---------------------------------------------------------------------------
# FUNCIONES DE APOYO (cada una es una regla pequena, y se prueba con pytest)
# ---------------------------------------------------------------------------
def sin_tildes(texto: str) -> str:
    """'Itagüí' -> 'itagui': minuscula, sin espacios a los lados y sin tildes."""
    letras = unicodedata.normalize("NFD", str(texto).strip().lower())
    return "".join(c for c in letras if unicodedata.category(c) != "Mn")


def clave_municipio(texto) -> str | None:
    """Convierte cualquier forma de escribir el municipio en la clave de MUNICIPIOS."""
    if pd.isna(texto):
        return None
    clave = sin_tildes(texto)
    return ALIAS_MUNICIPIO.get(clave, clave)


def leer_periodo(texto) -> str | None:
    """Lee una fecha escrita en cualquiera de los 4 formatos y la deja como 'AAAA-MM'.

        '2024-03'    -> '2024-03'   (ya viene bien)
        'mar-24'     -> '2024-03'   (mes abreviado, en espanol o en ingles: 'aug-24')
        '03/2024'    -> '2024-03'   (mes/anio)
        '01/03/2026' -> '2026-03'   (dia/mes/anio: MARZO, no el 3 de enero)
        'TOTAL'      -> None        (no es una fecha)
    """
    if pd.isna(texto):
        return None
    t = sin_tildes(texto)
    if m := re.fullmatch(r"(\d{4})-(\d{1,2})", t):              # 2024-03
        anio, mes = int(m[1]), int(m[2])
    elif m := re.fullmatch(r"([a-z]{3})-(\d{2})", t):            # mar-24
        if m[1] not in MESES:
            return None
        anio, mes = 2000 + int(m[2]), MESES[m[1]]
    elif m := re.fullmatch(r"(\d{1,2})/(\d{4})", t):             # 03/2024
        anio, mes = int(m[2]), int(m[1])
    elif m := re.fullmatch(r"(\d{1,2})/(\d{1,2})/(\d{4})", t):   # 01/03/2026 (dia/mes/anio)
        anio, mes = int(m[3]), int(m[2])
    else:
        return None
    if not 1 <= mes <= 12:
        return None
    return f"{anio}-{mes:02d}"                                   # :02d -> 3 queda como '03'


def formato_fecha(texto) -> str:
    """Nombre del formato en que vino la fecha (para medir cuantos formatos habia)."""
    t = sin_tildes(texto)
    if re.fullmatch(r"\d{4}-\d{1,2}", t):
        return "AAAA-MM"
    if re.fullmatch(r"[a-z]{3}-\d{2}", t):
        return "mmm-AA"
    if re.fullmatch(r"\d{1,2}/\d{4}", t):
        return "MM/AAAA"
    if re.fullmatch(r"\d{1,2}/\d{1,2}/\d{4}", t):
        return "DD/MM/AAAA"
    return "otro"


def a_kwh(valor: float, unidad) -> float:
    """Pasa la energia a kWh: 1 MWh = 1.000 kWh. Si la unidad es kWh (o no hay), no cambia."""
    if pd.notna(unidad) and sin_tildes(unidad) == "mwh":
        return valor * 1000
    return valor


def leer_hoja(bronce: pd.DataFrame, hoja: str) -> tuple[pd.DataFrame, int, tuple]:
    """Busca la fila del encabezado, quita lo que hay encima y estandariza los nombres.

    Devuelve (tabla con columnas estandar, filas de titulo/nota que habia encima,
    el encabezado original de la hoja).
    """
    df = bronce.drop(columns=LINAJE, errors="ignore").reset_index(drop=True)
    # El encabezado es la primera fila donde casi todas las celdas son nombres conocidos
    for i in range(len(df)):
        celdas = [sin_tildes(v) for v in df.iloc[i] if pd.notna(v)]
        if sum(c in ENCABEZADOS for c in celdas) >= 5:
            break
    else:
        raise ValueError(f"Hoja {hoja}: no se encontro la fila del encabezado")
    nombres = [ENCABEZADOS.get(sin_tildes(v), f"extra_{n}") for n, v in enumerate(df.iloc[i])]
    datos = df.iloc[i + 1:].copy()                 # las filas que hay DEBAJO del encabezado
    datos.columns = nombres
    if "unidad" not in datos.columns:              # solo la hoja 2024 trae la unidad
        datos["unidad"] = "kWh"
    datos["hoja"] = hoja
    # Filas de titulo o notas = las que estaban ENCIMA del encabezado y no estaban vacias
    titulos = int(df.iloc[:i].notna().any(axis=1).sum())
    encabezado = tuple(str(v) for v in df.iloc[i] if pd.notna(v))
    return datos, titulos, encabezado


# ---------------------------------------------------------------------------
# LIMPIEZA: las reglas, en orden
# ---------------------------------------------------------------------------
def limpiar(hojas) -> tuple[pd.DataFrame, pd.DataFrame, list[dict]]:
    """Limpia las hojas y las une. Devuelve (limpias, cuarentena, metricas).

    hojas: {"2023": tabla de bronce, "2024": ...}. Tambien acepta UNA tabla sola
    (se toma como la hoja 2023, como en la clase y en tests/test_limpieza.py).
    """
    if isinstance(hojas, pd.DataFrame):
        hojas = {"2023": hojas}
    m = Medidor()
    cuarentenas = []

    def apartar(df, malas, motivo):
        """Pasa las filas 'malas' a cuarentena con su motivo y devuelve las buenas."""
        cuarentenas.append(df[malas].assign(motivo_cuarentena=motivo))
        return df[~malas].copy()

    # Regla 1-2. Encabezados distintos y titulos encima: se lee cada hoja con su encabezado
    partes, titulos, encabezados = [], 0, set()
    for hoja, bronce in hojas.items():
        datos, n_titulos, encabezado = leer_hoja(bronce, hoja)
        partes.append(datos)
        titulos += n_titulos
        encabezados.add(encabezado)
    m.medir("Encabezados distintos en cada hoja", "Traducir cada encabezado a 8 nombres estándar",
            len(encabezados), 1)
    m.medir("Títulos y notas encima del encabezado", "Buscar la fila del encabezado y quitar lo de arriba",
            titulos, 0)
    # Se unen las hojas en una sola tabla (las columnas ya tienen los mismos nombres)
    df = pd.concat(partes, ignore_index=True)
    df = df[[c for c in df.columns if not c.startswith("extra_")]]

    # Regla 3. Filas vacias y filas TOTAL: no son ventas
    vacias = df.drop(columns=["hoja", "unidad"]).isna().all(axis=1)
    df = df[~vacias]
    es_total = df["periodo"].astype(str).str.strip().str.upper() == "TOTAL"
    m.medir("Filas de totales", "Eliminarlas (no son ventas)", int(es_total.sum()), 0)
    df = df[~es_total].copy()

    # Regla 4. Filas repetidas exactamente iguales (dentro de cada hoja)
    antes = int(df.duplicated().sum())
    df = df.drop_duplicates()
    m.medir("Filas duplicadas exactas", "Dejar una sola copia", antes, int(df.duplicated().sum()))

    # Regla 5. Fechas en 4 formatos -> AAAA-MM
    formatos = df["periodo"].map(formato_fecha)
    no_iso = int((formatos != "AAAA-MM").sum())
    df["periodo"] = df["periodo"].map(leer_periodo)
    m.medir("Fechas en 4 formatos distintos (2024-03, mar-24, 03/2024, 01/03/2026)",
            "Leer cada formato y dejar AAAA-MM", int(formatos.nunique()), int(df["periodo"].map(formato_fecha).nunique()))
    m.medir("Fechas que no estaban en formato AAAA-MM", "Convertirlas a AAAA-MM", no_iso, 0)
    m.medir("Fechas día/mes/año de la hoja 2026 (01/03/2026)", "Tomar el MES del segundo número (marzo)",
            int((formatos == "DD/MM/AAAA").sum()), 0)
    df = apartar(df, df["periodo"].isna(), "Fecha que no se pudo leer")

    # Regla 6. Los numeros llegaron como texto -> numero
    for col in ["energia", "valor_cop", "clientes"]:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    # Regla 7. Energia en MWh (hoja 2024) -> kWh
    en_mwh = df["unidad"].map(lambda u: pd.notna(u) and sin_tildes(u) == "mwh")
    df["energia_kwh"] = [a_kwh(v, u) for v, u in zip(df["energia"], df["unidad"])]
    m.medir("Energía en MWh mezclada con kWh (hoja 2024)", "Multiplicar por 1.000 y dejar todo en kWh",
            int(en_mwh.sum()), 0)

    # Regla 8. Segmento escrito de varias formas o vacio
    antes = df["segmento"].nunique()
    df["segmento"] = df["segmento"].map(lambda s: SEGMENTOS.get(sin_tildes(s)) if pd.notna(s) else None)
    vacios = int(df["segmento"].isna().sum())
    df["segmento"] = df["segmento"].fillna("No informado")
    m.medir("Segmento escrito de varias formas", "Unificar a Residencial, Comercial e Industrial",
            antes, df["segmento"].nunique() - (1 if vacios else 0))
    m.medir("Segmento vacío", "Marcarlo como 'No informado'", vacios, 0)

    # Regla 9. Tipo de compra escrito de varias formas
    antes = df["tipo_compra"].nunique()
    df["tipo_compra"] = df["tipo_compra"].map(lambda t: TIPOS_COMPRA.get(sin_tildes(t)) if pd.notna(t) else None)
    m.medir("Tipo de compra escrito de varias formas", "Unificar a Bolsa y Contrato",
            antes, df["tipo_compra"].nunique())
    df = apartar(df, df["tipo_compra"].isna(), "Tipo de compra vacío o desconocido")

    # Regla 10. Municipio escrito de varias formas -> codigo DIVIPOLA y nombre oficial
    antes = df["municipio"].nunique()
    claves = df["municipio"].map(clave_municipio)
    df = apartar(df, ~claves.isin(MUNICIPIOS), "Municipio vacío o desconocido")
    claves = df["municipio"].map(clave_municipio)
    df["divipola"] = claves.map(lambda c: MUNICIPIOS[c][0])
    df["municipio"] = claves.map(lambda c: MUNICIPIOS[c][1])
    m.medir("Municipio escrito de varias formas", "Unificar con el código DIVIPOLA",
            antes, df["municipio"].nunique())

    # Regla 11. La misma venta escrita distinto ('Bello' y 'Bello '): repetida despues de unificar
    columnas = COLUMNAS_PLATA
    antes = int(df.duplicated(columnas).sum())
    df = df.drop_duplicates(columnas)
    m.medir("Ventas repetidas que solo cambiaban en la escritura", "Dejar una sola copia después de unificar",
            antes, int(df.duplicated(columnas).sum()))

    # Regla 12. Energia vacia: no se puede adivinar -> cuarentena
    vacia = df["energia_kwh"].isna()
    m.medir("Energía vacía", "Pasar la fila a cuarentena", int(vacia.sum()), 0)
    df = apartar(df, vacia, "Energía vacía")

    # Regla 13. Energia negativa: imposible -> cuarentena
    negativa = df["energia_kwh"] < 0
    m.medir("Energía negativa", "Pasar la fila a cuarentena", int(negativa.sum()), 0)
    df = apartar(df, negativa, "Energía negativa")

    # Regla 14. Clientes vacios o negativos -> cuarentena
    malos = df["clientes"].isna() | (df["clientes"] < 0)
    m.medir("Clientes vacíos o negativos", "Pasar la fila a cuarentena", int(malos.sum()), 0)
    df = apartar(df, malos, "Clientes vacíos o negativos")
    df["clientes"] = df["clientes"].astype(int)

    # Regla 15. Valor facturado negativo: imposible -> se deja vacio
    negativo = df["valor_cop"] < 0
    m.medir("Valor facturado negativo", "Dejarlo vacío (no se inventa un valor)", int(negativo.sum()), 0)
    df.loc[negativo, "valor_cop"] = None

    # Regla 16. Valor facturado vacio: se deja vacio y se documenta
    vacios = int(df["valor_cop"].isna().sum())
    m.medir("Valor facturado vacío", "Dejarlo vacío y documentarlo", vacios, vacios)

    # Regla 17. Dos filas con la misma llave y valores distintos: no se sabe cual es la buena
    conflicto = df.duplicated(LLAVE, keep=False)
    m.medir("Misma venta (mes, municipio, segmento y tipo) con valores distintos",
            "Pasar todas sus copias a cuarentena", int(conflicto.sum()), 0)
    df = apartar(df, conflicto, "Llave repetida con valores distintos")

    limpias = df[COLUMNAS_PLATA].sort_values(LLAVE).reset_index(drop=True)
    limpias["energia_kwh"] = limpias["energia_kwh"].astype(float)
    limpias["valor_cop"] = limpias["valor_cop"].astype(float)
    cuarentena = pd.concat(cuarentenas, ignore_index=True) if cuarentenas else pd.DataFrame()
    if len(cuarentena):
        cuarentena = cuarentena.rename(columns={"energia": "energia_original"})
    return limpias, cuarentena, m.metricas


# ---------------------------------------------------------------------------
# PROGRAMA PRINCIPAL
# ---------------------------------------------------------------------------
def main() -> None:
    # Lee las 4 hojas de bronce: {"2023": tabla, "2024": tabla, ...}
    hojas = {h: pd.read_parquet(config.DIR_BRONZE / f"enerandes_ventas_{h}.parquet") for h in HOJAS}
    filas_bronce = sum(len(t) for t in hojas.values())
    log(f"   Bronce: {filas_bronce:,} filas en {len(hojas)} hojas")
    limpias, cuarentena, metricas = limpiar(hojas)
    # guardar_plata (src/silver/comun.py) valida con pandera y, si todo esta bien,
    # guarda la tabla limpia, la cuarentena y las metricas para el reporte de calidad
    guardar_plata(limpias, "enerandes_ventas", ESQUEMA_VENTAS, "EnerAndes", metricas,
                  filas_bronce, cuarentena)


if __name__ == "__main__":
    main()
