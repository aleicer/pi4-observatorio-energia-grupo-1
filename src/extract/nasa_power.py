"""
Fuente 5 (propia) - NASA POWER: clima y radiacion solar diaria por satelite.
- API REST con GET; no requiere usuario ni clave
- Un pedido por punto cubre todo el rango de fechas (la API diaria lo permite)
- Respuesta: properties -> parameter -> {VARIABLE: {"AAAAMMDD": valor}}
- El valor -999 significa "sin dato". En bronce se deja TAL CUAL; se trata en plata.
"""
import pandas as pd
from src import config
from src.utils import guardar_bronce, http_json, log, ya_existe

NOMBRE = "nasa_power_diario" # nombre del archivo en bronce

def aplanar_nasa(datos: dict, punto: str, latitud: float, longitud: float) -> list:
    """Convierte la respuesta de NASA POWER en filas: una por punto, variable y dia."""
    filas = []
    parametros = datos.get("properties", {}).get("parameter", {})
    
    for variable, serie in parametros.items(): # ALLSKY_SFC_SW_DWN, T2M, PRECTOTCORR
        for fecha, valor in serie.items(): # "20240101": 4.87
            filas.append({
                "punto": punto, 
                "latitud": latitud, 
                "longitud": longitud,
                "variable": variable, 
                "fecha": fecha, 
                "valor": valor
            })
            
    return filas

def extraer(forzar: bool = False) -> None:
    """Descarga los datos diarios de cada punto y los guarda en bronce."""
    log("NASA POWER - clima y radiacion solar (fuente propia)")
    
    if ya_existe(NOMBRE, forzar):
        return
        
    filas = []
    for punto, latitud, longitud in config.NASA_POWER_PUNTOS:
        params = {
            "parameters": config.NASA_POWER_PARAMETROS,
            "community": "RE", # RE = energias renovables
            "latitude": latitud,
            "longitude": longitud,
            "start": config.FECHA_INICIO.strftime("%Y%m%d"), # la API pide AAAAMMDD
            "end": config.FECHA_FIN.strftime("%Y%m%d"),
            "format": "JSON",
        }
        
        datos = http_json("GET", config.NASA_POWER_URL, params=params)
        nuevas = aplanar_nasa(datos, punto, latitud, longitud)
        filas.extend(nuevas)
        log(f" {punto}: {len(nuevas)} filas")
        
    guardar_bronce(pd.DataFrame(filas), NOMBRE, fuente="NASA POWER", origen=config.NASA_POWER_URL)

if __name__ == "__main__":
    import sys
    extraer(forzar="--forzar" in sys.argv)