-- HECHOS: el clima medido por las estaciones del IDEAM en Antioquia.
-- Grano: una fecha y una estacion.
-- Junta lluvia y temperatura: una estacion puede medir solo una de las dos (full outer join).

select
    cast(strftime(coalesce(p.fecha, t.fecha), '%Y%m%d') as integer)  as fecha_id,
    coalesce(p.estacion_id, t.estacion_id)                           as estacion_id,
    -- Medidas
    p.precipitacion_mm,
    t.temp_media_c,
    t.temp_min_c,
    t.temp_max_c
from {{ ref('stg_precipitacion') }} as p
full outer join {{ ref('stg_temperatura') }} as t
    on p.estacion_id = t.estacion_id and p.fecha = t.fecha
