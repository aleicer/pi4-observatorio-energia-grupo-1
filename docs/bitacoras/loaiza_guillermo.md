# Bitácora – Guillermo León Loaiza## Semana 2 (19 – 25 de octubre de 2026)
Rol esta semana: BI Analyst
Qué hice: Desarrollé el extractor de la fuente propia NASA POWER (src/extract/nasa_power.py),
actualicé la configuración (src/config.py), lo integré al pipeline y redacté su sección en el README.
https://github.com/aleicer/pi4-observatorio-energia-grupo-1/commit/016d5cf6fca0adfba44f7180c75ae0ca92142b9c
https://github.com/aleicer/pi4-observatorio-energia-grupo-1/commit/3a81a1c6a7e52c7e4bc84eb53712f6a8798c4d16
https://github.com/aleicer/pi4-observatorio-energia-grupo-1/commit/5f20ae5a212da4cce1795a17d31d7b0e3253eec1

Qué aprendí: Comprendí el concepto de idempotencia al usar la función ya_existe, para que el pipeline omita 
descargas que ya están en la capa bronce.
Aprendí a consumir una API REST, aplanar estructuras JSON anidadas (properties -> parameter) para convertirlas
en un DataFrame, y a guardar la data cruda en Parquet manteniendo valores como el -999 (sin dato) tal cual llegan
para tratarlos después en la etapa plata.

Bloqueos y cómo los resolví: Al principio la estructura de respuesta de la API no era evidente. 
Lo resolví probando el endpoint manualmente en el navegador para entender la forma del JSON antes de programar 
la función aplanar_nasa. También, para evitar conflictos de código en config.py, 
coordiné con el equipo esperando a que Aleicer hiciera el merge de XM e IDEAM, 
e hice un git pull de la rama main antes de crear la mía.   

Horas dedicadas: 5 horas