-- Dimension ESTACION: una estacion meteorologica del IDEAM en Antioquia.
-- Grano: una estacion. Llave: estacion_id (codigo de 10 digitos del IDEAM).
-- municipio_id (DIVIPOLA) solo esta lleno en los municipios con ventas de EnerAndes.

select
    estacion_id,
    nombre,
    municipio,
    divipola            as municipio_id,
    zona_hidrografica,
    latitud,
    longitud
from {{ ref('stg_estaciones') }}
