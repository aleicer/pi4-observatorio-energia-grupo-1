-- HECHOS: clima y radiacion solar por satelite (NASA POWER, fuente propia).
-- Grano: una fecha y un punto (Medellin, Embalse El Penol-Guatape, Hidroituango, La Guajira).

select
    cast(strftime(fecha, '%Y%m%d') as integer)  as fecha_id,
    punto,
    latitud,
    longitud,
    -- Medidas
    radiacion_kwh_m2,
    temperatura_c,
    precipitacion_mm
from {{ ref('stg_nasa') }}
